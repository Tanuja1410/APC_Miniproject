import logging
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.db import DatabaseError, transaction
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from .forms import ExpenseForm, MemberForm, SignupForm, TripForm
from .models import Trip

logger = logging.getLogger(__name__)


def _dashboard_url(trip_id=None):
    url = reverse("dashboard")
    if trip_id is not None:
        return f"{url}?trip={trip_id}"
    return url


def _form_error_text(form):
    errors = []
    for field, field_errors in form.errors.items():
        label = "Form" if field == "__all__" else field.replace("_", " ").title()
        errors.extend(f"{label}: {error}" for error in field_errors)
    return "; ".join(errors)


def _cents(amount):
    value = Decimal(str(amount)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    return int(value * 100)


def _build_summary(trip):
    members = list(trip.members.order_by("id"))
    expenses = list(
        trip.expenses.select_related("paid_by")
        .prefetch_related("participants")
        .order_by("created_at", "id")
    )
    paid = {member.id: 0 for member in members}
    shares = {member.id: 0 for member in members}
    expense_rows = []
    total_cents = 0

    for expense in expenses:
        amount_cents = _cents(expense.amount)
        total_cents += amount_cents
        if expense.paid_by_id in paid:
            paid[expense.paid_by_id] += amount_cents

        participants = list(expense.participants.all()) or members
        participant_shares = []
        if participants:
            base_share, remainder = divmod(amount_cents, len(participants))
            for index, member in enumerate(participants):
                share_cents = base_share + (remainder if index == len(participants) - 1 else 0)
                shares[member.id] = shares.get(member.id, 0) + share_cents
                participant_shares.append({
                    "name": member.name,
                    "amount": share_cents / 100,
                })
        expense_rows.append({
            "expense": expense,
            "shares": participant_shares,
        })

    member_rows = []
    for member in members:
        balance_cents = paid[member.id] - shares[member.id]
        member_rows.append({
            "member": member,
            "paid": paid[member.id] / 100,
            "share": shares[member.id] / 100,
            "balance": balance_cents / 100,
            "balance_amount": abs(balance_cents) / 100,
        })

    debtors = [[row["member"].name, -_cents(row["balance"])] for row in member_rows if row["balance"] < -0.009]
    creditors = [[row["member"].name, _cents(row["balance"])] for row in member_rows if row["balance"] > 0.009]
    settlements = []
    debtor_index = 0
    creditor_index = 0
    while debtor_index < len(debtors) and creditor_index < len(creditors):
        debtor, debt = debtors[debtor_index]
        creditor, credit = creditors[creditor_index]
        amount = min(debt, credit)
        settlements.append({
            "from": debtor,
            "to": creditor,
            "amount": amount / 100,
        })
        debtors[debtor_index][1] -= amount
        creditors[creditor_index][1] -= amount
        if debtors[debtor_index][1] == 0:
            debtor_index += 1
        if creditors[creditor_index][1] == 0:
            creditor_index += 1

    budget_cents = _cents(trip.budget)
    return {
        "members": members,
        "expenses": expense_rows,
        "member_rows": member_rows,
        "settlements": settlements,
        "total": total_cents / 100,
        "remaining": (budget_cents - total_cents) / 100 if budget_cents else None,
    }


def _report_text(trip, summary):
    lines = [
        f"TripSplit Expense Report: {trip.name}",
        f"Budget: {trip.budget:.2f}",
        f"Total expenses: {summary['total']:.2f}",
        (
            f"Remaining budget: {summary['remaining']:.2f}"
            if summary["remaining"] is not None else "Remaining budget: No budget limit"
        ),
        "",
        "Expenses and individual shares:",
    ]
    for row in summary["expenses"]:
        expense = row["expense"]
        lines.append(f"- {expense.name}: {expense.amount:.2f} paid by {expense.paid_by.name}")
        for share in row["shares"]:
            lines.append(f"  {share['name']}: share {share['amount']:.2f}")

    lines.append("")
    lines.append("Member contributions and balances:")
    for row in summary["member_rows"]:
        lines.append(
            f"- {row['member'].name}: paid {row['paid']:.2f}, "
            f"share {row['share']:.2f}, balance {row['balance']:.2f}"
        )

    lines.append("")
    lines.append("Settlements:")
    if summary["settlements"]:
        for item in summary["settlements"]:
            lines.append(f"- {item['from']} pays {item['to']}: {item['amount']:.2f}")
    else:
        lines.append("- All settled.")
    return "\n".join(lines) + "\n"


def signup(request):
    if request.method == "POST":
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("dashboard")
    else:
        form = SignupForm()
    return render(request, "signup.html", {"form": form})


@login_required
def dashboard(request):
    try:
        trips = list(Trip.objects.order_by("id"))
        trip_id = request.GET.get("trip")
        if trip_id:
            try:
                trip_id = int(trip_id)
            except ValueError:
                raise Http404("Trip not found.") from None
            trip = get_object_or_404(Trip, pk=trip_id)
        else:
            trip = trips[0] if trips else None
        summary = _build_summary(trip) if trip else None
    except DatabaseError:
        logger.exception("Could not load the TripSplit dashboard")
        return HttpResponse(
            "Could not load saved trip data. Check the database and try refreshing again.",
            status=500,
        )

    if request.GET.get("refresh") == "1":
        messages.success(request, "Trip data refreshed.")
    return render(request, "dashboard.html", {
        "trips": trips,
        "trip": trip,
        "summary": summary,
    })


@login_required
def create_trip(request):
    form = TripForm(request.POST or None)
    if request.method == "POST":
        if form.is_valid():
            try:
                trip = form.save()
            except DatabaseError:
                logger.exception("Could not save a trip")
                return HttpResponse("Could not save the trip. Please try again.", status=500)
            messages.success(request, "Trip saved.")
            return redirect(_dashboard_url(trip.id))
        messages.error(request, _form_error_text(form))
    return render(request, "trip_form.html", {"form": form})


@login_required
def add_member(request, trip_id):
    trip = get_object_or_404(Trip, pk=trip_id)
    if request.method != "POST":
        return redirect(_dashboard_url(trip.id))
    form = MemberForm(request.POST, trip=trip)
    if not form.is_valid():
        messages.error(request, _form_error_text(form))
        return redirect(_dashboard_url(trip.id))
    try:
        with transaction.atomic():
            member = form.save(commit=False)
            member.trip = trip
            member.save()
    except DatabaseError:
        logger.exception("Could not save a trip member")
        return HttpResponse("Could not save the member. Please try again.", status=500)
    messages.success(request, f"{member.name} was added.")
    return redirect(_dashboard_url(trip.id))


@login_required
def add_expense(request, trip_id):
    trip = get_object_or_404(Trip, pk=trip_id)
    if request.method != "POST":
        return redirect(_dashboard_url(trip.id))
    form = ExpenseForm(request.POST, trip=trip)
    if not form.is_valid():
        messages.error(request, _form_error_text(form))
        return redirect(_dashboard_url(trip.id))
    try:
        with transaction.atomic():
            expense = form.save(commit=False)
            expense.trip = trip
            expense.amount = float(form.cleaned_data["amount"])
            expense.save()
            participants = form.cleaned_data["participants"] or trip.members.all()
            expense.participants.set(participants)
    except DatabaseError:
        logger.exception("Could not save a trip expense")
        return HttpResponse("Could not save the expense. Please try again.", status=500)
    messages.success(request, f"{expense.name} was saved.")
    return redirect(_dashboard_url(trip.id))


@login_required
def report(request, trip_id):
    trip = get_object_or_404(Trip, pk=trip_id)
    try:
        summary = _build_summary(trip)
    except DatabaseError:
        logger.exception("Could not load the expense report")
        return HttpResponse("Could not load the report data. Please try again.", status=500)

    if request.GET.get("download") == "1":
        text = _report_text(trip, summary)
        report_dir = Path(settings.BASE_DIR).parent / "reports"
        report_path = report_dir / f"trip_{trip.id}_report.txt"
        try:
            report_dir.mkdir(parents=True, exist_ok=True)
            report_path.write_text(text, encoding="utf-8")
        except OSError:
            logger.exception("Could not save the expense report")
            return render(request, "report.html", {
                "trip": trip,
                "summary": summary,
                "save_error": "The report could not be saved to the reports folder.",
            }, status=500)
        response = HttpResponse(text, content_type="text/plain; charset=utf-8")
        response["Content-Disposition"] = f'attachment; filename="{report_path.name}"'
        return response

    return render(request, "report.html", {"trip": trip, "summary": summary})
