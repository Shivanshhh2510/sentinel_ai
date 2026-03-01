import pandas as pd
from app.ingestion.csv_loader import get_current_df
from app.ai.copilot_brain import analyze_question
from app.ingestion.csv_loader import get_current_df



# ======================================
# HELPER: TOP N AGGREGATION
# ======================================

def top_n(df, group_col, value_col, n=10):

    result = (
        df.groupby(group_col)[value_col]
        .sum()
        .sort_values(ascending=False)
        .head(n)
        .reset_index()
    )

    return result.to_dict(orient="records")


# ======================================
# SALES BY CATEGORY
# ======================================

def sales_by_category(df):

    if "category" in df.columns and "sales" in df.columns:

        data = top_n(df, "category", "sales")

        return {
            "chart_type": "bar",
            "title": "Sales by Category",
            "x": "category",
            "y": "sales",
            "data": data
        }

    return None


# ======================================
# SALES BY REGION
# ======================================

def sales_by_region(df):

    if "region" in df.columns and "sales" in df.columns:

        data = top_n(df, "region", "sales")

        return {
            "chart_type": "bar",
            "title": "Sales by Region",
            "x": "region",
            "y": "sales",
            "data": data
        }

    return None


# ======================================
# PROFIT BY CATEGORY
# ======================================

def profit_by_category(df):

    if "category" in df.columns and "profit" in df.columns:

        data = top_n(df, "category", "profit")

        return {
            "chart_type": "bar",
            "title": "Profit by Category",
            "x": "category",
            "y": "profit",
            "data": data
        }

    return None


# ======================================
# MONTHLY SALES TREND
# ======================================

def monthly_sales(df):

    if "order_date" in df.columns and "sales" in df.columns:

        try:

            df["order_date"] = pd.to_datetime(df["order_date"])

            df["month"] = df["order_date"].dt.to_period("M").astype(str)

            result = (
                df.groupby("month")["sales"]
                .sum()
                .reset_index()
            )

            return {
                "chart_type": "line",
                "title": "Monthly Sales Trend",
                "x": "month",
                "y": "sales",
                "data": result.to_dict(orient="records")
            }

        except Exception:
            return None

    return None


# ======================================
# QUESTION AWARE CHART GENERATION
# ======================================

def generate_charts_for_question(question: str):

    df = get_current_df()

    if df is None or df.empty:
        return []

    q = question.lower()

    charts = []

    try:

        # --------------------------------
        # SALES BY REGION
        # --------------------------------

        if "region" in q and "sales" in q:

            chart = sales_by_region(df.copy())

            if chart:
                charts.append(chart)

        # --------------------------------
        # SALES BY CATEGORY
        # --------------------------------

        elif "category" in q and "sales" in q:

            chart = sales_by_category(df.copy())

            if chart:
                charts.append(chart)

        # --------------------------------
        # PROFIT BY CATEGORY
        # --------------------------------

        elif "category" in q and "profit" in q:

            chart = profit_by_category(df.copy())

            if chart:
                charts.append(chart)

        # --------------------------------
        # SALES TREND
        # --------------------------------

        elif "trend" in q or "monthly" in q:

            chart = monthly_sales(df.copy())

            if chart:
                charts.append(chart)

    except Exception:
        return []

    return charts


# ======================================
# GENERATE ALL CHARTS (EXISTING SYSTEM)
# ======================================

def generate_charts():

    df = get_current_df()

    if df is None:
        return []

    charts = []

    generators = [
        sales_by_category,
        sales_by_region,
        profit_by_category,
        monthly_sales
    ]

    for fn in generators:

        try:

            chart = fn(df.copy())

            if chart:
                charts.append(chart)

        except Exception:
            continue

    return charts

# ======================================
# DYNAMIC CHART GENERATOR
# ======================================

def generate_dynamic_chart(question: str):

    df = get_current_df()

    if df is None:
        return None

    brain = analyze_question(question)

    metric = brain.get("metric")
    group_by = brain.get("group_by")
    chart_type = brain.get("chart")

    # allow charts that don't require metric
    if chart_type != "heatmap":
        if metric not in df.columns:
            return None

    # ======================================
    # BAR CHART
    # ======================================

    if chart_type == "bar" and group_by and group_by in df.columns:

        result = (
            df.groupby(group_by)[metric]
            .sum()
            .reset_index()
            .sort_values(metric, ascending=False)
        )

        return {
            "chart_type": "bar",
            "title": f"{metric.title()} by {group_by.title()}",
            "x": group_by,
            "y": metric,
            "data": result.to_dict(orient="records")
        }

    # ======================================
    # LINE CHART (TREND)
    # ======================================

    elif chart_type == "line":

        if "order_date" in df.columns:

            df["order_date"] = pd.to_datetime(df["order_date"], errors="coerce")

            df["month"] = df["order_date"].dt.to_period("M").astype(str)

            result = (
                df.groupby("month")[metric]
                .sum()
                .reset_index()
            )

            return {
                "chart_type": "line",
                "title": f"{metric.title()} Trend",
                "x": "month",
                "y": metric,
                "data": result.to_dict(orient="records")
            }

    # ======================================
    # HISTOGRAM
    # ======================================

    elif chart_type == "histogram":

        return {
            "chart_type": "histogram",
            "title": f"{metric.title()} Distribution",
            "x": metric,
            "data": df[[metric]].to_dict(orient="records")
        }

    # ======================================
    # SCATTER
    # ======================================

    elif chart_type == "scatter":

        cols = ["sales", "profit"]

        if all(c in df.columns for c in cols):

            return {
                "chart_type": "scatter",
                "title": "Sales vs Profit",
                "x": "sales",
                "y": "profit",
                "data": df[cols].to_dict(orient="records")
            }

    # ======================================
    # BOX PLOT
    # ======================================

    elif chart_type == "box":

        if group_by and group_by in df.columns:

            return {
                "chart_type": "box",
                "title": f"{metric.title()} Distribution by {group_by.title()}",
                "x": group_by,
                "y": metric,
                "data": df[[group_by, metric]].to_dict(orient="records")
            }

    # ======================================
    # PIE CHART
    # ======================================

    elif chart_type == "pie":

        if group_by and group_by in df.columns:

            result = (
                df.groupby(group_by)[metric]
                .sum()
                .reset_index()
            )

            return {
                "chart_type": "pie",
                "title": f"{metric.title()} Share by {group_by.title()}",
                "names": group_by,
                "values": metric,
                "data": result.to_dict(orient="records")
            }

    # ======================================
    # AREA CHART
    # ======================================

    elif chart_type == "area":

        if "order_date" not in df.columns:
            return None

        df["order_date"] = pd.to_datetime(df["order_date"])
        df["month"] = df["order_date"].dt.to_period("M").astype(str)

        result = (
            df.groupby("month")[metric]
            .sum()
            .cumsum()
            .reset_index()
        )

        return {
            "chart_type": "area",
            "title": f"Cumulative {metric.title()}",
            "x": "month",
            "y": metric,
            "data": result.to_dict(orient="records")
        }

    # ======================================
    # HEATMAP
    # ======================================

    elif chart_type == "heatmap":

        # select numeric columns only
        numeric_df = df.select_dtypes(include="number")

        # need at least 2 numeric columns for correlation
        if numeric_df.shape[1] < 2:
            return None

        # compute correlation matrix
        corr = numeric_df.corr()

        # convert matrix to long format
        heatmap_data = (
            corr
            .reset_index()
            .melt(id_vars="index")
        )

        heatmap_data.columns = ["x", "y", "value"]

        return {
            "chart_type": "heatmap",
            "title": "Correlation Heatmap",
            "x": "x",
            "y": "y",
            "z": "value",
            "data": heatmap_data.to_dict(orient="records")
        }

    return None