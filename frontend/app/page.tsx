"use client";

import {
  CSSProperties,
  FormEvent,
  useEffect,
  useMemo,
  useState,
} from "react";

import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

const API_URL = "http://localhost:8000";

type Summary = {
  total_spending: number;
  total_transactions: number;
  average_expense: number;
  highest_expense: number;
};

type Category = {
  category: string;
  total: number;
};

type Expense = {
  id: number;
  date: string;
  category: string;
  amount: number;
};

type Prediction = {
  predicted_food_spending: number;
};

type Anomaly = {
  date: string;
  category: string;
  amount: number;
  anomaly: number;
};

type Advisor = {
  score: number;
  level: string;
  total_spending: number;
  total_transactions: number;
  average_expense: number;
  highest_category: string | null;
  highest_category_amount: number;
  highest_category_percentage: number;
  weekend_percentage: number;
  large_expenses: number;
  insights: string[];
  recommendations: string[];
};

type ExpenseForm = {
  date: string;
  category: string;
  amount: string;
};

export default function Home() {
  const [summary, setSummary] = useState<Summary | null>(null);
  const [categories, setCategories] = useState<Category[]>([]);
  const [expenses, setExpenses] = useState<Expense[]>([]);
  const [prediction, setPrediction] = useState<Prediction | null>(null);
  const [anomalies, setAnomalies] = useState<Anomaly[]>([]);
  const [advisor, setAdvisor] = useState<Advisor | null>(null);

  const [loading, setLoading] = useState(true);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  const [form, setForm] = useState<ExpenseForm>({
    date: new Date().toISOString().split("T")[0],
    category: "Food",
    amount: "",
  });

  const [editingExpense, setEditingExpense] = useState<Expense | null>(null);

  const [selectedCategory, setSelectedCategory] = useState("All");
  const [startDate, setStartDate] = useState("");
  const [endDate, setEndDate] = useState("");

  // --------------------------------------------------
  // LOAD ALL DATA
  // --------------------------------------------------

  const loadData = async () => {
    try {
      setLoading(true);
      setError("");

      const [
        summaryResponse,
        categoriesResponse,
        expensesResponse,
        predictionResponse,
        anomaliesResponse,
        advisorResponse,
      ] = await Promise.all([
        fetch(`${API_URL}/summary`),
        fetch(`${API_URL}/categories`),
        fetch(`${API_URL}/expenses`),
        fetch(`${API_URL}/predict`),
        fetch(`${API_URL}/anomalies`),
        fetch(`${API_URL}/advisor`),
      ]);

      if (!summaryResponse.ok) {
        throw new Error("Failed to load summary");
      }

      const summaryData = await summaryResponse.json();
      const categoriesData = await categoriesResponse.json();
      const expensesData = await expensesResponse.json();

      setSummary(summaryData);
      setCategories(categoriesData);
      setExpenses(expensesData);

      if (predictionResponse.ok) {
        setPrediction(await predictionResponse.json());
      }

      if (anomaliesResponse.ok) {
        setAnomalies(await anomaliesResponse.json());
      }

      if (advisorResponse.ok) {
        setAdvisor(await advisorResponse.json());
      }
    } catch (err) {
      console.error(err);
      setError(
        "Backend se connection nahi ho raha. Check karo FastAPI server running hai ya nahi."
      );
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  // --------------------------------------------------
  // ADD EXPENSE
  // --------------------------------------------------

  const handleAddExpense = async (event: FormEvent) => {
    event.preventDefault();

    setMessage("");
    setError("");

    if (!form.date || !form.category || !form.amount) {
      setError("Please fill all fields.");
      return;
    }

    const amount = Number(form.amount);

    if (amount <= 0) {
      setError("Amount must be greater than 0.");
      return;
    }

    try {
      const response = await fetch(`${API_URL}/expenses`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          date: form.date,
          category: form.category,
          amount,
        }),
      });

      if (!response.ok) {
        throw new Error("Failed to add expense");
      }

      setForm({
        date: new Date().toISOString().split("T")[0],
        category: "Food",
        amount: "",
      });

      setMessage("Expense added successfully.");

      await loadData();
    } catch (err) {
      console.error(err);
      setError("Expense add nahi hua.");
    }
  };

  // --------------------------------------------------
  // DELETE EXPENSE
  // --------------------------------------------------

  const handleDelete = async (id: number) => {
    const confirmDelete = window.confirm(
      "Are you sure you want to delete this expense?"
    );

    if (!confirmDelete) return;

    try {
      const response = await fetch(`${API_URL}/expenses/${id}`, {
        method: "DELETE",
      });

      if (!response.ok) {
        throw new Error("Delete failed");
      }

      setMessage("Expense deleted successfully.");

      await loadData();
    } catch (err) {
      console.error(err);
      setError("Expense delete nahi hua.");
    }
  };

  // --------------------------------------------------
  // OPEN EDIT
  // --------------------------------------------------

  const openEdit = (expense: Expense) => {
    setEditingExpense(expense);
  };

  // --------------------------------------------------
  // UPDATE EXPENSE
  // --------------------------------------------------

  const handleUpdate = async (event: FormEvent) => {
    event.preventDefault();

    if (!editingExpense) return;

    try {
      const response = await fetch(
        `${API_URL}/expenses/${editingExpense.id}`,
        {
          method: "PUT",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            date: editingExpense.date,
            category: editingExpense.category,
            amount: Number(editingExpense.amount),
          }),
        }
      );

      if (!response.ok) {
        throw new Error("Update failed");
      }

      setEditingExpense(null);
      setMessage("Expense updated successfully.");

      await loadData();
    } catch (err) {
      console.error(err);
      setError("Expense update nahi hua.");
    }
  };

  // --------------------------------------------------
  // FILTER EXPENSES
  // --------------------------------------------------

  const filteredExpenses = useMemo(() => {
    return expenses.filter((expense) => {
      const categoryMatch =
        selectedCategory === "All" ||
        expense.category === selectedCategory;

      const startMatch =
        !startDate || expense.date >= startDate;

      const endMatch =
        !endDate || expense.date <= endDate;

      return categoryMatch && startMatch && endMatch;
    });
  }, [expenses, selectedCategory, startDate, endDate]);

  // --------------------------------------------------
  // FILTER ANALYTICS
  // --------------------------------------------------

  const filteredTotal = useMemo(() => {
    return filteredExpenses.reduce(
      (sum, expense) => sum + Number(expense.amount),
      0
    );
  }, [filteredExpenses]);

  const filteredAverage = useMemo(() => {
    if (filteredExpenses.length === 0) return 0;

    return filteredTotal / filteredExpenses.length;
  }, [filteredExpenses, filteredTotal]);

  const filteredHighest = useMemo(() => {
    if (filteredExpenses.length === 0) return 0;

    return Math.max(
      ...filteredExpenses.map((expense) => Number(expense.amount))
    );
  }, [filteredExpenses]);

  // --------------------------------------------------
  // MONTHLY DATA
  // --------------------------------------------------

  const monthlyData = useMemo(() => {
    const monthly: Record<string, number> = {};

    filteredExpenses.forEach((expense) => {
      const month = expense.date.slice(0, 7);

      monthly[month] = (monthly[month] || 0) + Number(expense.amount);
    });

    return Object.entries(monthly)
      .sort(([a], [b]) => a.localeCompare(b))
      .map(([month, amount]) => ({
        month,
        amount: Number(amount.toFixed(2)),
      }));
  }, [filteredExpenses]);

  // --------------------------------------------------
  // CATEGORY CHART DATA
  // --------------------------------------------------

  const categoryChartData = useMemo(() => {
    const categoryTotals: Record<string, number> = {};

    filteredExpenses.forEach((expense) => {
      categoryTotals[expense.category] =
        (categoryTotals[expense.category] || 0) +
        Number(expense.amount);
    });

    return Object.entries(categoryTotals)
      .map(([category, amount]) => ({
        category,
        amount: Number(amount.toFixed(2)),
      }))
      .sort((a, b) => b.amount - a.amount);
  }, [filteredExpenses]);

  // --------------------------------------------------
  // CLEAR FILTERS
  // --------------------------------------------------

  const clearFilters = () => {
    setSelectedCategory("All");
    setStartDate("");
    setEndDate("");
  };

  // --------------------------------------------------
  // FORMAT CURRENCY
  // --------------------------------------------------

  const money = (value: number) => {
    return `₹${Number(value || 0).toLocaleString("en-IN", {
      maximumFractionDigits: 2,
    })}`;
  };

  // --------------------------------------------------
  // PIE COLORS
  // --------------------------------------------------

  const pieCells = [
    "#8b5cf6",
    "#06b6d4",
    "#22c55e",
    "#f59e0b",
    "#ef4444",
    "#ec4899",
    "#3b82f6",
  ];

  // --------------------------------------------------
  // LOADING
  // --------------------------------------------------

  if (loading) {
    return (
      <main className="app-shell">
        <div className="loading-screen">
          <div className="loading-spinner"></div>
          <h2>SmartSpend AI</h2>
          <p>Loading your financial intelligence...</p>
        </div>
      </main>
    );
  }

  // --------------------------------------------------
  // UI
  // --------------------------------------------------

  return (
    <main className="app-shell">
      <div className="container">

        {/* ========================================= */}
        {/* HEADER */}
        {/* ========================================= */}

        <header className="topbar">
          <div>
            <div className="brand">
              SmartSpend<span>AI</span>
            </div>

            <p className="brand-subtitle">
              Personal Finance Intelligence Dashboard
            </p>
          </div>

          <div className="status-badge">
            <span className="status-dot"></span>
            AI SYSTEM ONLINE
          </div>
        </header>

        {/* ========================================= */}
        {/* ALERTS */}
        {/* ========================================= */}

        {message && (
          <div className="success-message">
            ✓ {message}
          </div>
        )}

        {error && (
          <div className="error-message">
            ⚠ {error}
          </div>
        )}

        {/* ========================================= */}
        {/* HERO */}
        {/* ========================================= */}

        <section className="hero-section">
          <div>
            <p className="ai-label">SMARTSPEND AI</p>

            <h1>
              Understand your money.
              <br />
              <span>Improve your decisions.</span>
            </h1>

            <p className="hero-description">
              Track expenses, analyze spending patterns, detect unusual
              transactions and get AI-powered financial insights.
            </p>
          </div>
        </section>

        {/* ========================================= */}
        {/* SUMMARY CARDS */}
        {/* ========================================= */}

        <section className="summary-grid">
          <div className="summary-card">
            <div className="summary-icon">₹</div>

            <div>
              <p>Total Spending</p>
              <h2>{money(summary?.total_spending || 0)}</h2>
            </div>
          </div>

          <div className="summary-card">
            <div className="summary-icon">#</div>

            <div>
              <p>Transactions</p>
              <h2>{summary?.total_transactions || 0}</h2>
            </div>
          </div>

          <div className="summary-card">
            <div className="summary-icon">Ø</div>

            <div>
              <p>Average Expense</p>
              <h2>{money(summary?.average_expense || 0)}</h2>
            </div>
          </div>

          <div className="summary-card">
            <div className="summary-icon">↑</div>

            <div>
              <p>Highest Expense</p>
              <h2>{money(summary?.highest_expense || 0)}</h2>
            </div>
          </div>
        </section>

        {/* ========================================= */}
        {/* ADD EXPENSE */}
        {/* ========================================= */}

        <section className="panel add-expense-panel">
          <div className="section-heading">
            <div>
              <p className="ai-label">TRACK</p>
              <h2>Add New Expense</h2>
              <p>Record your daily spending.</p>
            </div>
          </div>

          <form
            className="expense-form"
            onSubmit={handleAddExpense}
          >
            <div className="form-group">
              <label>Date</label>

              <input
                type="date"
                value={form.date}
                onChange={(e) =>
                  setForm({
                    ...form,
                    date: e.target.value,
                  })
                }
              />
            </div>

            <div className="form-group">
              <label>Category</label>

              <select
                value={form.category}
                onChange={(e) =>
                  setForm({
                    ...form,
                    category: e.target.value,
                  })
                }
              >
                <option value="Food">Food</option>
                <option value="Travel">Travel</option>
                <option value="Shopping">Shopping</option>
                <option value="Bills">Bills</option>
                <option value="Entertainment">
                  Entertainment
                </option>
                <option value="Education">Education</option>
                <option value="Health">Health</option>
                <option value="Other">Other</option>
              </select>
            </div>

            <div className="form-group">
              <label>Amount</label>

              <input
                type="number"
                placeholder="₹ 0"
                min="1"
                step="0.01"
                value={form.amount}
                onChange={(e) =>
                  setForm({
                    ...form,
                    amount: e.target.value,
                  })
                }
              />
            </div>

            <button
              type="submit"
              className="primary-button"
            >
              + Add Expense
            </button>
          </form>
        </section>

        {/* ========================================= */}
        {/* ANALYTICS FILTER */}
        {/* ========================================= */}

        <section className="panel analytics-filter">
          <div className="section-heading">
            <div>
              <p className="ai-label">ANALYTICS</p>
              <h2>Spending Explorer</h2>
              <p>Filter and analyze your expenses.</p>
            </div>
          </div>

          <div className="filter-grid">
            <div className="form-group">
              <label>Category</label>

              <select
                value={selectedCategory}
                onChange={(e) =>
                  setSelectedCategory(e.target.value)
                }
              >
                <option value="All">All Categories</option>

                {categories.map((category) => (
                  <option
                    key={category.category}
                    value={category.category}
                  >
                    {category.category}
                  </option>
                ))}
              </select>
            </div>

            <div className="form-group">
              <label>Start Date</label>

              <input
                type="date"
                value={startDate}
                onChange={(e) =>
                  setStartDate(e.target.value)
                }
              />
            </div>

            <div className="form-group">
              <label>End Date</label>

              <input
                type="date"
                value={endDate}
                onChange={(e) =>
                  setEndDate(e.target.value)
                }
              />
            </div>

            <button
              type="button"
              className="secondary-button"
              onClick={clearFilters}
            >
              Clear Filters
            </button>
          </div>

          <div className="filter-result">
            <div>
              <span>Filtered Spending</span>
              <strong>{money(filteredTotal)}</strong>
            </div>

            <div>
              <span>Transactions</span>
              <strong>{filteredExpenses.length}</strong>
            </div>

            <div>
              <span>Average</span>
              <strong>{money(filteredAverage)}</strong>
            </div>

            <div>
              <span>Highest</span>
              <strong>{money(filteredHighest)}</strong>
            </div>
          </div>
        </section>

        {/* ========================================= */}
        {/* CHARTS */}
        {/* ========================================= */}

        <section className="charts-grid">

          {/* CATEGORY BAR */}
          <div className="chart-card">
            <div className="chart-header">
              <div>
                <p className="ai-label">BREAKDOWN</p>
                <h3>Category Spending</h3>
              </div>
            </div>

            <div className="chart-container">
              {categoryChartData.length > 0 ? (
                <ResponsiveContainer
                  width="100%"
                  height="100%"
                >
                  <BarChart data={categoryChartData}>
                    <CartesianGrid
                      strokeDasharray="3 3"
                      opacity={0.15}
                    />

                    <XAxis
                      dataKey="category"
                      tick={{ fill: "#aaa", fontSize: 12 }}
                    />

                    <YAxis
                      tick={{ fill: "#aaa", fontSize: 12 }}
                    />

                    <Tooltip
                      formatter={(value) => [
                        money(Number(value)),
                        "Spending",
                      ]}
                    />

                    <Bar
                      dataKey="amount"
                      radius={[8, 8, 0, 0]}
                    />
                  </BarChart>
                </ResponsiveContainer>
              ) : (
                <div className="empty-chart">
                  No category data available.
                </div>
              )}
            </div>
          </div>

          {/* PIE */}
          <div className="chart-card">
            <div className="chart-header">
              <div>
                <p className="ai-label">DISTRIBUTION</p>
                <h3>Spending Distribution</h3>
              </div>
            </div>

            <div className="chart-container">
              {categoryChartData.length > 0 ? (
                <ResponsiveContainer
                  width="100%"
                  height="100%"
                >
                  <PieChart>
                    <Pie
                      data={categoryChartData}
                      dataKey="amount"
                      nameKey="category"
                      cx="50%"
                      cy="50%"
                      outerRadius={110}
                      innerRadius={60}
                      paddingAngle={3}
                    >
                      {categoryChartData.map(
                        (_, index) => (
                          <Cell
                            key={`cell-${index}`}
                            fill={
                              pieCells[
                                index % pieCells.length
                              ]
                            }
                          />
                        )
                      )}
                    </Pie>

                    <Tooltip
                      formatter={(value) => [
                        money(Number(value)),
                        "Spending",
                      ]}
                    />
                  </PieChart>
                </ResponsiveContainer>
              ) : (
                <div className="empty-chart">
                  No data available.
                </div>
              )}
            </div>
          </div>

          {/* MONTHLY */}
          <div className="chart-card chart-wide">
            <div className="chart-header">
              <div>
                <p className="ai-label">TREND</p>
                <h3>Monthly Spending</h3>
              </div>
            </div>

            <div className="chart-container">
              {monthlyData.length > 0 ? (
                <ResponsiveContainer
                  width="100%"
                  height="100%"
                >
                  <BarChart data={monthlyData}>
                    <CartesianGrid
                      strokeDasharray="3 3"
                      opacity={0.15}
                    />

                    <XAxis
                      dataKey="month"
                      tick={{ fill: "#aaa", fontSize: 12 }}
                    />

                    <YAxis
                      tick={{ fill: "#aaa", fontSize: 12 }}
                    />

                    <Tooltip
                      formatter={(value) => [
                        money(Number(value)),
                        "Spending",
                      ]}
                    />

                    <Bar
                      dataKey="amount"
                      radius={[8, 8, 0, 0]}
                    />
                  </BarChart>
                </ResponsiveContainer>
              ) : (
                <div className="empty-chart">
                  No monthly data available.
                </div>
              )}
            </div>
          </div>
        </section>

        {/* ========================================= */}
        {/* AI FINANCIAL ADVISOR */}
        {/* ========================================= */}

        <section className="advisor-section">
          <div className="section-heading">
            <div>
              <p className="ai-label">SMARTSPEND AI</p>

              <h2>AI Financial Advisor</h2>

              <p>
                Your spending behavior analyzed by AI.
              </p>
            </div>
          </div>

          {advisor ? (
            <div className="advisor-grid">

              {/* SCORE */}
              <div className="advisor-score-card">
                <div
                  className="score-circle"
                  style={
                    {
                      "--score": advisor.score,
                    } as CSSProperties
                  }
                >
                  <div>
                    <strong>{advisor.score}</strong>
                    <span>/100</span>
                  </div>
                </div>

                <h3>{advisor.level}</h3>

                <p>
                  Financial spending health
                </p>
              </div>

              {/* INSIGHTS */}
              <div className="advisor-card">
                <div className="advisor-card-title">
                  <span>💡</span>
                  <h3>AI Insights</h3>
                </div>

                {advisor.insights.length > 0 ? (
                  <div className="advisor-list">
                    {advisor.insights.map(
                      (insight, index) => (
                        <div
                          className="advisor-item"
                          key={index}
                        >
                          <span className="advisor-bullet">
                            {index + 1}
                          </span>

                          <p>{insight}</p>
                        </div>
                      )
                    )}
                  </div>
                ) : (
                  <p>No insights available yet.</p>
                )}
              </div>

              {/* RECOMMENDATIONS */}
              <div className="advisor-card">
                <div className="advisor-card-title">
                  <span>🎯</span>
                  <h3>Recommendations</h3>
                </div>

                {advisor.recommendations.length >
                0 ? (
                  <div className="advisor-list">
                    {advisor.recommendations.map(
                      (recommendation, index) => (
                        <div
                          className="advisor-item"
                          key={index}
                        >
                          <span className="advisor-bullet">
                            ✓
                          </span>

                          <p>{recommendation}</p>
                        </div>
                      )
                    )}
                  </div>
                ) : (
                  <p>
                    No recommendations available yet.
                  </p>
                )}
              </div>

              {/* METRICS */}
              <div className="advisor-metrics">

                <div className="advisor-metric">
                  <span>Top Category</span>

                  <strong>
                    {advisor.highest_category ||
                      "N/A"}
                  </strong>

                  <small>
                    {money(
                      advisor.highest_category_amount
                    )}
                  </small>
                </div>

                <div className="advisor-metric">
                  <span>Category Share</span>

                  <strong>
                    {advisor.highest_category_percentage.toFixed(
                      1
                    )}
                    %
                  </strong>

                  <small>
                    of total spending
                  </small>
                </div>

                <div className="advisor-metric">
                  <span>Weekend Spending</span>

                  <strong>
                    {advisor.weekend_percentage.toFixed(
                      1
                    )}
                    %
                  </strong>

                  <small>
                    of total spending
                  </small>
                </div>

                <div className="advisor-metric">
                  <span>Large Expenses</span>

                  <strong>
                    {advisor.large_expenses}
                  </strong>

                  <small>
                    higher-value transactions
                  </small>
                </div>
              </div>
            </div>
          ) : (
            <div className="advisor-empty">
              Add expenses to generate AI financial
              advice.
            </div>
          )}
        </section>

        {/* ========================================= */}
        {/* AI PREDICTION */}
        {/* ========================================= */}

        <section className="ai-section">
          <div className="section-heading">
            <div>
              <p className="ai-label">MACHINE LEARNING</p>

              <h2>AI Spending Prediction</h2>

              <p>
                Random Forest model prediction.
              </p>
            </div>
          </div>

          {prediction ? (
            <div className="ai-prediction-card">
              <div>
                <span>Predicted Food Spending</span>

                <strong>
                  {money(
                    prediction.predicted_food_spending
                  )}
                </strong>
              </div>

              <div className="prediction-badge">
                RANDOM FOREST
              </div>
            </div>
          ) : (
            <div className="advisor-empty">
              Prediction unavailable.
            </div>
          )}
        </section>

        {/* ========================================= */}
        {/* ANOMALY DETECTION */}
        {/* ========================================= */}

        <section className="panel">
          <div className="section-heading">
            <div>
              <p className="ai-label">AI DETECTION</p>

              <h2>Unusual Transactions</h2>

              <p>
                Transactions detected as unusual by
                Isolation Forest.
              </p>
            </div>
          </div>

          {anomalies.length > 0 ? (
            <div className="table-wrapper">
              <table className="expense-table">
                <thead>
                  <tr>
                    <th>Date</th>
                    <th>Category</th>
                    <th>Amount</th>
                    <th>Status</th>
                  </tr>
                </thead>

                <tbody>
                  {anomalies.map(
                    (anomaly, index) => (
                      <tr key={index}>
                        <td>{anomaly.date}</td>

                        <td>{anomaly.category}</td>

                        <td>
                          {money(anomaly.amount)}
                        </td>

                        <td>
                          <span className="anomaly-badge">
                            Unusual
                          </span>
                        </td>
                      </tr>
                    )
                  )}
                </tbody>
              </table>
            </div>
          ) : (
            <div className="empty-state">
              No unusual transactions detected.
            </div>
          )}
        </section>

        {/* ========================================= */}
        {/* ALL EXPENSES */}
        {/* ========================================= */}

        <section className="panel">
          <div className="section-heading">
            <div>
              <p className="ai-label">TRANSACTIONS</p>

              <h2>All Expenses</h2>

              <p>
                Manage your complete expense history.
              </p>
            </div>
          </div>

          {filteredExpenses.length > 0 ? (
            <div className="table-wrapper">
              <table className="expense-table">
                <thead>
                  <tr>
                    <th>Date</th>
                    <th>Category</th>
                    <th>Amount</th>
                    <th>Actions</th>
                  </tr>
                </thead>

                <tbody>
                  {filteredExpenses.map(
                    (expense) => (
                      <tr key={expense.id}>
                        <td>{expense.date}</td>

                        <td>
                          <span className="category-pill">
                            {expense.category}
                          </span>
                        </td>

                        <td className="amount-cell">
                          {money(expense.amount)}
                        </td>

                        <td>
                          <div className="action-buttons">
                            <button
                              className="edit-button"
                              onClick={() =>
                                openEdit(expense)
                              }
                            >
                              Edit
                            </button>

                            <button
                              className="delete-button"
                              onClick={() =>
                                handleDelete(
                                  expense.id
                                )
                              }
                            >
                              Delete
                            </button>
                          </div>
                        </td>
                      </tr>
                    )
                  )}
                </tbody>
              </table>
            </div>
          ) : (
            <div className="empty-state">
              No expenses found.
            </div>
          )}
        </section>

        {/* ========================================= */}
        {/* FOOTER */}
        {/* ========================================= */}

        <footer className="footer">
          <div className="brand">
            SmartSpend<span>AI</span>
          </div>

          <p>
            AI-powered personal finance intelligence
            system.
          </p>

          <span>
            Built with Next.js + FastAPI + Machine
            Learning
          </span>
        </footer>
      </div>

      {/* =========================================== */}
      {/* EDIT MODAL */}
      {/* =========================================== */}

      {editingExpense && (
        <div className="modal-overlay">
          <div className="edit-modal">

            <div className="modal-header">
              <div>
                <p className="ai-label">EDIT</p>

                <h2>Edit Expense</h2>
              </div>

              <button
                className="close-button"
                onClick={() =>
                  setEditingExpense(null)
                }
              >
                ×
              </button>
            </div>

            <form onSubmit={handleUpdate}>
              <div className="form-group">
                <label>Date</label>

                <input
                  type="date"
                  value={editingExpense.date}
                  onChange={(e) =>
                    setEditingExpense({
                      ...editingExpense,
                      date: e.target.value,
                    })
                  }
                />
              </div>

              <div className="form-group">
                <label>Category</label>

                <select
                  value={editingExpense.category}
                  onChange={(e) =>
                    setEditingExpense({
                      ...editingExpense,
                      category: e.target.value,
                    })
                  }
                >
                  <option value="Food">Food</option>

                  <option value="Travel">
                    Travel
                  </option>

                  <option value="Shopping">
                    Shopping
                  </option>

                  <option value="Bills">
                    Bills
                  </option>

                  <option value="Entertainment">
                    Entertainment
                  </option>

                  <option value="Education">
                    Education
                  </option>

                  <option value="Health">
                    Health
                  </option>

                  <option value="Other">
                    Other
                  </option>
                </select>
              </div>

              <div className="form-group">
                <label>Amount</label>

                <input
                  type="number"
                  min="1"
                  step="0.01"
                  value={editingExpense.amount}
                  onChange={(e) =>
                    setEditingExpense({
                      ...editingExpense,
                      amount: Number(
                        e.target.value
                      ),
                    })
                  }
                />
              </div>

              <div className="modal-actions">
                <button
                  type="button"
                  className="secondary-button"
                  onClick={() =>
                    setEditingExpense(null)
                  }
                >
                  Cancel
                </button>

                <button
                  type="submit"
                  className="primary-button"
                >
                  Save Changes
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </main>
  );
}