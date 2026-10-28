import json
import os
from models.expense import EqualExpense, PercentageExpense, CustomExpense
from models.member import Member
from models.trip import Trip


class BudgetExceededError(Exception):
    pass


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
REPORT_DIR = os.path.join(BASE_DIR, "reports")
JSON_FILE = os.path.join(DATA_DIR, "trip.json")
CSV_FILE = os.path.join(DATA_DIR, "expenses.csv")
TXT_FILE = os.path.join(DATA_DIR, "settlements.txt")


def ensure_dirs():
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(REPORT_DIR, exist_ok=True)


def save_trip(trip):
    ensure_dirs()
    if trip.budget > 0 and trip.total_expense() > trip.budget:
        raise BudgetExceededError("Trip budget exceeded")
    with open(JSON_FILE, "w", encoding="utf-8") as file:
        json.dump(trip.to_dict(), file, indent=2)
    export_expenses_csv(trip)


def export_expenses_csv(trip):
    import csv
    ensure_dirs()
    with open(CSV_FILE, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["ExpenseID", "Date", "Expense", "Amount", "PaidBy", "Category", "SplitType", "Participants", "Description"])
        for e in trip.expenses:
            writer.writerow([e.expense_id, e.date, e.name, e.amount, e.paid_by, e.category, e.__class__.__name__, ";".join(e.participants), e.description])


def save_settlements(settlements):
    ensure_dirs()
    with open(TXT_FILE, "w", encoding="utf-8") as file:
        file.write("TripSplit Settlement Report\n")
        file.write("=" * 30 + "\n")
        for item in settlements:
            file.write(f"{item['from']} -> {item['to']} : {item['amount']:.2f}\n")


def load_trip():
    ensure_dirs()
    if not os.path.exists(JSON_FILE):
        return None
    with open(JSON_FILE, "r", encoding="utf-8") as file:
        data = json.load(file)
    trip = Trip(data["name"], data.get("budget", 0), data.get("start_date", ""), data.get("end_date", ""))
    for m in data.get("members", []):
        member = Member(m["member_id"], m["name"], m.get("mobile", ""))
        member.paid = float(m.get("paid", 0))
        member.balance = float(m.get("balance", 0))
        trip.members[member.name] = member
    trip.next_member_id = data.get("next_member_id", len(trip.members) + 1)
    for e in data.get("expenses", []):
        cls = e.get("type", "EqualExpense")
        if cls == "EqualExpense":
            expense = EqualExpense(e["expense_id"], e["name"], e["amount"], e["paid_by"], e.get("category", "Other"), e.get("participants", []), e.get("shares", {}), e.get("date"), e.get("description", ""))
        elif cls == "PercentageExpense":
            expense = PercentageExpense(e["expense_id"], e["name"], e["amount"], e["paid_by"], e.get("category", "Other"), e.get("participants", []), e.get("shares", {}), e.get("date"), e.get("description", ""))
        else:
            expense = CustomExpense(e["expense_id"], e["name"], e["amount"], e["paid_by"], e.get("category", "Other"), e.get("participants", []), e.get("shares", {}), e.get("date"), e.get("description", ""))
        expense.shares = {k: float(v) for k, v in e.get("shares", {}).items()}
        trip.expenses.append(expense)
    trip.next_expense_id = data.get("next_expense_id", len(trip.expenses) + 1)
    return trip
