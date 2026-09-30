import pandas as pd
import random
from datetime import date, timedelta


# =========================================
# SETTINGS
# =========================================

NUMBER_OF_DAYS = 120

OUTPUT_FILE = "demo_ml_expenses.csv"


# =========================================
# CATEGORIES
# =========================================

categories = {
    "Food": (100, 500),
    "Travel": (50, 300),
    "Shopping": (200, 1500),
    "Entertainment": (100, 800),
    "Bills": (300, 2000),
    "Education": (200, 1200),
    "Health": (100, 1000)
}


# =========================================
# GENERATE DATA
# =========================================

def generate_data():

    records = []

    start_date = date.today() - timedelta(
        days=NUMBER_OF_DAYS - 1
    )

    for i in range(NUMBER_OF_DAYS):

        current_date = (
            start_date + timedelta(days=i)
        )

        # Generate 1-3 expenses per day
        number_of_expenses = random.randint(1, 3)

        for _ in range(number_of_expenses):

            category = random.choice(
                list(categories.keys())
            )

            minimum, maximum = categories[category]

            amount = random.randint(
                minimum,
                maximum
            )

            records.append({
                "date": current_date.isoformat(),
                "category": category,
                "amount": amount
            })

    return pd.DataFrame(records)


# =========================================
# ADD ML FEATURES
# =========================================

def prepare_features(df):

    df["date"] = pd.to_datetime(df["date"])

    df["year"] = df["date"].dt.year

    df["month"] = df["date"].dt.month

    df["day"] = df["date"].dt.day

    df["day_of_week"] = (
        df["date"].dt.dayofweek
    )

    df["is_weekend"] = (
        df["day_of_week"] >= 5
    ).astype(int)

    return df


# =========================================
# MAIN
# =========================================

def main():

    print("========================================")
    print("       SMARTSPEND AI v2.5")
    print("       Demo Dataset Generator")
    print("========================================")

    df = generate_data()

    df = prepare_features(df)

    # Save CSV
    df.to_csv(
        OUTPUT_FILE,
        index=False
    )

    print("\n✅ Demo dataset generated!")

    print(
        f"Records generated : {len(df)}"
    )

    print(
        f"Date range        : "
        f"{df['date'].min().date()} "
        f"to "
        f"{df['date'].max().date()}"
    )

    print(
        f"Categories        : "
        f"{df['category'].nunique()}"
    )

    print(
        f"Total spending    : "
        f"₹{df['amount'].sum():.2f}"
    )

    print(
        f"\nSaved as: {OUTPUT_FILE}"
    )

    print("\n========== SAMPLE DATA ==========")

    print(
        df.head(10).to_string(index=False)
    )

    print("\n========================================")
    print("Demo dataset ready for ML!")
    print("========================================")


if __name__ == "__main__":
    main()