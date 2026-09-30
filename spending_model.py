import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, r2_score


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

def prepare_data(df):

    # Features used by the model
    features = [
        "month",
        "day",
        "day_of_week",
        "is_weekend",
        "category"
    ]

    # Target = amount we want to predict
    X = df[features]

    y = df["amount"]

    return X, y


# =========================================
# CREATE ML PIPELINE
# =========================================

def create_model():

    numeric_features = [
        "month",
        "day",
        "day_of_week",
        "is_weekend"
    ]

    categorical_features = [
        "category"
    ]

    # Convert category text into numbers
    preprocessor = ColumnTransformer(
        transformers=[
            (
                "category",
                OneHotEncoder(
                    handle_unknown="ignore"
                ),
                categorical_features
            )
        ],
        remainder="passthrough"
    )

    # Random Forest model
    model = RandomForestRegressor(
        n_estimators=100,
        random_state=42
    )

    # Complete ML pipeline
    pipeline = Pipeline(
        steps=[
            (
                "preprocessor",
                preprocessor
            ),
            (
                "model",
                model
            )
        ]
    )

    return pipeline


# =========================================
# TRAIN MODEL
# =========================================

def train_model(X, y):

    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=42
    )

    print("\n========== DATA SPLIT ==========")

    print(
        f"Training records : {len(X_train)}"
    )

    print(
        f"Testing records  : {len(X_test)}"
    )

    # Create model
    pipeline = create_model()

    # Train
    print("\nTraining model...")

    pipeline.fit(
        X_train,
        y_train
    )

    print("✅ Model training completed!")

    # Predict test data
    predictions = pipeline.predict(X_test)

    # Evaluation
    mae = mean_absolute_error(
        y_test,
        predictions
    )

    r2 = r2_score(
        y_test,
        predictions
    )

    print("\n========== MODEL EVALUATION ==========")

    print(
        f"Mean Absolute Error : ₹{mae:.2f}"
    )

    print(
        f"R² Score            : {r2:.4f}"
    )

    return pipeline


# =========================================
# MAKE NEW PREDICTION
# =========================================

def make_prediction(model):

    print("\n========== NEW PREDICTION ==========")

    # Example prediction
    new_expense = pd.DataFrame([
        {
            "month": 9,
            "day": 22,
            "day_of_week": 1,
            "is_weekend": 0,
            "category": "Food"
        }
    ])

    prediction = model.predict(
        new_expense
    )

    print(
        f"\nPredicted Food expense:"
        f" ₹{prediction[0]:.2f}"
    )


# =========================================
# MAIN
# =========================================

def main():

    print("========================================")
    print("       SMARTSPEND AI v2.6")
    print("       Spending Prediction ML")
    print("========================================")

    df = load_data()

    X, y = prepare_data(df)

    model = train_model(
        X,
        y
    )

    make_prediction(model)

    print("\n========================================")
    print("Machine Learning completed!")
    print("========================================")


if __name__ == "__main__":
    main()