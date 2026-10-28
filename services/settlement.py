def calculate_balances(trip):
    balances = {name: 0.0 for name in trip.members}
    for expense in trip.expenses:
        balances[expense.paid_by] += expense.amount
        for name, share in expense.shares.items():
            balances[name] -= float(share)
    for name, value in balances.items():
        trip.members[name].balance = round(value, 2)
    return {name: round(value, 2) for name, value in balances.items()}


def settle_expenses(trip):
    balances = calculate_balances(trip)
    creditors = [[name, amount] for name, amount in balances.items() if amount > 0.009]
    debtors = [[name, -amount] for name, amount in balances.items() if amount < -0.009]
    settlements = []

    def solve(i, j):
        if i >= len(debtors) or j >= len(creditors):
            return
        debtor, debt = debtors[i]
        creditor, credit = creditors[j]
        amount = round(min(debt, credit), 2)
        settlements.append({"from": debtor, "to": creditor, "amount": amount})
        debtors[i][1] = round(debt - amount, 2)
        creditors[j][1] = round(credit - amount, 2)
        next_i = i + 1 if debtors[i][1] <= 0.009 else i
        next_j = j + 1 if creditors[j][1] <= 0.009 else j
        solve(next_i, next_j)

    solve(0, 0)
    return settlements
