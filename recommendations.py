import sqlite3
import pandas as pd


DB_NAME = "smartspend.db"


# =========================================
# LOAD REAL EXPENSE DATA
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
# CATEGORY ANALYSIS
# =========================================

def category_analysis(df):

    category_data = (
        df.groupby("category")["amount"]
        .sum()
        .sort_values(ascending=False)
    )

    return category_data


# =========================================
# GENERATE RECOMMENDATIONS
# =========================================

def generate_recommendations(df):

    category_data = category_analysis(df)

    total = df["amount"].sum()

    recommendations = []

    print("\n========== SMART RECOMMENDATIONS ==========")

    # -----------------------------------------
    # CHECK HIGHEST CATEGORY
    # -----------------------------------------

    highest_category = category_data.index[0]

    highest_amount = category_data.iloc[0]

    highest_percentage = (
        highest_amount / total * 100
    )

    print(
        f"\n🏆 Highest spending category:"
        f" {highest_category}"
    )

    print(
        f"Amount: ₹{highest_amount:.2f}"
    )

    print(
        f"Percentage: {highest_percentage:.1f}%"
    )

    # -----------------------------------------
    # CATEGORY RECOMMENDATION
    # -----------------------------------------

    if highest_percentage >= 50:

        recommendation = (
            f"More than half of your spending "
            f"is going toward {highest_category}. "
            f"Consider setting a monthly budget "
            f"for this category."
        )

        recommendations.append(
            recommendation
        )

    elif highest_percentage >= 30:

        recommendation = (
            f"{highest_category} is a major part "
            f"of your spending. Monitor this "
            f"category regularly."
        )

        recommendations.append(
            recommendation
        )

    else:

        recommendation = (
            "Your spending is reasonably "
            "distributed across categories."
        )

        recommendations.append(
            recommendation
        )

    # -----------------------------------------
    # LARGE EXPENSE CHECK
    # -----------------------------------------

    average = df["amount"].mean()

    large_expenses = df[
        df["amount"] > average * 2
    ]

    if not large_expenses.empty:

        recommendations.append(
            "You have some expenses that are "
            "more than twice your average expense. "
            "Review these transactions."
        )

    # -----------------------------------------
    # WEEKEND ANALYSIS
    # -----------------------------------------

    df["date"] = pd.to_datetime(df["date"])

    df["is_weekend"] = (
        df["date"].dt.dayofweek >= 5
    )

    weekday_spending = df[
        df["is_weekend"] == False
    ]["amount"].sum()

    weekend_spending = df[
        df["is_weekend"] == True
    ]["amount"].sum()

    if weekend_spending > weekday_spending:

        recommendations.append(
            "Your spending is higher on "
            "weekends than weekdays. "
            "Keep an eye on weekend expenses."
        )

    # -----------------------------------------
    # DISPLAY RECOMMENDATIONS
    # -----------------------------------------

    print("\n💡 Recommendations:")

    for number, recommendation in enumerate(
        recommendations,
        start=1
    ):

        print(
            f"\n{number}. {recommendation}"
        )


# =========================================
# MAIN
# =========================================

def main():

    print("========================================")
    print("       SMARTSPEND AI v2.8")
    print("       Recommendation Engine")
    print("========================================")

    df = load_expenses()

    if df.empty:

        print("\n❌ No expense data found.")

        print(
            "Add expenses using main.py first."
        )

        return

    generate_recommendations(df)

    print("\n========================================")
    print("Recommendation generation completed!")
    print("========================================")


# =========================================
# PROGRAM START
# =========================================

if __name__ == "__main__":
    main()