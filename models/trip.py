from datetime import datetime
from models.member import Member
from models.expense import EqualExpense, PercentageExpense, CustomExpense


class Trip:
    def __init__(self, name, budget=0.0, start_date="", end_date=""):
        self.name = name.strip()
        self.budget = float(budget)
        self.start_date = start_date
        self.end_date = end_date
        self.members = {}
        self.expenses = []
        self.next_member_id = 1
        self.next_expense_id = 1

    def add_member(self, name, mobile=""):
        if any(m.name.lower() == name.strip().lower() for m in self.members.values()):
            raise ValueError("Member already exists")
        member = Member(self.next_member_id, name, mobile)
        self.members[member.name] = member
        self.next_member_id += 1
        return member

    def add_expense(self, name, amount, paid_by, category="Other", split_type="equal", participants=None, shares=None, date=None, description=""):
        amount = float(amount)
        if amount <= 0:
            raise ValueError("Amount must be greater than zero")
        if self.budget > 0 and self.total_expense() + amount > self.budget:
            raise ValueError("Trip budget exceeded")
        if paid_by not in self.members:
            raise KeyError("Payer not found")
        participants = participants or list(self.members.keys())
        if not set(participants).issubset(self.members.keys()):
            raise KeyError("Participant not found")
        if split_type == "equal":
            expense = EqualExpense(self.next_expense_id, name, amount, paid_by, category, participants, date=date, description=description)
        elif split_type == "percentage":
            expense = PercentageExpense(self.next_expense_id, name, amount, paid_by, category, shares=shares, date=date, description=description)
        else:
            expense = CustomExpense(self.next_expense_id, name, amount, paid_by, category, shares=shares, date=date, description=description)
        expense.calculate_shares()
        self.expenses.append(expense)
        self.members[paid_by].add_payment(amount)
        self.next_expense_id += 1
        return expense

    def total_expense(self):
        return round(sum(e.amount for e in self.expenses), 2)

    def remaining_budget(self):
        if self.budget <= 0:
            return 0.0
        return round(self.budget - self.total_expense(), 2)

    def to_dict(self):
        return {
            "name": self.name,
            "budget": self.budget,
            "start_date": self.start_date,
            "end_date": self.end_date,
            "next_member_id": self.next_member_id,
            "next_expense_id": self.next_expense_id,
            "members": [
                {"member_id": m.member_id, "name": m.name, "mobile": m.mobile, "paid": m.paid, "balance": m.balance}
                for m in self.members.values()
            ],
            "expenses": [e.to_dict() for e in self.expenses],
            "updated_at": datetime.now().isoformat(timespec="seconds")
        }
