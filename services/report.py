from datetime import datetime
import os
from services.file_manager import REPORT_DIR


def generate_report(trip, settlements):
    os.makedirs(REPORT_DIR, exist_ok=True)
    path = os.path.join(REPORT_DIR, "trip_report.txt")
    lines = [
        f"TripSplit Report - {trip.name}",
        f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"Budget: {trip.budget:.2f}",
        f"Total Expense: {trip.total_expense():.2f}",
        (
            f"Remaining Budget: {trip.remaining_budget():.2f}"
            if trip.budget > 0 else "Remaining Budget: No budget limit"
        ),
        "",
        "Expenses and individual shares"
    ]
    for expense in trip.expenses:
        lines.append(f"{expense.name} | Amount: {expense.amount:.2f} | Paid by: {expense.paid_by}")
        for name, share in expense.shares.items():
            lines.append(f"  {name}: Share {float(share):.2f}")
    lines += [
        "",
        "Members"
    ]
    for m in trip.members.values():
        share = sum(float(e.shares.get(m.name, 0)) for e in trip.expenses)
        lines.append(f"{m.name} | Paid: {m.paid:.2f} | Share: {share:.2f} | Balance: {m.balance:.2f}")
    lines += ["", "Settlements"]
    if settlements:
        for s in settlements:
            lines.append(f"{s['from']} -> {s['to']} : {s['amount']:.2f}")
    else:
        lines.append("All settled.")
    with open(path, "w", encoding="utf-8") as file:
        file.write("\n".join(lines))
    return path
