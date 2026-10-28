from abc import ABC, abstractmethod
from datetime import datetime


class Auditable:
    def audit(self):
        return f"{self.expense_id} | {self.name} | {self.amount:.2f}"


class Expense(ABC):
    def __init__(self, expense_id, name, amount, paid_by, category="Other", participants=None, shares=None, date=None, description=""):
        self.expense_id = expense_id
        self.name = name.strip()
        self.amount = float(amount)
        self.paid_by = paid_by
        self.category = category or "Other"
        self.participants = participants or []
        self.shares = shares or {}
        self.date = date or datetime.now().strftime("%Y-%m-%d")
        self.description = description.strip()

    @abstractmethod
    def calculate_shares(self):
        pass

    def to_dict(self):
        return {
            "expense_id": self.expense_id,
            "name": self.name,
            "amount": self.amount,
            "paid_by": self.paid_by,
            "category": self.category,
            "participants": self.participants,
            "shares": self.shares,
            "date": self.date,
            "description": self.description,
            "type": self.__class__.__name__
        }


class EqualExpense(Expense):
    def calculate_shares(self):
        if not self.participants:
            return {}
        share = round(self.amount / len(self.participants), 2)
        result = {name: share for name in self.participants}
        diff = round(self.amount - sum(result.values()), 2)
        result[self.participants[-1]] = round(result[self.participants[-1]] + diff, 2)
        self.shares = result
        return result


class PercentageExpense(Expense):
    def calculate_shares(self):
        result = {name: round(self.amount * float(percent) / 100, 2) for name, percent in self.shares.items()}
        diff = round(self.amount - sum(result.values()), 2)
        if result:
            last = next(reversed(result))
            result[last] = round(result[last] + diff, 2)
        self.shares = result
        return result


class CustomExpense(Expense):
    def calculate_shares(self):
        result = {name: round(float(value), 2) for name, value in self.shares.items()}
        diff = round(self.amount - sum(result.values()), 2)
        if result:
            last = next(reversed(result))
            result[last] = round(result[last] + diff, 2)
        self.shares = result
        return result


class AuditableExpense(EqualExpense, Auditable):
    pass
