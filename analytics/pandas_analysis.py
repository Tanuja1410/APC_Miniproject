import pandas as pd
from services.file_manager import CSV_FILE


def load_data():
    try:
        return pd.read_csv(CSV_FILE)
    except (FileNotFoundError, pd.errors.EmptyDataError):
        return pd.DataFrame(columns=["ExpenseID", "Date", "Expense", "Amount", "PaidBy", "Category", "SplitType", "Participants", "Description"])


def summary(trip):
    df = load_data()
    if df.empty:
        return {"dataframe": df, "category": pd.Series(dtype=float), "payer": pd.Series(dtype=float), "highest": None}
    category = df.groupby("Category")["Amount"].sum().sort_values(ascending=False)
    payer = df.groupby("PaidBy")["Amount"].sum().sort_values(ascending=False)
    highest = df.loc[df["Amount"].idxmax()].to_dict()
    return {"dataframe": df, "category": category, "payer": payer, "highest": highest}
