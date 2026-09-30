from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sqlite3
import pandas as pd
from datetime import date
from sklearn.ensemble import RandomForestRegressor, IsolationForest
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.pipeline import Pipeline


app = FastAPI(
    title="SmartSpend AI API",
    description="AI-powered personal finance intelligence API",
    version="3.8"
)


# =========================
# CORS
# =========================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


DB_NAME = "smartspend.db"


# =========================
# DATABASE
# =========================

def connect_db():
    return sqlite3.connect(DB_NAME)


# =========================
# MODEL
# =========================

class Expense(BaseModel):
    date: str
    category: str
    amount: float


# =========================
# HOME
# =========================

@app.get("/")
def home():
    return {
        "message": "SmartSpend AI API is running!",
        "version": "3.8"
    }


# =========================
# GET EXPENSES
# =========================

@app.get("/expenses")
def get_expenses():

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, date, category, amount
        FROM expenses
        ORDER BY id ASC
    """)

    rows = cursor.fetchall()

    conn.close()

    return [
        {
            "id": row[0],
            "date": row[1],
            "category": row[2],
            "amount": row[3]
        }
        for row in rows
    ]


# =========================
# ADD EXPENSE
# =========================

@app.post("/expenses")
def add_expense(expense: Expense):

    if expense.amount <= 0:
        raise HTTPException(
            status_code=400,
            detail="Amount must be greater than zero."
        )

    if not expense.category.strip():
        raise HTTPException(
            status_code=400,
            detail="Category cannot be empty."
        )

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO expenses
        (date, category, amount)
        VALUES (?, ?, ?)
        """,
        (
            expense.date,
            expense.category.strip().title(),
            expense.amount
        )
    )

    new_id = cursor.lastrowid

    conn.commit()
    conn.close()

    return {
        "message": "Expense added successfully",
        "id": new_id
    }


# =========================
# UPDATE EXPENSE
# =========================

@app.put("/expenses/{expense_id}")
def update_expense(
    expense_id: int,
    expense: Expense
):

    if expense.amount <= 0:
        raise HTTPException(
            status_code=400,
            detail="Amount must be greater than zero."
        )

    if not expense.category.strip():
        raise HTTPException(
            status_code=400,
            detail="Category cannot be empty."
        )

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT id FROM expenses WHERE id = ?",
        (expense_id,)
    )

    existing = cursor.fetchone()

    if existing is None:

        conn.close()

        raise HTTPException(
            status_code=404,
            detail="Expense not found."
        )

    cursor.execute(
        """
        UPDATE expenses
        SET date = ?,
            category = ?,
            amount = ?
        WHERE id = ?
        """,
        (
            expense.date,
            expense.category.strip().title(),
            expense.amount,
            expense_id
        )
    )

    conn.commit()
    conn.close()

    return {
        "message": "Expense updated successfully",
        "id": expense_id
    }


# =========================
# DELETE EXPENSE
# =========================

@app.delete("/expenses/{expense_id}")
def delete_expense(expense_id: int):

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT id FROM expenses WHERE id = ?",
        (expense_id,)
    )

    existing = cursor.fetchone()

    if existing is None:

        conn.close()

        raise HTTPException(
            status_code=404,
            detail="Expense not found."
        )

    cursor.execute(
        "DELETE FROM expenses WHERE id = ?",
        (expense_id,)
    )

    conn.commit()
    conn.close()

    return {
        "message": "Expense deleted successfully",
        "id": expense_id
    }


# =========================
# SUMMARY
# =========================

@app.get("/summary")
def get_summary():

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            COUNT(*),
            COALESCE(SUM(amount), 0),
            COALESCE(AVG(amount), 0),
            COALESCE(MAX(amount), 0)
        FROM expenses
    """)

    row = cursor.fetchone()

    conn.close()

    return {
        "total_expenses": row[0],
        "total_spending": row[1],
        "average_expense": row[2],
        "highest_expense": row[3]
    }


# =========================
# CATEGORIES
# =========================

@app.get("/categories")
def get_categories():

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            category,
            SUM(amount) AS total
        FROM expenses
        GROUP BY category
        ORDER BY total DESC
    """)

    rows = cursor.fetchall()

    conn.close()

    return [
        {
            "category": row[0],
            "total": row[1]
        }
        for row in rows
    ]


# =========================
# ML PREDICTION
# =========================

def train_prediction_model():

    df = pd.read_csv(
        "demo_ml_expenses.csv"
    )

    features = [
        "month",
        "day",
        "day_of_week",
        "is_weekend",
        "category"
    ]

    target = "amount"

    X = df[features]
    y = df[target]

    categorical_features = [
        "category"
    ]

    numeric_features = [
        "month",
        "day",
        "day_of_week",
        "is_weekend"
    ]

    preprocessor = ColumnTransformer(
        transformers=[
            (
                "category",
                OneHotEncoder(
                    handle_unknown="ignore"
                ),
                categorical_features
            ),
            (
                "numeric",
                "passthrough",
                numeric_features
            )
        ]
    )

    model = Pipeline(
        steps=[
            (
                "preprocessor",
                preprocessor
            ),
            (
                "model",
                RandomForestRegressor(
                    n_estimators=100,
                    random_state=42
                )
            )
        ]
    )

    model.fit(X, y)

    return model


@app.get("/predict")
def predict_expense():

    model = train_prediction_model()

    today = date.today()

    input_data = pd.DataFrame([
        {
            "month": today.month,
            "day": today.day,
            "day_of_week": today.weekday(),
            "is_weekend": (
                1
                if today.weekday() >= 5
                else 0
            ),
            "category": "Food"
        }
    ])

    prediction = model.predict(
        input_data
    )[0]

    return {
        "category": "Food",
        "predicted_amount": round(
            float(prediction),
            2
        )
    }


# =========================
# ANOMALY DETECTION
# =========================

@app.get("/anomalies")
def detect_anomalies():

    conn = connect_db()

    df = pd.read_sql_query(
        """
        SELECT
            id,
            date,
            category,
            amount
        FROM expenses
        """,
        conn
    )

    conn.close()

    if df.empty:
        return []

    df["date"] = pd.to_datetime(
        df["date"]
    )

    df["month"] = df["date"].dt.month

    df["day_of_week"] = (
        df["date"].dt.dayofweek
    )

    df["is_weekend"] = (
        df["day_of_week"] >= 5
    ).astype(int)

    if len(df) < 5:
        return []

    features = [
        "amount",
        "month",
        "day_of_week",
        "is_weekend"
    ]

    model = IsolationForest(
        n_estimators=100,
        contamination=0.05,
        random_state=42
    )

    df["anomaly"] = model.fit_predict(
        df[features]
    )

    anomalies = df[
        df["anomaly"] == -1
    ]

    return [
        {
            "id": int(row["id"]),
            "date": row["date"].strftime(
                "%Y-%m-%d"
            ),
            "category": row["category"],
            "amount": float(
                row["amount"]
            ),
            "status": "Anomaly"
        }
        for _, row in anomalies.iterrows()
    ]


# =========================
# AI FINANCIAL ADVISOR
# =========================

@app.get("/advisor")
def financial_advisor():

    conn = connect_db()

    df = pd.read_sql_query(
        """
        SELECT
            id,
            date,
            category,
            amount
        FROM expenses
        """,
        conn
    )

    conn.close()

    if df.empty:

        return {
            "score": 0,
            "level": "No Data",
            "total_spending": 0,
            "highest_category": None,
            "highest_category_percentage": 0,
            "weekend_percentage": 0,
            "insights": [
                "Add some expenses to generate financial insights."
            ],
            "recommendations": [
                "Start tracking your daily expenses."
            ]
        }

    df["date"] = pd.to_datetime(
        df["date"]
    )

    total_spending = float(
        df["amount"].sum()
    )

    total_transactions = len(df)

    average_expense = float(
        df["amount"].mean()
    )

    # -------------------------
    # CATEGORY ANALYSIS
    # -------------------------

    category_totals = (
        df.groupby("category")["amount"]
        .sum()
        .sort_values(
            ascending=False
        )
    )

    highest_category = (
        category_totals.index[0]
    )

    highest_category_amount = float(
        category_totals.iloc[0]
    )

    highest_category_percentage = (
        highest_category_amount
        / total_spending
    ) * 100

    # -------------------------
    # WEEKEND ANALYSIS
    # -------------------------

    df["day_of_week"] = (
        df["date"].dt.dayofweek
    )

    weekend_expenses = df[
        df["day_of_week"] >= 5
    ]

    weekend_total = float(
        weekend_expenses["amount"].sum()
    )

    weekend_percentage = (
        weekend_total
        / total_spending
    ) * 100

    # -------------------------
    # LARGE EXPENSES
    # -------------------------

    large_expenses = df[
        df["amount"]
        > average_expense * 2
    ]

    # -------------------------
    # SCORE
    # -------------------------

    score = 100

    if highest_category_percentage >= 60:
        score -= 25

    elif highest_category_percentage >= 40:
        score -= 15

    elif highest_category_percentage >= 30:
        score -= 8

    if weekend_percentage >= 40:
        score -= 15

    elif weekend_percentage >= 30:
        score -= 8

    if len(large_expenses) >= 5:
        score -= 15

    elif len(large_expenses) >= 3:
        score -= 8

    score = max(
        0,
        min(100, score)
    )

    # -------------------------
    # LEVEL
    # -------------------------

    if score >= 80:
        level = "Healthy"

    elif score >= 60:
        level = "Moderate"

    else:
        level = "Needs Attention"

    # -------------------------
    # INSIGHTS
    # -------------------------

    insights = []

    insights.append(
        f"{highest_category} is your highest spending category."
    )

    insights.append(
        f"{highest_category} represents "
        f"{highest_category_percentage:.1f}% "
        f"of your total spending."
    )

    if weekend_percentage >= 30:

        insights.append(
            f"{weekend_percentage:.1f}% of your spending "
            f"happens on weekends."
        )

    if len(large_expenses) > 0:

        insights.append(
            f"You have {len(large_expenses)} "
            f"expenses significantly above your average."
        )

    # -------------------------
    # RECOMMENDATIONS
    # -------------------------

    recommendations = []

    if highest_category_percentage >= 50:

        recommendations.append(
            f"Try reducing {highest_category} spending "
            f"by 10-15% this month."
        )

    elif highest_category_percentage >= 30:

        recommendations.append(
            f"Keep an eye on your {highest_category} "
            f"expenses."
        )

    else:

        recommendations.append(
            "Your spending is distributed across categories."
        )

    if weekend_percentage >= 30:

        recommendations.append(
            "Set a weekend spending limit "
            "to control unnecessary expenses."
        )

    if len(large_expenses) >= 3:

        recommendations.append(
            "Review unusually large transactions "
            "before making similar purchases."
        )

    recommendations.append(
        "Track expenses regularly to improve "
        "your financial awareness."
    )

    return {
        "score": score,
        "level": level,
        "total_spending": round(
            total_spending,
            2
        ),
        "total_transactions": total_transactions,
        "average_expense": round(
            average_expense,
            2
        ),
        "highest_category": highest_category,
        "highest_category_amount": round(
            highest_category_amount,
            2
        ),
        "highest_category_percentage": round(
            highest_category_percentage,
            2
        ),
        "weekend_percentage": round(
            weekend_percentage,
            2
        ),
        "large_expenses": len(
            large_expenses
        ),
        "insights": insights,
        "recommendations": recommendations
    }