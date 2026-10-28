import math
import tkinter as tk
from tkinter import ttk, messagebox

from models.trip import Trip
from services.file_manager import load_trip, save_trip, BudgetExceededError
from services.settlement import settle_expenses
from services.validation import valid_amount, valid_mobile
from analytics.charts import make_charts


class TripSplitGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Trip Expense Manager")
        self.root.geometry("1050x760")
        self.root.minsize(820, 620)
        self.root.configure(bg="#eeefef")
        self.trip = load_trip() or Trip("My Trip", 0)
        self.configure_style()
        self.build()
        self.refresh()

    def configure_style(self):
        style = ttk.Style(self.root)
        style.theme_use("clam")
        style.configure(".", font=("Segoe UI", 10), background="#eeefef", foreground="#2d2d2d")
        style.configure("TFrame", background="#eeefef")
        style.configure("TLabel", background="#eeefef", foreground="#2d2d2d")
        style.configure("Title.TLabel", font=("Segoe UI", 22, "bold"), foreground="#1d1d1d")
        style.configure("Hint.TLabel", font=("Segoe UI", 9), foreground="#64748b")
        style.configure("TLabelframe", background="#f5f5f5", bordercolor="#d1d5db")
        style.configure("TLabelframe.Label", background="#f5f5f5", foreground="#343434", font=("Segoe UI", 10, "bold"))
        style.configure("TEntry", fieldbackground="#ffffff", padding=6)
        style.configure("TCombobox", fieldbackground="#ffffff", padding=5)
        style.configure("TButton", padding=(10, 7), background="#ffffff", bordercolor="#bfc4cf")
        style.map("TButton", background=[("active", "#e6e8ee")])
        style.configure("Accent.TButton", background="#4b4b4b", foreground="#ffffff", bordercolor="#4b4b4b")
        style.map("Accent.TButton", background=[("active", "#333333")])
        style.configure("Treeview", rowheight=30, background="#ffffff", fieldbackground="#ffffff", bordercolor="#dfe3eb")
        style.configure("Treeview.Heading", font=("Segoe UI", 9, "bold"), background="#ececf2", foreground="#2d2d2d", padding=8)
        style.map("Treeview", background=[("selected", "#dfe6f8")], foreground=[("selected", "#1f2937")])

    def build(self):
        root = self.root
        page = ttk.Frame(root, padding=(18, 14))
        page.pack(fill="both", expand=True)

        header = ttk.Frame(page)
        header.pack(fill="x", pady=(0, 10))
        ttk.Label(header, text="Trip Expense Manager", style="Title.TLabel").pack(side="left", anchor="w")

        action_bar = ttk.Frame(header)
        action_bar.pack(side="right")
        ttk.Button(action_bar, text="Delete Entire Trip", command=self.delete_trip).pack(side="left", padx=(0, 8))
        ttk.Button(action_bar, text="Report", command=self.make_charts).pack(side="left", padx=(0, 8))
        ttk.Button(action_bar, text="Save", command=self.save, style="Accent.TButton").pack(side="left")

        trip_frame = ttk.LabelFrame(page, text="", padding=12)
        trip_frame.pack(fill="x", pady=5)
        trip_frame.columnconfigure(1, weight=1)
        ttk.Label(trip_frame, text="Name").grid(row=0, column=0, sticky="w", padx=(0, 10))
        self.trip_name = tk.StringVar(value=self.trip.name)
        ttk.Entry(trip_frame, textvariable=self.trip_name, width=38).grid(row=0, column=1, sticky="ew", padx=(0, 20))
        ttk.Label(trip_frame, text="Budget").grid(row=0, column=2, sticky="w", padx=(0, 10))
        self.budget = tk.StringVar(value=str(self.trip.budget))
        ttk.Entry(trip_frame, textvariable=self.budget, width=18).grid(row=0, column=3, sticky="ew")

        member_frame = ttk.LabelFrame(page, text="Add Member", padding=12)
        member_frame.pack(fill="x", pady=5)
        member_frame.columnconfigure(1, weight=1)
        member_frame.columnconfigure(3, weight=1)
        self.member_name = tk.StringVar()
        self.mobile = tk.StringVar()
        ttk.Label(member_frame, text="Name").grid(row=0, column=0, sticky="w", padx=(0, 10))
        ttk.Entry(member_frame, textvariable=self.member_name).grid(row=0, column=1, sticky="ew", padx=(0, 14))
        ttk.Label(member_frame, text="Mobile").grid(row=0, column=2, sticky="w", padx=(0, 10))
        ttk.Entry(member_frame, textvariable=self.mobile).grid(row=0, column=3, sticky="ew", padx=(0, 14))
        ttk.Button(member_frame, text="Add Member", command=self.add_member, style="Accent.TButton").grid(row=0, column=4, padx=(8, 0))

        expense_frame = ttk.LabelFrame(page, text="Add Expense", padding=12)
        expense_frame.pack(fill="x", pady=5)
        self.expense_name = tk.StringVar()
        self.amount = tk.StringVar()
        self.category = tk.StringVar(value="Other")
        self.payer = tk.StringVar()
        self.description = tk.StringVar()
        for column, weight in enumerate((3, 1, 2, 2, 3)):
            expense_frame.columnconfigure(column, weight=weight)
        ttk.Label(expense_frame, text="Expense").grid(row=0, column=0, sticky="w", padx=(0, 8))
        ttk.Label(expense_frame, text="Amount").grid(row=0, column=1, sticky="w", padx=4)
        ttk.Label(expense_frame, text="Category").grid(row=0, column=2, sticky="w", padx=4)
        ttk.Label(expense_frame, text="Paid By").grid(row=0, column=3, sticky="w", padx=4)
        ttk.Label(expense_frame, text="Description").grid(row=0, column=4, sticky="w", padx=4)
        ttk.Entry(expense_frame, textvariable=self.expense_name).grid(row=1, column=0, sticky="ew", padx=(0, 8), pady=(4, 0))
        ttk.Entry(expense_frame, textvariable=self.amount).grid(row=1, column=1, sticky="ew", padx=4, pady=(4, 0))
        ttk.Combobox(
            expense_frame,
            textvariable=self.category,
            values=["Food", "Stay", "Travel", "Tickets", "Shopping", "Entertainment", "Other"],
            state="readonly",
        ).grid(row=1, column=2, sticky="ew", padx=4, pady=(4, 0))
        self.payer_combo = ttk.Combobox(expense_frame, textvariable=self.payer, state="readonly")
        self.payer_combo.grid(row=1, column=3, sticky="ew", padx=4, pady=(4, 0))
        ttk.Entry(expense_frame, textvariable=self.description).grid(row=1, column=4, sticky="ew", padx=(4, 0), pady=(4, 0))
        ttk.Button(expense_frame, text="Add Expense", command=self.add_expense, style="Accent.TButton").grid(row=2, column=0, columnspan=5, sticky="ew", pady=(10, 0))

        content = ttk.Frame(page)
        content.pack(fill="both", expand=True, pady=(10, 0))

        left = ttk.LabelFrame(content, text="Members", padding=(10, 8))
        left.pack(side="left", fill="y", expand=False, padx=(0, 12))
        right = ttk.LabelFrame(content, text="Expenses", padding=(10, 8))
        right.pack(side="left", fill="both", expand=True)

        self.member_list = tk.Listbox(
            left,
            width=34,
            height=10,
            font=("Segoe UI", 10),
            bg="#ffffff",
            fg="#2d2d2d",
            selectbackground="#dfe6f8",
            selectforeground="#1f2937",
            highlightthickness=1,
            highlightbackground="#d9deea",
            relief="flat",
        )
        self.member_list.pack(fill="both", expand=True)

        cols = ("id", "date", "name", "amount", "payer", "category")
        self.tree = ttk.Treeview(right, columns=cols, show="headings", selectmode="browse")
        headings = {"id": "ID", "date": "Date", "name": "Expense", "amount": "Amount", "payer": "Paid By", "category": "Category"}
        widths = {"id": 45, "date": 90, "name": 150, "amount": 90, "payer": 95, "category": 95}
        for column in cols:
            self.tree.heading(column, text=headings[column])
            self.tree.column(column, width=widths[column], minwidth=45, anchor="w")
        self.tree.pack(fill="both", expand=True)

        footer = ttk.Frame(page)
        footer.pack(fill="x", pady=(10, 0))
        footer.columnconfigure(0, weight=1)
        self.balance_value = tk.StringVar(value="Balance: ₹0.00")
        ttk.Label(footer, textvariable=self.balance_value, font=("Segoe UI", 10, "bold")).grid(row=0, column=0, sticky="w")
        btn_row = ttk.Frame(footer)
        btn_row.grid(row=0, column=1, sticky="e")
        ttk.Button(btn_row, text="Delete Selected Expense", command=self.delete_selected_expense).pack(side="left", padx=(0, 8))
        ttk.Button(btn_row, text="Reset", command=self.reset_trip).pack(side="left")

        self.status = tk.StringVar()
        ttk.Label(page, textvariable=self.status, style="Hint.TLabel", anchor="w").pack(fill="x", pady=(8, 0))

    def refresh(self, show_message=False):
        try:
            saved_trip = load_trip()
        except (OSError, ValueError) as error:
            messagebox.showerror("Refresh failed", f"Could not load saved trip data: {error}")
            return
        if saved_trip is not None:
            self.trip = saved_trip
        else:
            self.status.set("No saved trip yet. Add details, then select Save.")
            self.update_lists()
            return
        self.trip_name.set(self.trip.name)
        self.budget.set(str(self.trip.budget))
        self.update_lists()
        remaining = f"₹{self.trip.remaining_budget():.2f}" if self.trip.budget > 0 else "No limit"
        self.status.set(f"Refreshed from saved data  •  Total ₹{self.trip.total_expense():.2f}  •  Remaining budget {remaining}")
        if hasattr(self, "balance_value"):
            total = self.trip.total_expense()
            if self.trip.budget > 0:
                self.balance_value.set(f"Balance: ₹{(self.trip.budget - total):.2f}")
            else:
                self.balance_value.set(f"Balance: ₹{total:.2f}")
        if show_message:
            messagebox.showinfo("Refresh complete", f"Loaded saved trip: {self.trip.name}")

    def update_lists(self):
        self.member_list.delete(0, "end")
        for m in self.trip.members.values():
            self.member_list.insert("end", f"{m.name} | Paid ₹{m.paid:.2f} | Balance ₹{m.balance:.2f}")
        names = list(self.trip.members.keys())
        if hasattr(self, "payer_combo"):
            self.payer_combo["values"] = names
            if names and self.payer.get() not in names:
                self.payer.set(names[0])
        for row in self.tree.get_children():
            self.tree.delete(row)
        for e in self.trip.expenses:
            self.tree.insert("", "end", values=(e.expense_id, e.date, e.name, f"₹{e.amount:.2f}", e.paid_by, e.category))

    def delete_trip(self):
        self.trip = Trip("My Trip", 0)
        self.trip_name.set(self.trip.name)
        self.budget.set(str(self.trip.budget))
        self.member_name.set("")
        self.mobile.set("")
        self.expense_name.set("")
        self.amount.set("")
        self.description.set("")
        self.update_lists()
        self.status.set("Trip cleared. Add a new setup and save it.")
        save_trip(self.trip)

    def delete_selected_expense(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Selection required", "Select an expense in the table to delete.")
            return
        expense_id = self.tree.item(selected[0], "values")[0]
        self.trip.expenses = [expense for expense in self.trip.expenses if expense.expense_id != expense_id]
        save_trip(self.trip)
        self.refresh()

    def reset_trip(self):
        self.trip = Trip("My Trip", 0)
        self.trip_name.set(self.trip.name)
        self.budget.set("0")
        self.member_name.set("")
        self.mobile.set("")
        self.expense_name.set("")
        self.amount.set("")
        self.description.set("")
        self.update_lists()
        self.status.set("Trip reset.")
        save_trip(self.trip)

    def save(self):
        try:
            name = self.trip_name.get().strip()
            budget = float(self.budget.get())
            if not name:
                raise ValueError("Enter a trip name.")
            if not math.isfinite(budget) or budget < 0:
                raise ValueError("Budget must be zero or a positive amount.")
            self.trip.name = name
            self.trip.budget = budget
            save_trip(self.trip)
            self.refresh()
            self.status.set(f"Saved successfully  •  Total ₹{self.trip.total_expense():.2f}")
            messagebox.showinfo("Save complete", "Trip details saved.")
        except (ValueError, BudgetExceededError, OSError) as e:
            messagebox.showerror("Save failed", str(e))

    def add_member(self):
        name = self.member_name.get().strip()
        if not name:
            messagebox.showerror("Error", "Enter member name")
            return
        if self.mobile.get() and not valid_mobile(self.mobile.get()):
            messagebox.showerror("Error", "Invalid mobile")
            return
        try:
            self.trip.add_member(name, self.mobile.get())
            save_trip(self.trip)
            self.member_name.set("")
            self.mobile.set("")
            self.refresh()
        except (ValueError, BudgetExceededError, OSError) as e:
            messagebox.showerror("Error", str(e))

    def add_expense(self):
        if not self.expense_name.get().strip():
            messagebox.showerror("Error", "Enter an expense name")
            return
        if not valid_amount(self.amount.get()):
            messagebox.showerror("Error", "Enter a valid amount")
            return
        try:
            self.trip.add_expense(self.expense_name.get(), float(self.amount.get()), self.payer.get(), self.category.get(), "equal", list(self.trip.members.keys()), description=self.description.get())
            save_trip(self.trip)
            self.expense_name.set("")
            self.amount.set("")
            self.description.set("")
            self.refresh()
        except (KeyError, ValueError, BudgetExceededError, OSError) as e:
            messagebox.showerror("Error", str(e))

    def show_balance(self):
        from services.settlement import calculate_balances
        balances = calculate_balances(self.trip)
        text = "\n".join(f"{name}: ₹{value:.2f}" for name, value in balances.items()) or "No members"
        messagebox.showinfo("Balances", text)
        self.refresh()

    def show_settlement(self):
        settlements = settle_expenses(self.trip)
        save_trip(self.trip)
        if not settlements:
            text = "All settled"
        else:
            text = "\n".join(f"{s['from']} → {s['to']} : ₹{s['amount']:.2f}" for s in settlements)
        messagebox.showinfo("Settlement", text)
        self.refresh()

    def make_charts(self):
        try:
            paths = make_charts(self.trip)
            messagebox.showinfo("Charts", "Created:\n" + "\n".join(paths))
        except ImportError:
            messagebox.showerror("Error", "Install requirements first")

def run():
    root = tk.Tk()
    TripSplitGUI(root)
    root.mainloop()


if __name__ == "__main__":
    run()
