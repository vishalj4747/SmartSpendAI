import pandas as pd

from sklearn.ensemble import IsolationForest


DATA_FILE = "demo_ml_expenses.csv"


# =========================================
# LOAD DATA
# =========================================

def load_data():

    df = pd.read_csv(DATA_FILE)

    print("\n========== DATASET ==========")

    print(df.head())

    print(
        f"\nTotal records: {len(df)}"
    )

    return df


# =========================================
# PREPARE FEATURES
# =========================================

def prepare_features(df):

    # Features used for anomaly detection
    features = [
        "amount",
        "month",
        "day_of_week",
        "is_weekend"
    ]

    X = df[features]

    return X


# =========================================
# TRAIN ANOMALY MODEL
# =========================================

def detect_anomalies(df, X):

    print("\n========== ANOMALY DETECTION ==========")

    model = IsolationForest(
        n_estimators=100,
        contamination=0.05,
        random_state=42
    )

    # Train model and predict
    predictions = model.fit_predict(X)

    # Isolation Forest:
    # 1  = normal
    # -1 = anomaly

    df["anomaly"] = predictions

    # Convert to readable labels
    df["status"] = df["anomaly"].map({
        1: "Normal",
        -1: "Anomaly"
    })

    return df


# =========================================
# SHOW ANOMALIES
# =========================================

def show_anomalies(df):

    anomalies = df[
        df["status"] == "Anomaly"
    ]

    print("\n========== DETECTED ANOMALIES ==========")

    if anomalies.empty:

        print("No unusual expenses detected.")

        return

    print(
        anomalies[
            [
                "date",
                "category",
                "amount",
                "status"
            ]
        ].to_string(index=False)
    )

    print(
        f"\n⚠️ Unusual expenses found: "
        f"{len(anomalies)}"
    )


# =========================================
# SHOW NORMAL EXPENSES
# =========================================

def show_summary(df):

    normal_count = (
        (df["status"] == "Normal").sum()
    )

    anomaly_count = (
        (df["status"] == "Anomaly").sum()
    )

    print("\n========== SUMMARY ==========")

    print(
        f"Normal expenses  : {normal_count}"
    )

    print(
        f"Anomalous expenses : {anomaly_count}"
    )


# =========================================
# SAVE RESULTS
# =========================================

def save_results(df):

    output_file = "anomaly_results.csv"

    df.to_csv(
        output_file,
        index=False
    )

    print(
        f"\n✅ Results saved as: {output_file}"
    )


# =========================================
# MAIN
# =========================================

def main():

    print("========================================")
    print("       SMARTSPEND AI v2.7")
    print("       Anomaly Detection")
    print("========================================")

    df = load_data()

    X = prepare_features(df)

    df = detect_anomalies(
        df,
        X
    )

    show_anomalies(df)

    show_summary(df)

    save_results(df)

    print("\n========================================")
    print("Anomaly detection completed!")
    print("========================================")


# =========================================
# PROGRAM START
# =========================================

if __name__ == "__main__":
    main()