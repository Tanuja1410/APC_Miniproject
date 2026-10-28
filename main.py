from datetime import datetime

from models.trip import Trip
from services.file_manager import load_trip, save_trip, BudgetExceededError, ensure_dirs
from services.settlement import calculate_balances, settle_expenses
from services.report import generate_report
from services.validation import valid_mobile
from analytics.numpy_analysis import analyze_expenses
from analytics.pandas_analysis import summary as pandas_summary
from analytics.charts import make_charts
from analytics.prediction import predict_next_expense
from nlp.text_processing import process_text, search_relevant_expenses


def input_int(prompt):
    while True:
        try:
            return int(input(prompt))
        except ValueError:
            print("Enter a valid number.")


def input_float(prompt):
    while True:
        try:
            value = float(input(prompt))
            if value <= 0:
                raise ValueError
            return value
        except ValueError:
            print("Enter a positive amount.")


def create_trip():
    name = input("Trip name: ").strip()
    budget_text = input("Budget: ").strip()
    budget = float(budget_text or 0)
    start = input("Start date (YYYY-MM-DD): ").strip()
    end = input("End date (YYYY-MM-DD): ").strip()
    return Trip(name, budget, start, end)


def add_member_ui(trip):
    name = input("Member name: ").strip()
    mobile = input("Mobile: ").strip()
    if mobile and not valid_mobile(mobile):
        print("Invalid mobile.")
        return
    try:
        trip.add_member(name, mobile)
        save_trip(trip)
        print("Member added.")
    except Exception as e:
        print("Error:", e)


def choose_participants(trip):
    names = list(trip.members)
    if not names:
        return []
    print("Members:")
    for i, name in enumerate(names, 1):
        print(f"{i}. {name}")
    raw = input("Participant numbers separated by comma, blank for everyone: ").strip()
    if not raw:
        return names
    selected = []
    try:
        for part in raw.split(","):
            index = int(part.strip()) - 1
            if 0 <= index < len(names) and names[index] not in selected:
                selected.append(names[index])
        return selected
    except ValueError:
        print("Invalid selection.")
        return []


def add_expense_ui(trip):
    if not trip.members:
        print("Add members first.")
        return
    name = input("Expense name: ").strip()
    amount = input_float("Amount: ")
    print("Categories: Food, Stay, Travel, Tickets, Shopping, Entertainment, Other")
    category = input("Category: ").strip() or "Other"
    names = list(trip.members)
    for i, member in enumerate(names, 1):
        print(f"{i}. {member}")
    payer_index = input_int("Paid by number: ") - 1
    if not 0 <= payer_index < len(names):
        print("Invalid payer.")
        return
    payer = names[payer_index]
    print("1. Equal split\n2. Percentage split\n3. Custom amount split")
    mode = input_int("Split type: ")
    date = input("Date (blank for today): ").strip() or datetime.now().strftime("%Y-%m-%d")
    description = input("Description: ").strip()
    participants = choose_participants(trip)
    if not participants:
        print("No participants selected.")
        return
    shares = None
    if mode == 2:
        shares = {}
        remaining = 100.0
        for name in participants[:-1]:
            percent = float(input(f"% for {name} (remaining {remaining:.2f}): "))
            shares[name] = percent
            remaining -= percent
        shares[participants[-1]] = round(remaining, 2)
        if abs(sum(shares.values()) - 100) > 0.01:
            print("Percentages must total 100.")
            return
        split_type = "percentage"
    elif mode == 3:
        shares = {}
        remaining = amount
        for name in participants[:-1]:
            share = float(input(f"Amount for {name} (remaining {remaining:.2f}): "))
            shares[name] = share
            remaining -= share
        shares[participants[-1]] = round(remaining, 2)
        if abs(sum(shares.values()) - amount) > 0.01:
            print("Shares must total the expense amount.")
            return
        split_type = "custom"
    else:
        split_type = "equal"
    try:
        trip.add_expense(name, amount, payer, category, split_type, participants, shares, date, description)
        save_trip(trip)
        print("Expense added.")
    except (ValueError, KeyError, BudgetExceededError) as e:
        print("Error:", e)


def list_expenses(trip):
    if not trip.expenses:
        print("No expenses.")
        return
    print("\nID | Date | Expense | Amount | Paid By | Category")
    print("-" * 70)
    for e in trip.expenses:
        print(f"{e.expense_id} | {e.date} | {e.name} | ₹{e.amount:.2f} | {e.paid_by} | {e.category}")


def show_balance(trip):
    balances = calculate_balances(trip)
    for name, value in balances.items():
        status = "Receive" if value > 0.009 else "Pay" if value < -0.009 else "Settled"
        print(f"{name}: {status} ₹{abs(value):.2f}")
    save_trip(trip)


def show_settlement(trip):
    settlements = settle_expenses(trip)
    if not settlements:
        print("All settled.")
        return settlements
    print("\nSettlement")
    for s in settlements:
        print(f"{s['from']} -> {s['to']} : ₹{s['amount']:.2f}")
    from services.file_manager import save_settlements
    save_settlements(settlements)
    save_trip(trip)
    return settlements


def analytics_ui(trip):
    print("\nTotal:", trip.total_expense())
    remaining = trip.remaining_budget() if trip.budget > 0 else "No budget limit"
    print("Remaining budget:", remaining)
    try:
        stats = analyze_expenses(trip)
        print("NumPy:", stats)
    except ImportError:
        print("NumPy not installed.")
    try:
        result = pandas_summary(trip)
        print("\nPandas category totals:")
        print(result["category"])
        print("\nPandas payer totals:")
        print(result["payer"])
    except ImportError:
        print("Pandas not installed.")
    try:
        prediction = predict_next_expense(trip)
        print("Predicted next expense:", prediction if prediction is not None else "Need 2+ expenses")
    except ImportError:
        print("Scikit-learn not installed.")


def search_ui(trip):
    query = input("Search: ").strip()
    matches = search_relevant_expenses(trip, query)
    if not matches:
        print("No matching expenses.")
        return
    for e in matches:
        print(f"#{e.expense_id} {e.name} | ₹{e.amount:.2f} | {e.category} | {e.description}")


def nlp_ui():
    text = input("Enter expense description: ")
    words, clean, keywords = process_text(text)
    print("Tokens:", words)
    print("Without stop words:", clean)
    print("Keywords:", keywords)


def report_ui(trip):
    settlements = settle_expenses(trip)
    path = generate_report(trip, settlements)
    print("Report:", path)


def main():
    ensure_dirs()
    trip = load_trip()
    if trip is None:
        trip = create_trip()
        save_trip(trip)
    while True:
        print(f"\n=== TRIPSPLIT: {trip.name} ===")
        print("1. Add Friend")
        print("2. Add Expense")
        print("3. View Expenses")
        print("4. View Balances")
        print("5. Settle Expenses")
        print("6. Search Expense")
        print("7. Analytics")
        print("8. NLP Description Demo")
        print("9. Generate Report")
        print("10. Create Charts")
        print("11. GUI")
        print("12. Scikit-learn Prediction")
        print("13. Concept Demo")
        print("14. Exit")
        choice = input_int("Choice: ")
        try:
            match choice:
                case 1:
                    add_member_ui(trip)
                case 2:
                    add_expense_ui(trip)
                case 3:
                    list_expenses(trip)
                case 4:
                    show_balance(trip)
                case 5:
                    show_settlement(trip)
                case 6:
                    search_ui(trip)
                case 7:
                    analytics_ui(trip)
                case 8:
                    nlp_ui()
                case 9:
                    report_ui(trip)
                case 10:
                    try:
                        print("Created:", *make_charts(trip), sep="\n")
                    except ImportError:
                        print("Install requirements first.")
                case 11:
                    from gui.app import run
                    run()
                case 12:
                    try:
                        value = predict_next_expense(trip)
                        print("Prediction:", value if value is not None else "Add at least 2 expenses.")
                    except ImportError as e:
                        print(e)
                case 13:
                    from concepts_demo import run_demo
                    run_demo()
                case 14:
                    print("Program ended.")
                    break
                case _:
                    print("Invalid choice.")
        except (KeyError, ValueError, ZeroDivisionError, IndexError) as e:
            print("Error:", e)


if __name__ == "__main__":
    main()
