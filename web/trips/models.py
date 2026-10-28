from django.db import models


class Trip(models.Model):
    name = models.CharField(max_length=100)
    budget = models.FloatField(default=0)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)

    def total_expense(self):
        return sum(e.amount for e in self.expenses.all())

    def __str__(self):
        return self.name


class Member(models.Model):
    trip = models.ForeignKey(Trip, related_name="members", on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    mobile = models.CharField(max_length=20, blank=True)

    def __str__(self):
        return self.name


class Expense(models.Model):
    trip = models.ForeignKey(Trip, related_name="expenses", on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    amount = models.FloatField()
    paid_by = models.ForeignKey(Member, related_name="payments", on_delete=models.CASCADE)
    participants = models.ManyToManyField(Member, related_name="shared_expenses", blank=True)
    category = models.CharField(max_length=50, default="Other")
    created_at = models.DateField(auto_now_add=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name
