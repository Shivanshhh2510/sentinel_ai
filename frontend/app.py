import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from io import BytesIO
import uuid
import sqlite3
import json
import os

# ============================
# CONFIG
# ============================

BACKEND_URL = "http://127.0.0.1:8000"
DB_PATH = "storage/sentinelai.db"

st.set_page_config(
    page_title="SentinelAI",
    page_icon="🧠",
    layout="wide"
)

# ============================
# AUTH SESSION
# ============================

if "token" not in st.session_state:
    st.session_state.token = None

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False


def auth_headers():
    return {"Authorization": f"Bearer {st.session_state.token}"}


def require_login():
    if not st.session_state.logged_in:
        st.warning("Please login first.")
        st.stop()


# ============================
# DATABASE
# ============================

def init_db():
    os.makedirs("storage", exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS dashboards (
        name TEXT PRIMARY KEY,
        charts_json TEXT
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS chat_history (
        id INTEGER PRIMARY KEY,
        messages_json TEXT
    )
    """)

    conn.commit()
    conn.close()


def load_dashboards():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT name, charts_json FROM dashboards")
    rows = c.fetchall()
    conn.close()

    dashboards = {}
    for name, charts in rows:
        dashboards[name] = json.loads(charts)

    return dashboards


def save_dashboards(dashboards):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    for name, charts in dashboards.items():
        c.execute(
            "INSERT OR REPLACE INTO dashboards VALUES (?,?)",
            (name, json.dumps(charts))
        )

    conn.commit()
    conn.close()


def load_chat():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT messages_json FROM chat_history WHERE id=1")
    row = c.fetchone()
    conn.close()

    if row:
        return json.loads(row[0])
    return []


def save_chat(messages):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        "INSERT OR REPLACE INTO chat_history VALUES (?,?)",
        (1, json.dumps(messages))
    )
    conn.commit()
    conn.close()


init_db()

# ============================
# SESSION STATE
# ============================

if "dashboards" not in st.session_state:
    st.session_state.dashboards = load_dashboards()

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "chat_loaded" not in st.session_state:
    st.session_state.chat_history = load_chat()
    st.session_state.chat_loaded = True

if "last_plot" not in st.session_state:
    st.session_state.last_plot = None

# ============================
# HEADER
# ============================

st.title("🧠 SentinelAI – Automated Business Intelligence")

tabs = st.tabs([
    "🔐 Login / Register",
    "📂 Upload Dataset",
    "🤖 AI Data Copilot",
    "📊 Dashboard Builder"
])

# ============================
# TAB 0 — LOGIN / REGISTER
# ============================

with tabs[0]:

    mode = st.radio("Select Mode", ["Login", "Register"], horizontal=True)

    if st.session_state.logged_in:
        st.success("Already logged in.")
    else:
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")

        if mode == "Register":
            confirm_password = st.text_input("Confirm Password", type="password")

            if st.button("Register"):

                if password != confirm_password:
                    st.error("Passwords do not match.")
                else:
                    r = requests.post(
                        f"{BACKEND_URL}/auth/register",
                        json={"email": email, "password": password}
                    )

                    if r.status_code == 200:
                        st.success("Registration successful. You can now login.")
                    else:
                        st.error("Registration failed.")

        else:
            if st.button("Login"):
                r = requests.post(
                    f"{BACKEND_URL}/auth/login",
                    data={"username": email, "password": password}
                )

                if r.status_code == 200:
                    data = r.json()
                    st.session_state.token = data["access_token"]
                    st.session_state.logged_in = True
                    st.success("Logged in successfully!")
                    st.rerun()
                else:
                    st.error("Invalid credentials")

# ============================
# TAB 1 — UPLOAD DATASET
# ============================

# ============================
# TAB 1 — DATASET UPLOAD & AUTOML
# ============================

with tabs[1]:

    require_login()

    st.subheader("Upload CSV or Excel Dataset")
    file = st.file_uploader("Upload File", type=["csv", "xlsx"])

    if file:
        data = file.read()
        buf = BytesIO(data)

        if file.name.endswith(".csv"):

            # SAFE CSV LOADING (FIX FOR KAGGLE DATASETS)
            try:
                df = pd.read_csv(buf)
            except:
                buf.seek(0)
                df = pd.read_csv(buf, encoding="latin1")

        else:
            df = pd.read_excel(buf)

        st.dataframe(df, width="stretch")
        st.success(f"Dataset loaded: {df.shape[0]} rows × {df.shape[1]} columns")

        if st.button("🚀 Train Model"):

            r = requests.post(
                f"{BACKEND_URL}/ingest/csv",
                files={"file": (file.name, data, file.type)},
                headers=auth_headers()
            )

            if r.status_code == 200:
                s = r.json()["summary"]

                st.success("Model Trained")

                # ============================
                # DATASET OVERVIEW
                # ============================

                st.subheader("Dataset Overview")

                col1, col2, col3 = st.columns(3)

                col1.metric("Rows", s.get("rows"))
                col2.metric("Target Column", s.get("target_column"))
                col3.metric("Problem Type", s.get("problem_type", "Auto"))

                # Target Detection Explanation
                if "target_reason" in s:
                    st.info(f"Target Detection Reason: {s.get('target_reason')}")

                st.divider()

                # ============================
                # DATASET STRUCTURE
                # ============================

                if "profile" in s:

                    profile = s["profile"]

                    st.subheader("Dataset Structure")

                    c1, c2, c3, c4 = st.columns(4)

                    c1.metric(
                        "Numeric Columns",
                        len(profile.get("numeric_columns", []))
                    )

                    c2.metric(
                        "Categorical Columns",
                        len(profile.get("categorical_columns", []))
                    )

                    c3.metric(
                        "Date Columns",
                        len(profile.get("datetime_columns", []))
                    )

                    c4.metric(
                        "Identifier Columns",
                        len(profile.get("identifier_columns", []))
                    )

                    st.divider()

                    # ============================
                    # DATA QUALITY SIGNALS
                    # ============================

                    st.subheader("Data Quality Signals")

                    q1, q2, q3 = st.columns(3)

                    q1.metric(
                        "Columns with Missing Values",
                        len(profile.get("missing_values", {}))
                    )

                    q2.metric(
                        "Duplicate Rows",
                        profile.get("duplicate_rows", 0)
                    )

                    q3.metric(
                        "High Cardinality Columns",
                        len(profile.get("high_cardinality_columns", []))
                    )

                    st.divider()

                    # ============================
                    # SENTINELAI DATASET INTELLIGENCE (NEW)
                    # ============================

                    st.subheader("SentinelAI Dataset Intelligence")

                    numeric_count = len(profile.get("numeric_columns", []))
                    categorical_count = len(profile.get("categorical_columns", []))
                    datetime_count = len(profile.get("datetime_columns", []))
                    identifier_cols = profile.get("identifier_columns", [])
                    missing_cols = profile.get("missing_values", {})
                    high_card_cols = profile.get("high_cardinality_columns", [])

                    summary_text = f"""
SentinelAI automatically analyzed the dataset structure.

• **{numeric_count} numeric variables** detected
• **{categorical_count} categorical variables** detected
• **{datetime_count} datetime variables** detected

The system detected **{len(identifier_cols)} identifier-like columns**, which may not carry predictive signal.

**{len(high_card_cols)} high-cardinality columns** were found and may impact model generalization.

**{len(missing_cols)} columns contain missing values** that could influence model performance.

Based on the dataset structure, SentinelAI identified this as a **{s.get("problem_type")} problem** and selected **{s.get("target_column")}** as the prediction target.
"""

                    st.info(summary_text)

                    # ============================
                    # DATA RISK WARNINGS
                    # ============================

                    if high_card_cols:

                        st.warning(
                            "High Cardinality Columns Detected: "
                            + ", ".join(high_card_cols[:5])
                        )

                    if identifier_cols:

                        st.warning(
                            "Identifier-like Columns Detected: "
                            + ", ".join(identifier_cols[:5])
                        )

                    st.divider()

                # ============================
                # BEST MODEL
                # ============================

                st.subheader("Best Model")

                st.metric("Model", s.get("best_model"))
                st.metric("Best Score", s.get("best_score"))

                st.divider()

                # ============================
                # MODEL COMPARISON
                # ============================

                if "model_scores" in s:

                    scores = s["model_scores"]

                    score_df = pd.DataFrame({
                        "Model": list(scores.keys()),
                        "Score": list(scores.values())
                    })

                    st.subheader("Model Comparison")

                    fig = px.bar(
                        score_df,
                        x="Model",
                        y="Score",
                        color="Model"
                    )

                    st.plotly_chart(fig, width="stretch")

                st.divider()

                # ============================
                # FEATURE IMPORTANCE
                # ============================

                if "top_features" in s:

                    st.subheader("Top Feature Drivers")

                    fi_df = pd.DataFrame({
                        "Feature": list(s["top_features"].keys()),
                        "Importance": list(s["top_features"].values())
                    })

                    fig2 = px.bar(
                        fi_df,
                        x="Importance",
                        y="Feature",
                        orientation="h"
                    )

                    st.plotly_chart(fig2, width="stretch")

                # ============================
                # AI SUMMARY
                # ============================

                if "ai_summary" in s:

                    st.divider()
                    st.subheader("AI Interpretation")
                    st.success(s["ai_summary"])

                # ============================
                # AI CHART RECOMMENDATIONS
                # ============================

                st.divider()
                st.subheader("AI Recommended Visualizations")

                try:

                    r = requests.get(
                        f"{BACKEND_URL}/analytics/charts",
                        headers=auth_headers()
                    )

                    if r.status_code == 200:

                        charts = r.json()["charts"]

                        for chart in charts:

                            if "data" not in chart:
                                continue

                            df_chart = pd.DataFrame(chart["data"])

                            if chart["chart_type"] == "bar":

                                fig = px.bar(
                                    df_chart,
                                    x=chart["x"],
                                    y=chart["y"],
                                    title=chart["title"]
                                )

                            elif chart["chart_type"] == "line":

                                fig = px.line(
                                    df_chart,
                                    x=chart["x"],
                                    y=chart["y"],
                                    title=chart["title"]
                                )

                            else:
                                continue

                            st.plotly_chart(fig, width="stretch")

                            st.session_state.last_plot = chart

                except Exception:
                    pass

# ============================
# TAB 2 — AI DATA COPILOT
# ============================

with tabs[2]:

    require_login()

    st.subheader("Ask Questions About Your Data")

    st.info(
        "Ask SentinelAI questions about your data. Example: "
        "'Show sales by region' or 'Which category has highest profit?'"
    )

    st.markdown("**Example questions:**")
    st.caption("• Show sales by region")
    st.caption("• Which category has highest profit")
    st.caption("• Show sales trend over time")
    st.caption("• Show profit distribution")

    question = st.text_input("Ask a business question")

    if st.button("Ask Copilot") and question:

        with st.spinner("SentinelAI is analyzing your data..."):

            r = requests.post(
                f"{BACKEND_URL}/copilot/ask",
                json={"question": question},
                headers=auth_headers()
            )

            if r.status_code == 200:

                data = r.json()["copilot_response"]

                message = {
                    "question": question,
                    "answer": data.get("answer"),
                    "analysis": data.get("analysis"),
                    "charts": data.get("charts"),
                    "insights": data.get("insights"),
                    "suggestions": data.get("suggestions")
                }

                st.session_state.chat_history.append(message)
                save_chat(st.session_state.chat_history)

    # ============================
    # DISPLAY CHAT HISTORY
    # ============================

    if st.button("🗑 Clear Chat"):
        st.session_state.chat_history = []
        save_chat([])
        st.rerun()

    if len(st.session_state.chat_history) == 0:
        st.info("Ask your first question.")
    else:

        for msg in reversed(st.session_state.chat_history):

            st.markdown("**User Question:**")
            st.write(msg.get("question", "Unknown question"))


            answer = msg.get("answer")
            if answer:
                st.success(answer)

            analysis = msg.get("analysis")

            if analysis:
                st.info(analysis)

            charts = msg.get("charts")

            if charts:

                st.markdown("### Visual Insights")

                for chart in charts:

                    if "data" not in chart:
                        continue

                    df_chart = pd.DataFrame(chart["data"])

                    if chart["chart_type"] == "bar":

                        fig = px.bar(
                            df_chart,
                            x=chart["x"],
                            y=chart["y"],
                            title=chart["title"]
                        )

                    elif chart["chart_type"] == "line":

                        fig = px.line(
                            df_chart,
                            x=chart["x"],
                            y=chart["y"],
                            title=chart["title"]
                        )

                    # ======================================
                    # HISTOGRAM
                    # ======================================

                    elif chart["chart_type"] == "histogram":

                        fig = px.histogram(
                            df_chart,
                            x=chart["x"],
                            title=chart["title"]
                        )

                    # ======================================
                    # SCATTER
                    # ======================================

                    elif chart["chart_type"] == "scatter":

                        fig = px.scatter(
                            df_chart,
                            x=chart["x"],
                            y=chart["y"],
                            title=chart["title"]
                        )

                    # ======================================
                    # BOX PLOT
                    # ======================================

                    elif chart["chart_type"] == "box":

                        fig = px.box(
                            df_chart,
                            x=chart["x"],
                            y=chart["y"],
                            title=chart["title"]
                        )

                    # ======================================
                    # PIE
                    # ======================================

                    elif chart["chart_type"] == "pie":

                        fig = px.pie(
                            df_chart,
                            names=chart["names"],
                            values=chart["values"],
                            title=chart["title"]
                        )

                    # ======================================
                    # AREA
                    # ======================================

                    elif chart["chart_type"] == "area":

                        fig = px.area(
                            df_chart,
                            x=chart["x"],
                            y=chart["y"],
                            title=chart["title"]
                        )

                    # ======================================
                    # HEATMAP
                    # ======================================

                    elif chart["chart_type"] == "heatmap":

                        pivot = df_chart.pivot(
                            index=chart["y"],
                            columns=chart["x"],
                            values=chart["z"]
                        )

                        fig = px.imshow(
                            pivot,
                            text_auto=True,
                            aspect="auto",
                            title=chart["title"]
                        )

                    else:
                        continue

                    st.plotly_chart(
                        fig,
                        width="stretch",
                        key=f"chat_chart_{msg.get('question','q')}_{chart['title']}_{id(chart)}"
                    )

                    st.session_state.last_plot = chart

            insights = msg.get("insights")

            if insights:

                st.markdown("### AI Insights")

                for insight in insights:
                    st.info(insight)


            # ======================================
            # SUGGESTED QUESTIONS
            # ======================================

            suggestions = msg.get("suggestions")

            if suggestions:

                st.markdown("### Suggested Questions")

                for s in suggestions:
                    st.markdown(f"- {s}")



# ============================
# TAB 3 — DASHBOARD BUILDER
# ============================

with tabs[3]:

    require_login()

    st.subheader("Dashboard Builder")

    if st.session_state.last_plot is None:
        st.info("Generate a chart using the AI Copilot first.")
    else:

        dashboards = list(st.session_state.dashboards.keys())
        selected = st.selectbox("Add to existing dashboard", ["--select--"] + dashboards)
        new_name = st.text_input("Or create new dashboard")

        if st.button("➕ Add Chart"):

            name = new_name if new_name else selected

            if name and name != "--select--":

                if name not in st.session_state.dashboards:
                    st.session_state.dashboards[name] = []

                st.session_state.dashboards[name].append(st.session_state.last_plot)
                save_dashboards(st.session_state.dashboards)
                st.success(f"Added to dashboard: {name}")

    st.divider()

    if len(st.session_state.dashboards) == 0:
        st.info("No dashboards created yet.")
    else:

        st.subheader("Saved Dashboards")

        for name, charts in st.session_state.dashboards.items():

            st.markdown(f"### {name}")

            for chart in charts:

                if "data" not in chart:
                    continue

                df_chart = pd.DataFrame(chart["data"])

                if chart["chart_type"] == "bar":

                    fig = px.bar(
                        df_chart,
                        x=chart["x"],
                        y=chart["y"],
                        title=chart["title"]
                    )

                elif chart["chart_type"] == "line":

                    fig = px.line(
                        df_chart,
                        x=chart["x"],
                        y=chart["y"],
                        title=chart["title"]
                    )

                # ======================================
                # HISTOGRAM
                # ======================================

                elif chart["chart_type"] == "histogram":

                    fig = px.histogram(
                        df_chart,
                        x=chart["x"],
                        title=chart["title"]
                    )

                # ======================================
                # SCATTER
                # ======================================

                elif chart["chart_type"] == "scatter":

                    fig = px.scatter(
                        df_chart,
                        x=chart["x"],
                        y=chart["y"],
                        title=chart["title"]
                    )

                # ======================================
                # BOX PLOT
                # ======================================

                elif chart["chart_type"] == "box":

                    fig = px.box(
                        df_chart,
                        x=chart["x"],
                        y=chart["y"],
                        title=chart["title"]
                    )

                # ======================================
                # PIE
                # ======================================

                elif chart["chart_type"] == "pie":

                    fig = px.pie(
                        df_chart,
                        names=chart["names"],
                        values=chart["values"],
                        title=chart["title"]
                    )

                # ======================================
                # AREA
                # ======================================

                elif chart["chart_type"] == "area":

                    fig = px.area(
                        df_chart,
                        x=chart["x"],
                        y=chart["y"],
                        title=chart["title"]
                    )

                # ======================================
                # HEATMAP
                # ======================================

                elif chart["chart_type"] == "heatmap":

                    pivot = df_chart.pivot(
                        index=chart["y"],
                        columns=chart["x"],
                        values=chart["z"]
                    )

                    fig = px.imshow(
                        pivot,
                        text_auto=True,
                        aspect="auto",
                        title=chart["title"]
                    )

                else:
                    continue

                st.plotly_chart(
                    fig,
                    width="stretch",
                    key=f"dashboard_chart_{name}_{chart['title']}_{id(chart)}"
                )

st.divider()
st.caption("SentinelAI — AI Data Copilot for Automated Business Intelligence")