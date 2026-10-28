from pathlib import Path
from tempfile import TemporaryDirectory

from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.urls import reverse

from .models import Expense, Member, Trip


class TripSplitWorkflowTests(TestCase):
    def setUp(self):
        user = get_user_model().objects.create_user(
            username="student",
            password="simple-password-123",
        )
        self.client.force_login(user)
        self.trip = Trip.objects.create(name="College trip", budget=500)
        self.alice = Member.objects.create(trip=self.trip, name="Alice")
        self.bob = Member.objects.create(trip=self.trip, name="Bob")

    def test_expense_saves_participants_balances_and_report(self):
        response = self.client.post(
            reverse("add_expense", args=[self.trip.id]),
            {
                "name": "Lunch",
                "amount": "100.00",
                "paid_by": str(self.alice.id),
                "participants": [str(self.alice.id), str(self.bob.id)],
                "category": "Food",
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(Expense.objects.count(), 1)
        expense = Expense.objects.get()
        self.assertEqual(set(expense.participants.all()), {self.alice, self.bob})

        dashboard = self.client.get(reverse("dashboard"), {"trip": self.trip.id})
        self.assertContains(dashboard, "Alice")
        self.assertContains(dashboard, "Bob")
        self.assertContains(dashboard, "50.00")
        self.assertContains(dashboard, "Bob pays Alice")

        report = self.client.get(reverse("report", args=[self.trip.id]))
        self.assertContains(report, "Alice: ₹50.00")
        self.assertContains(report, "Bob pays Alice")

    def test_refresh_reads_saved_data_without_adding_records(self):
        Expense.objects.create(
            trip=self.trip,
            name="Bus",
            amount=50,
            paid_by=self.alice,
        )

        response = self.client.get(
            reverse("dashboard"),
            {"trip": self.trip.id, "refresh": "1"},
        )

        self.assertContains(response, "Trip data refreshed.")
        self.assertContains(response, "Bus")
        self.assertEqual(Expense.objects.count(), 1)

    def test_optional_budget_is_shown_as_unlimited(self):
        self.trip.budget = 0
        self.trip.save()

        dashboard = self.client.get(reverse("dashboard"), {"trip": self.trip.id})
        report = self.client.get(reverse("report", args=[self.trip.id]))

        self.assertContains(dashboard, "No limit")
        self.assertContains(report, "No budget limit")

    def test_trip_and_member_forms_save_records(self):
        response = self.client.post(
            reverse("create_trip"),
            {"name": "Weekend away", "budget": "250.00"},
        )

        self.assertEqual(response.status_code, 302)
        trip = Trip.objects.get(name="Weekend away")
        self.assertEqual(trip.budget, 250)

        response = self.client.post(
            reverse("add_member", args=[trip.id]),
            {"name": "Casey", "mobile": ""},
        )

        self.assertEqual(response.status_code, 302)
        self.assertTrue(Member.objects.filter(trip=trip, name="Casey").exists())

    def test_expense_over_budget_is_rejected(self):
        response = self.client.post(
            reverse("add_expense", args=[self.trip.id]),
            {
                "name": "Too much",
                "amount": "501.00",
                "paid_by": str(self.alice.id),
                "participants": [str(self.alice.id)],
                "category": "Other",
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(Expense.objects.count(), 0)

    def test_report_download_is_saved_and_contains_current_data(self):
        Expense.objects.create(
            trip=self.trip,
            name="Taxi",
            amount=30,
            paid_by=self.alice,
        )

        with TemporaryDirectory() as folder:
            base_dir = Path(folder) / "web"
            base_dir.mkdir()
            with override_settings(BASE_DIR=base_dir):
                response = self.client.get(
                    reverse("report", args=[self.trip.id]),
                    {"download": "1"},
                )

            saved_report = Path(folder) / "reports" / f"trip_{self.trip.id}_report.txt"
            self.assertEqual(response.status_code, 200)
            self.assertIn("Taxi", response.content.decode())
            self.assertTrue(saved_report.exists())
            self.assertIn("30.00", saved_report.read_text(encoding="utf-8"))

    def test_signup_works_with_username_and_password(self):
        response = self.client.post(
            reverse("signup"),
            {
                "username": "newstudent",
                "password1": "simple-password-456",
                "password2": "simple-password-456",
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertTrue(get_user_model().objects.filter(username="newstudent").exists())

    def test_login_works_with_username_and_password(self):
        self.client.logout()
        response = self.client.post(
            reverse("login"),
            {
                "username": "student",
                "password": "simple-password-123",
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("dashboard"))

    def test_logout_uses_post(self):
        response = self.client.post(reverse("logout"))

        self.assertEqual(response.status_code, 302)
        response = self.client.get(reverse("dashboard"))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("login"), response.url)
