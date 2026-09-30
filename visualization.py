import sqlite3
import pandas as pd
import matplotlib.pyplot as plt


DB_NAME = "smartspend.db"


# =========================================
# LOAD DATA
# =========================================

def load_expenses():

    connection = sqlite3.connect(DB_NAME)

    query = """
        SELECT id, date, category, amount
        FROM expenses
        ORDER BY date
    """

    df = pd.read_sql_query(query, connection)

    connection.close()

    return df


# =========================================
# CATEGORY BAR CHART
# =========================================

def category_chart(df):

    category_data = (
        df.groupby("category")["amount"]
        .sum()
        .sort_values(ascending=False)
    )

    plt.figure(figsize=(9, 5))

    category_data.plot(kind="bar")

    plt.title("Spending by Category")
    plt.xlabel("Category")
    plt.ylabel("Amount (₹)")

    plt.xticks(rotation=0)

    plt.tight_layout()

    plt.show()


# =========================================
# CATEGORY PIE CHART
# =========================================

def category_pie_chart(df):

    category_data = (
        df.groupby("category")["amount"]
        .sum()
    )

    plt.figure(figsize=(7, 7))

    category_data.plot(
        kind="pie",
        autopct="%1.1f%%",
        startangle=90
    )

    plt.title("Expense Distribution by Category")

    plt.ylabel("")

    plt.tight_layout()

    plt.show()


# =========================================
# DAILY SPENDING LINE CHART
# =========================================

def daily_spending_chart(df):

    df["date"] = pd.to_datetime(df["date"])

    daily_data = (
        df.groupby("date")["amount"]
        .sum()
        .sort_index()
    )

    plt.figure(figsize=(10, 5))

    daily_data.plot(
        kind="line",
        marker="o"
    )

    plt.title("Daily Spending Trend")
    plt.xlabel("Date")
    plt.ylabel("Amount (₹)")

    plt.grid(True)

    plt.tight_layout()

    plt.show()


# =========================================
# MONTHLY SPENDING CHART
# =========================================

def monthly_spending_chart(df):

    df["date"] = pd.to_datetime(df["date"])

    df["month"] = df["date"].dt.to_period("M")

    monthly_data = (
        df.groupby("month")["amount"]
        .sum()
        .sort_index()
    )

    monthly_data.index = monthly_data.index.astype(str)

    plt.figure(figsize=(10, 5))

    monthly_data.plot(
        kind="line",
        marker="o"
    )

    plt.title("Monthly Spending Trend")
    plt.xlabel("Month")
    plt.ylabel("Amount (₹)")

    plt.grid(True)

    plt.tight_layout()

    plt.show()


# =========================================
# MAIN
# =========================================

def main():

    print("========================================")
    print("       SMARTSPEND AI v2.2")
    print("       Data Visualization")
    print("========================================")

    df = load_expenses()

    if df.empty:

        print("\n❌ No expense data found.")

        print(
            "Please add expenses using main.py first."
        )

        return

    print("\nOpening category chart...")
    category_chart(df)

    print("Opening category distribution...")
    category_pie_chart(df)

    print("Opening daily spending chart...")
    daily_spending_chart(df)

    print("Opening monthly spending chart...")
    monthly_spending_chart(df)

    print("\n========================================")
    print("All charts generated successfully!")
    print("========================================")


# =========================================
# PROGRAM START
# =========================================

if __name__ == "__main__":
    main()