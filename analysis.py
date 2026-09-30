import sqlite3
import pandas as pd

DB_NAME = "smartspend.db"


# =========================================
# LOAD DATA FROM SQLITE
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
# BASIC ANALYSIS
# =========================================

def basic_analysis(df):

    print("\n========== DATASET ==========")
    print(df)

    print("\n========== DATASET INFO ==========")

    print(f"Number of expenses : {len(df)}")
    print(f"Total spending    : ₹{df['amount'].sum():.2f}")
    print(f"Average expense   : ₹{df['amount'].mean():.2f}")
    print(f"Maximum expense   : ₹{df['amount'].max():.2f}")
    print(f"Minimum expense   : ₹{df['amount'].min():.2f}")


# =========================================
# CATEGORY ANALYSIS
# =========================================

def category_analysis(df):

    print("\n========== CATEGORY ANALYSIS ==========")

    category_data = (
        df.groupby("category")["amount"]
        .sum()
        .sort_values(ascending=False)
    )

    print(category_data)


# =========================================
# DAILY ANALYSIS
# =========================================

def date_analysis(df):

    print("\n========== DAILY SPENDING ==========")

    df["date"] = pd.to_datetime(df["date"])

    daily_spending = (
        df.groupby("date")["amount"]
        .sum()
        .sort_index()
    )

    print(daily_spending)


# =========================================
# TOP EXPENSES
# =========================================

def top_expenses(df):

    print("\n========== TOP 3 EXPENSES ==========")

    top = df.nlargest(3, "amount")

    print(
        top[
            ["date", "category", "amount"]
        ]
    )


# =========================================
# CATEGORY PERCENTAGE
# =========================================

def category_percentage(df):

    print("\n========== CATEGORY PERCENTAGE ==========")

    category_total = (
        df.groupby("category")["amount"]
        .sum()
    )

    total = category_total.sum()

    percentage = (
        category_total / total * 100
    ).sort_values(ascending=False)

    result = pd.DataFrame({
        "Amount": category_total,
        "Percentage": percentage
    })

    print(result)


# =========================================
# MONTHLY ANALYSIS
# =========================================

def monthly_analysis(df):

    print("\n========== MONTHLY ANALYSIS ==========")

    # Convert date into datetime
    df["date"] = pd.to_datetime(df["date"])

    # Create month column
    df["month"] = df["date"].dt.to_period("M")

    # Monthly total
    monthly_total = (
        df.groupby("month")["amount"]
        .sum()
        .sort_index()
    )

    print("\nMonthly Spending:")

    print(monthly_total)

    # Highest spending month
    highest_month = monthly_total.idxmax()
    highest_amount = monthly_total.max()

    print("\nHighest Spending Month:")

    print(
        f"{highest_month} → ₹{highest_amount:.2f}"
    )


# =========================================
# MONTHLY CATEGORY ANALYSIS
# =========================================

def monthly_category_analysis(df):

    print("\n========== MONTHLY CATEGORY ANALYSIS ==========")

    df["date"] = pd.to_datetime(df["date"])

    df["month"] = df["date"].dt.to_period("M")

    monthly_category = (
        df.groupby(
            ["month", "category"]
        )["amount"]
        .sum()
        .sort_values(ascending=False)
    )

    print(monthly_category)


# =========================================
# MAIN
# =========================================

def main():

    print("========================================")
    print("       SMARTSPEND AI v2.1")
    print("       Pandas Data Analysis")
    print("========================================")

    df = load_expenses()

    # Check if database has data
    if df.empty:

        print("\n❌ No expense data found.")

        print(
            "Please add some expenses using main.py first."
        )

        return

    # Run analyses

    basic_analysis(df)

    category_analysis(df)

    date_analysis(df)

    top_expenses(df)

    category_percentage(df)

    monthly_analysis(df)

    monthly_category_analysis(df)

    print("\n========================================")
    print("Pandas analysis completed successfully!")
    print("========================================")


# =========================================
# PROGRAM START
# =========================================

if __name__ == "__main__":
    main()