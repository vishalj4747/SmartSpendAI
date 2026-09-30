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
# PREPARE ML FEATURES
# =========================================

def prepare_dataset(df):

    # Convert date into datetime
    df["date"] = pd.to_datetime(df["date"])

    # Create useful date features
    df["year"] = df["date"].dt.year
    df["month"] = df["date"].dt.month
    df["day"] = df["date"].dt.day
    df["day_of_week"] = df["date"].dt.dayofweek

    # Weekend indicator
    df["is_weekend"] = (
        df["day_of_week"] >= 5
    ).astype(int)

    return df


# =========================================
# SHOW DATASET
# =========================================

def show_dataset(df):

    print("\n========== ML DATASET ==========")

    print(df)

    print("\n========== DATASET COLUMNS ==========")

    for column in df.columns:
        print(column)


# =========================================
# DATASET STATISTICS
# =========================================

def dataset_statistics(df):

    print("\n========== DATASET STATISTICS ==========")

    print(f"Number of records : {len(df)}")

    print(
        f"Average amount   : ₹{df['amount'].mean():.2f}"
    )

    print(
        f"Maximum amount   : ₹{df['amount'].max():.2f}"
    )

    print(
        f"Minimum amount   : ₹{df['amount'].min():.2f}"
    )

    print(
        f"Number of categories : {df['category'].nunique()}"
    )


# =========================================
# SAVE PREPARED DATASET
# =========================================

def save_dataset(df):

    output_file = "ml_expenses.csv"

    df.to_csv(
        output_file,
        index=False
    )

    print(
        f"\n✅ ML dataset saved as: {output_file}"
    )


# =========================================
# MAIN
# =========================================

def main():

    print("========================================")
    print("       SMARTSPEND AI v2.4")
    print("       ML Dataset Preparation")
    print("========================================")

    df = load_expenses()

    if df.empty:

        print("\n❌ No expense data found.")

        print(
            "Please add expenses using main.py first."
        )

        return

    # Prepare features
    df = prepare_dataset(df)

    # Display dataset
    show_dataset(df)

    # Statistics
    dataset_statistics(df)

    # Save CSV
    save_dataset(df)

    print("\n========================================")
    print("ML dataset preparation completed!")
    print("========================================")


# =========================================
# PROGRAM START
# =========================================

if __name__ == "__main__":
    main()