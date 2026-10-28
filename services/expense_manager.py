from services.file_manager import save_trip, BudgetExceededError
from services.validation import valid_amount


def add_member(trip, name, mobile=""):
    return trip.add_member(name, mobile)


def add_expense(trip, name, amount, paid_by, category="Other", split_type="equal", participants=None, shares=None, date=None, description=""):
    if not valid_amount(amount):
        raise ValueError("Invalid amount")
    expense = trip.add_expense(name, amount, paid_by, category, split_type, participants, shares, date, description)
    try:
        save_trip(trip)
    except BudgetExceededError:
        trip.expenses.pop()
        trip.members[paid_by].paid -= float(amount)
        raise
    return expense
