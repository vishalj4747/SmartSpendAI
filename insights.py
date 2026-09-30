import sqlite3
import pandas as pd


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
# TOTAL SPENDING
# =========================================

def total_spending(df):

    return df["amount"].sum()


# =========================================
# AVERAGE EXPENSE
# =========================================

def average_expense(df):

    return df["amount"].mean()


# =========================================
# HIGHEST EXPENSE
# =========================================

def highest_expense(df):

    index = df["amount"].idxmax()

    return df.loc[index]


# =========================================
# HIGHEST CATEGORY
# =========================================

def highest_category(df):

    category_data = (
        df.groupby("category")["amount"]
        .sum()
        .sort_values(ascending=False)
    )

    return category_data.index[0], category_data.iloc[0]


# =========================================
# CATEGORY PERCENTAGE
# =========================================

def category_percentage(df):

    category_data = (
        df.groupby("category")["amount"]
        .sum()
    )

    total = category_data.sum()

    percentage = (
        category_data / total * 100
    ).sort_values(ascending=False)

    return percentage


# =========================================
# GENERATE INSIGHTS
# =========================================

def generate_insights(df):

    total = total_spending(df)

    average = average_expense(df)

    highest = highest_expense(df)

    category, category_amount = highest_category(df)

    percentages = category_percentage(df)

    print("\n========== SMARTSPEND AI INSIGHTS ==========")

    # Total spending
    print(f"\n💰 Total Spending")
    print(f"₹{total:.2f}")

    # Average expense
    print(f"\n📊 Average Expense")
    print(f"₹{average:.2f}")

    # Highest expense
    print(f"\n🔥 Highest Single Expense")

    print(
        f"{highest['category']} → "
        f"₹{highest['amount']:.2f} "
        f"on {highest['date']}"
    )

    # Highest category
    print(f"\n🏆 Highest Spending Category")

    print(
        f"{category} → "
        f"₹{category_amount:.2f}"
    )

    # Percentage
    category_percent = percentages.iloc[0]

    print(
        f"\n📈 {category} represents "
        f"{category_percent:.1f}% of total spending."
    )

    # Spending warning
    print("\n⚠️ Spending Analysis")

    if category_percent >= 50:

        print(
            f"More than half of your spending "
            f"is going toward {category}."
        )

    elif category_percent >= 30:

        print(
            f"{category} is a major part "
            f"of your spending."
        )

    else:

        print(
            "Your spending is distributed "
            "across multiple categories."
        )


# =========================================
# MAIN
# =========================================

def main():

    print("========================================")
    print("       SMARTSPEND AI v2.3")
    print("       Smart Spending Insights")
    print("========================================")

    df = load_expenses()

    if df.empty:

        print("\n❌ No expense data found.")

        print(
            "Please add expenses using main.py first."
        )

        return

    generate_insights(df)

    print("\n========================================")
    print("Insight generation completed!")
    print("========================================")


# =========================================
# PROGRAM START
# =========================================

if __name__ == "__main__":
    main()