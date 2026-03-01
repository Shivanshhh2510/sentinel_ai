import pandas as pd

from app.ingestion.csv_loader import get_current_df


# ==============================
# QUERY TYPE DETECTION
# ==============================

def is_analytical_query(query: str) -> bool:
    """
    Detect if query requires dataset computation
    """

    query = query.lower()

    keywords = [
        "highest",
        "lowest",
        "average",
        "total",
        "sum",
        "count",
        "maximum",
        "minimum",
        "top",
        "trend",
        "group",
        "distribution",
        "sales",
        "profit"
    ]

    return any(word in query for word in keywords)


# ==============================
# COLUMN DETECTION
# ==============================

def detect_column(query: str, df: pd.DataFrame):

    query = query.lower()

    for col in df.columns:
        if col.lower() in query:
            return col

    return None


# ==============================
# REGION SALES ANALYSIS
# ==============================

def highest_sales_by_region(df):

    if "region" not in df.columns or "sales" not in df.columns:
        return None

    result = (
        df.groupby("region")["sales"]
        .sum()
        .sort_values(ascending=False)
    )

    return result


# ==============================
# SALES BY CATEGORY
# ==============================

def sales_by_category(df):

    if "category" not in df.columns or "sales" not in df.columns:
        return None

    result = (
        df.groupby("category")["sales"]
        .sum()
        .sort_values(ascending=False)
    )

    return result


# ==============================
# TOP PRODUCTS BY PROFIT
# ==============================

def top_products_by_profit(df, top_n=5):

    if "product_name" not in df.columns or "profit" not in df.columns:
        return None

    result = (
        df.groupby("product_name")["profit"]
        .sum()
        .sort_values(ascending=False)
        .head(top_n)
    )

    return result


# ==============================
# TOP CITIES BY SALES
# ==============================

def top_cities_by_sales(df, top_n=10):

    if "city" not in df.columns or "sales" not in df.columns:
        return None

    result = (
        df.groupby("city")["sales"]
        .sum()
        .sort_values(ascending=False)
        .head(top_n)
    )

    return result


# ==============================
# SALES TREND
# ==============================

def monthly_sales_trend(df):

    if "order_date" not in df.columns or "sales" not in df.columns:
        return None

    try:

        df["order_date"] = pd.to_datetime(df["order_date"])

        result = (
            df.groupby(df["order_date"].dt.to_period("M"))["sales"]
            .sum()
        )

        result.index = result.index.astype(str)

        return result

    except Exception:
        return None


# ==============================
# ANALYTICAL ENGINE
# ==============================

def run_analytical_query(query: str):

    df = get_current_df()

    if df is None or df.empty:
        return {
            "type": "error",
            "message": "Dataset not loaded."
        }

    query_lower = query.lower()

    try:

        # -------------------------
        # Highest sales by region
        # -------------------------

        if "highest" in query_lower and "sales" in query_lower and "region" in query_lower:

            result = highest_sales_by_region(df)

            if result is None or result.empty:
                return {"type": "unknown"}

            top_region = result.index[0]
            value = round(result.iloc[0], 2)

            return {
                "type": "analytical",
                "analysis": result.to_dict(),
                "answer": f"The region with the highest total sales is **{top_region}** with sales of **{value}**."
            }

        # -------------------------
        # Average sales
        # -------------------------

        if "average" in query_lower and "sales" in query_lower:

            if "sales" not in df.columns:
                return {"type": "unknown"}

            avg_sales = round(df["sales"].mean(), 2)

            return {
                "type": "analytical",
                "answer": f"The average sales value across the dataset is **{avg_sales}**."
            }

        # -------------------------
        # Total sales
        # -------------------------

        if "total" in query_lower and "sales" in query_lower:

            if "sales" not in df.columns:
                return {"type": "unknown"}

            total_sales = round(df["sales"].sum(), 2)

            return {
                "type": "analytical",
                "answer": f"The total sales across the dataset is **{total_sales}**."
            }

        # -------------------------
        # Sales by category
        # -------------------------

        if "sales" in query_lower and "category" in query_lower:

            result = sales_by_category(df)

            if result is None or result.empty:
                return {"type": "unknown"}

            return {
                "type": "analytical",
                "analysis": result.to_dict(),
                "answer": "Here is the sales distribution by category."
            }

        # -------------------------
        # Top products by profit
        # -------------------------

        if "top" in query_lower and "profit" in query_lower:

            result = top_products_by_profit(df)

            if result is None or result.empty:
                return {"type": "unknown"}

            top_items = "\n".join(
                [f"{i+1}. {name} — Profit: {round(value,2)}"
                 for i, (name, value) in enumerate(result.items())]
            )

            return {
                "type": "analytical",
                "analysis": result.to_dict(),
                "answer": f"Top products by total profit:\n{top_items}"
            }

        # -------------------------
        # Top cities by sales
        # -------------------------

        if "top" in query_lower and "city" in query_lower:

            result = top_cities_by_sales(df)

            if result is None or result.empty:
                return {"type": "unknown"}

            return {
                "type": "analytical",
                "analysis": result.to_dict(),
                "answer": "Here are the top cities by total sales."
            }

        # -------------------------
        # Sales trend
        # -------------------------

        if "trend" in query_lower and "sales" in query_lower:

            result = monthly_sales_trend(df)

            if result is None or result.empty:
                return {"type": "unknown"}

            return {
                "type": "analytical",
                "analysis": result.to_dict(),
                "answer": "Here is the monthly sales trend."
            }

        # -------------------------
        # Fallback
        # -------------------------

        return {
            "type": "unknown"
        }

    except Exception as e:

        return {
            "type": "error",
            "message": str(e)
        }