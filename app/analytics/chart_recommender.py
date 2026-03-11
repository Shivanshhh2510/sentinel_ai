import pandas as pd


def recommend_charts(df):

    charts = []

    if df is None or df.empty:
        return {
            "type": "text",
            "answer": "Dataset is empty."
        }

    numeric_cols = [
        c for c in df.select_dtypes(include="number").columns
        if "id" not in c.lower()
    ]

    categorical_cols = df.select_dtypes(include="object").columns.tolist()

    date_cols = [
        c for c in df.columns
        if "date" in c.lower()
    ]

    # -----------------------------------
    # Chart 1 — Category vs Metric
    # -----------------------------------

    if numeric_cols and categorical_cols:

        metric = numeric_cols[0]
        category = categorical_cols[0]

        agg = (
            df.groupby(category)[metric]
            .sum()
            .reset_index()
            .sort_values(metric, ascending=False)
        )

        charts.append({
            "chart_type": "bar",
            "title": f"{metric} by {category}",
            "x": category,
            "y": metric,
            "data": agg.to_dict(orient="records")
        })

    # -----------------------------------
    # Chart 2 — Trend
    # -----------------------------------

    if numeric_cols and date_cols:

        metric = numeric_cols[0]
        date_col = date_cols[0]

        df_temp = df.copy()
        df_temp[date_col] = pd.to_datetime(df_temp[date_col], errors="coerce")

        trend = (
            df_temp.groupby(date_col)[metric]
            .sum()
            .reset_index()
            .sort_values(date_col)
        )

        charts.append({
            "chart_type": "line",
            "title": f"{metric} trend",
            "x": date_col,
            "y": metric,
            "data": trend.to_dict(orient="records")
        })

    # -----------------------------------
    # Chart 3 — Correlation
    # -----------------------------------

    if len(numeric_cols) >= 2:

        col1 = numeric_cols[0]
        col2 = numeric_cols[1]

        charts.append({
            "chart_type": "scatter",
            "title": f"{col1} vs {col2}",
            "x": col1,
            "y": col2,
            "data": df[[col1, col2]].to_dict(orient="records")
        })

    return {
        "type": "chart_recommendations",
        "charts": charts
    }