import sqlite3
from datetime import datetime
import tkinter as tk
from tkinter import messagebox


# =========================================
# DATABASE
# =========================================

DB_NAME = "smartspend.db"


def connect_db():
    return sqlite3.connect(DB_NAME)


def create_table():

    connection = connect_db()
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            category TEXT NOT NULL,
            amount REAL NOT NULL
        )
    """)

    connection.commit()
    connection.close()


# =========================================
# VALIDATION
# =========================================

def get_valid_date():

    while True:

        date = input("Enter date (YYYY-MM-DD): ").strip()

        if date == "":
            print("❌ Date cannot be empty.")
            continue

        try:
            datetime.strptime(date, "%Y-%m-%d")
            return date

        except ValueError:
            print("❌ Invalid date.")
            print("Use format: YYYY-MM-DD")


def get_valid_category():

    while True:

        category = input("Enter category: ").strip()

        if category == "":
            print("❌ Category cannot be empty.")
            continue

        return category.title()


def get_valid_amount():

    while True:

        amount_input = input("Enter amount: ").strip()

        try:

            amount = float(amount_input)

            if amount <= 0:
                print("❌ Amount must be greater than 0.")
                continue

            return amount

        except ValueError:

            print("❌ Please enter a valid number.")


# =========================================
# ADD EXPENSE
# =========================================

def add_expense():

    print("\n========== ADD EXPENSE ==========")

    date = get_valid_date()
    category = get_valid_category()
    amount = get_valid_amount()

    connection = connect_db()
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO expenses (date, category, amount)
        VALUES (?, ?, ?)
    """, (date, category, amount))

    connection.commit()
    connection.close()

    print("\n✅ Expense saved successfully!")
    print(f"Date     : {date}")
    print(f"Category : {category}")
    print(f"Amount   : ₹{amount:.2f}")


# =========================================
# SHOW EXPENSES
# =========================================

def show_expenses():

    print("\n========== ALL EXPENSES ==========")

    connection = connect_db()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT id, date, category, amount
        FROM expenses
        ORDER BY id
    """)

    expenses = cursor.fetchall()

    connection.close()

    if len(expenses) == 0:

        print("No expenses found.")
        return

    for expense in expenses:

        print(f"\nExpense #{expense[0]}")
        print(f"Date     : {expense[1]}")
        print(f"Category : {expense[2]}")
        print(f"Amount   : ₹{expense[3]:.2f}")


# =========================================
# TOTAL
# =========================================

def calculate_total():

    connection = connect_db()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT SUM(amount)
        FROM expenses
    """)

    result = cursor.fetchone()

    connection.close()

    total = result[0]

    if total is None:
        total = 0

    print("\n========== TOTAL EXPENSE ==========")
    print(f"Total spent: ₹{total:.2f}")


# =========================================
# CATEGORY SUMMARY
# =========================================

def category_summary():

    print("\n========== CATEGORY SUMMARY ==========")

    connection = connect_db()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT category, SUM(amount)
        FROM expenses
        GROUP BY category
        ORDER BY SUM(amount) DESC
    """)

    categories = cursor.fetchall()

    connection.close()

    if len(categories) == 0:

        print("No expenses found.")
        return

    for category, total in categories:

        print(f"{category}: ₹{total:.2f}")


# =========================================
# HIGHEST CATEGORY
# =========================================

def highest_category():

    print("\n========== HIGHEST SPENDING CATEGORY ==========")

    connection = connect_db()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT category, SUM(amount)
        FROM expenses
        GROUP BY category
        ORDER BY SUM(amount) DESC
        LIMIT 1
    """)

    result = cursor.fetchone()

    connection.close()

    if result is None:

        print("No expenses found.")
        return

    print(f"Highest spending category: {result[0]}")
    print(f"Amount spent: ₹{result[1]:.2f}")


# =========================================
# DELETE EXPENSE
# =========================================

def delete_expense():

    print("\n========== DELETE EXPENSE ==========")

    connection = connect_db()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT id, date, category, amount
        FROM expenses
        ORDER BY id
    """)

    expenses = cursor.fetchall()

    if len(expenses) == 0:

        print("No expenses available.")
        connection.close()
        return

    for expense in expenses:

        print(
            f"ID: {expense[0]} | "
            f"Date: {expense[1]} | "
            f"Category: {expense[2]} | "
            f"Amount: ₹{expense[3]:.2f}"
        )

    while True:

        try:

            expense_id = int(
                input("\nEnter expense ID to delete: ").strip()
            )

        except ValueError:

            print("❌ Please enter a valid ID.")
            continue

        cursor.execute(
            "SELECT * FROM expenses WHERE id = ?",
            (expense_id,)
        )

        expense = cursor.fetchone()

        if expense is None:

            print("❌ Expense ID not found.")
            continue

        confirm = input(
            f"Delete expense #{expense_id}? (y/n): "
        ).strip().lower()

        if confirm == "y":

            cursor.execute(
                "DELETE FROM expenses WHERE id = ?",
                (expense_id,)
            )

            connection.commit()

            print("✅ Expense deleted successfully.")

        else:

            print("❌ Delete cancelled.")

        break

    connection.close()


# =========================================
# MONTHLY ANALYSIS
# =========================================

def monthly_analysis():

    print("\n========== MONTHLY ANALYSIS ==========")

    while True:

        month = input("Enter month (YYYY-MM): ").strip()

        try:

            datetime.strptime(month, "%Y-%m")
            break

        except ValueError:

            print("❌ Invalid month.")
            print("Use format: YYYY-MM")

    connection = connect_db()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT category, SUM(amount)
        FROM expenses
        WHERE substr(date, 1, 7) = ?
        GROUP BY category
        ORDER BY SUM(amount) DESC
    """, (month,))

    categories = cursor.fetchall()

    cursor.execute("""
        SELECT SUM(amount)
        FROM expenses
        WHERE substr(date, 1, 7) = ?
    """, (month,))

    total_result = cursor.fetchone()

    connection.close()

    total = total_result[0]

    if total is None:

        print(f"\nNo expenses found for {month}.")
        return

    print(f"\n========== {month} ANALYSIS ==========")
    print(f"Total spent: ₹{total:.2f}")

    print("\nCategory-wise spending:")

    for category, amount in categories:

        print(f"{category}: ₹{amount:.2f}")


# =========================================
# GET CATEGORY DATA
# =========================================

def get_category_data():

    connection = connect_db()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT category, SUM(amount)
        FROM expenses
        GROUP BY category
        ORDER BY SUM(amount) DESC
    """)

    data = cursor.fetchall()

    connection.close()

    return data


# =========================================
# DRAW CATEGORY CHART
# =========================================

def show_category_chart():

    data = get_category_data()

    if len(data) == 0:

        print("❌ No expense data available.")
        return

    window = tk.Tk()

    window.title("SmartSpend AI - Category Spending")
    window.geometry("800x600")

    canvas = tk.Canvas(
        window,
        width=800,
        height=600,
        bg="white"
    )

    canvas.pack()

    canvas.create_text(
        400,
        30,
        text="Category-wise Spending",
        font=("Arial", 20, "bold")
    )

    max_amount = max(amount for _, amount in data)

    bar_width = 80
    gap = 50
    start_x = 80
    base_y = 520
    max_height = 400

    for index, (category, amount) in enumerate(data):

        x1 = start_x + index * (bar_width + gap)
        x2 = x1 + bar_width

        bar_height = (
            amount / max_amount
        ) * max_height

        y1 = base_y - bar_height
        y2 = base_y

        canvas.create_rectangle(
            x1,
            y1,
            x2,
            y2,
            fill="steelblue"
        )

        canvas.create_text(
            (x1 + x2) / 2,
            y1 - 15,
            text=f"₹{amount:.0f}"
        )

        canvas.create_text(
            (x1 + x2) / 2,
            y2 + 20,
            text=category
        )

    window.mainloop()


# =========================================
# SPENDING INSIGHT
# =========================================

def spending_insight():

    print("\n========== SMART SPENDING INSIGHT ==========")

    data = get_category_data()

    if len(data) == 0:

        print("No expense data available.")
        return

    total = sum(amount for _, amount in data)

    highest_category_name = data[0][0]
    highest_amount = data[0][1]

    percentage = (highest_amount / total) * 100

    print(f"Total spending: ₹{total:.2f}")
    print(
        f"Highest spending category: "
        f"{highest_category_name}"
    )
    print(
        f"{highest_category_name} represents "
        f"{percentage:.1f}% of your total spending."
    )

    if percentage >= 50:

        print(
            f"💡 More than half of your spending "
            f"is in {highest_category_name}."
        )

    elif percentage >= 30:

        print(
            f"💡 {highest_category_name} is a major "
            f"part of your spending."
        )

    else:

        print(
            "💡 Your spending is distributed "
            "across multiple categories."
        )


# =========================================
# MAIN MENU
# =========================================

def main():

    create_table()

    while True:

        print("\n")
        print("========================================")
        print("        SMARTSPEND AI v1.5")
        print("========================================")
        print("1. Add Expense")
        print("2. Show Expenses")
        print("3. Calculate Total")
        print("4. Category Summary")
        print("5. Highest Spending Category")
        print("6. Delete Expense")
        print("7. Monthly Analysis")
        print("8. Category Chart")
        print("9. Spending Insight")
        print("10. Exit")
        print("========================================")

        choice = input("Enter your choice (1-10): ").strip()

        if choice == "1":

            add_expense()

        elif choice == "2":

            show_expenses()

        elif choice == "3":

            calculate_total()

        elif choice == "4":

            category_summary()

        elif choice == "5":

            highest_category()

        elif choice == "6":

            delete_expense()

        elif choice == "7":

            monthly_analysis()

        elif choice == "8":

            show_category_chart()

        elif choice == "9":

            spending_insight()

        elif choice == "10":

            print("\nThank you for using SmartSpend AI!")
            print("SmartSpend AI v1.5 Completed 🚀")
            break

        else:

            print("❌ Invalid choice.")
            print("Please enter a number between 1 and 10.")


# =========================================
# PROGRAM START
# =========================================

if __name__ == "__main__":
    main()