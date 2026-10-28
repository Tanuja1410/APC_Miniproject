import os
import matplotlib.pyplot as plt
from services.file_manager import REPORT_DIR


def make_charts(trip):
    os.makedirs(REPORT_DIR, exist_ok=True)
    category_totals = {}
    for e in trip.expenses:
        category_totals[e.category] = category_totals.get(e.category, 0) + e.amount

    if not category_totals:
        return []

    paths = []
    names = list(category_totals)
    values = [category_totals[n] for n in names]

    plt.figure(figsize=(8, 5))
    plt.bar(names, values)
    plt.title("Expenses by Category")
    plt.xlabel("Category")
    plt.ylabel("Amount")
    plt.xticks(rotation=25)
    plt.tight_layout()
    bar_path = os.path.join(REPORT_DIR, "expenses_by_category.png")
    plt.savefig(bar_path, dpi=150)
    plt.close()
    paths.append(bar_path)

    plt.figure(figsize=(6, 6))
    plt.pie(values, labels=names, autopct="%1.1f%%")
    plt.title("Expense Distribution")
    pie_path = os.path.join(REPORT_DIR, "expense_distribution.png")
    plt.savefig(pie_path, dpi=150)
    plt.close()
    paths.append(pie_path)

    return paths
