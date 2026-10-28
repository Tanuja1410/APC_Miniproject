class Person:
    def __init__(self, name, mobile=""):
        self.name = name.strip()
        self._mobile = mobile.strip()

    @property
    def mobile(self):
        return self._mobile

    def display(self):
        return f"{self.name} | {self.mobile}" if self.mobile else self.name


class Member(Person):
    def __init__(self, member_id, name, mobile=""):
        super().__init__(name, mobile)
        self.member_id = int(member_id)
        self.paid = 0.0
        self.balance = 0.0

    def add_payment(self, amount):
        self.paid += float(amount)


class AdminMember(Member):
    def __init__(self, member_id, name, mobile=""):
        super().__init__(member_id, name, mobile)
        self.role = "Admin"
