import pandas as pd


def discover_insights(df):

    insights = []
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

    # -----------------------------------
    # Insight 1 — Top category contribution
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

        top_row = agg.iloc[0]

        insights.append(
            f"Top {category}: {top_row[category]} with total {metric} of {round(top_row[metric],2)}"
        )

    # -----------------------------------
    # Insight 2 — Distribution check
    # -----------------------------------

    if numeric_cols:

        metric = numeric_cols[0]

        avg = df[metric].mean()
        max_val = df[metric].max()
        min_val = df[metric].min()

        insights.append(
            f"{metric} ranges from {round(min_val,2)} to {round(max_val,2)} with an average of {round(avg,2)}."
        )

    return {
        "type": "discovery",
        "insights": insights,
        "charts": charts
    }