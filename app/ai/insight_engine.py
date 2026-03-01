import pandas as pd


def generate_dataset_insights(df: pd.DataFrame):

    insights = []

    numeric_cols = df.select_dtypes(include=["int64", "float64"]).columns
    categorical_cols = df.select_dtypes(include=["object", "category"]).columns

    # =========================
    # SALES LEADER DETECTION
    # =========================

    if "sales" in df.columns:

        for col in categorical_cols:

            if df[col].nunique() <= 20:

                try:

                    grouped = df.groupby(col)["sales"].sum()

                    best = grouped.idxmax()
                    value = grouped.max()

                    insights.append(
                        f"{best} generates the highest total sales (${round(value,2)}) among {col} groups."
                    )

                    break

                except:
                    continue

    # =========================
    # PROFITABILITY INSIGHT
    # =========================

    if "profit" in df.columns:

        for col in categorical_cols:

            if df[col].nunique() <= 20:

                try:

                    grouped = df.groupby(col)["profit"].sum()

                    worst = grouped.idxmin()
                    value = grouped.min()

                    insights.append(
                        f"{worst} shows the lowest profitability (${round(value,2)}) in {col} groups."
                    )

                    break

                except:
                    continue

    # =========================
    # REGIONAL / CATEGORY DISTRIBUTION
    # =========================

    for col in categorical_cols:

        if df[col].nunique() <= 10:

            try:

                top = df[col].value_counts().idxmax()
                count = df[col].value_counts().max()

                insights.append(
                    f"{top} appears most frequently in the dataset under column '{col}' ({count} records)."
                )

                break

            except:
                continue

    # =========================
    # NUMERIC OUTLIER DETECTION
    # =========================

    for col in numeric_cols:

        try:

            mean = df[col].mean()
            max_val = df[col].max()

            if max_val > mean * 5:

                insights.append(
                    f"{col} contains extreme high values (max {round(max_val,2)} vs avg {round(mean,2)})."
                )

        except:
            continue

    # =========================
    # GENERAL GROUP INSIGHTS
    # =========================

    categorical_cols = list(categorical_cols)[:5]
    numeric_cols = list(numeric_cols)[:5]

    for cat in categorical_cols:

        if df[cat].nunique() > 20:
            continue

        for num in numeric_cols:

            try:

                grouped = df.groupby(cat)[num].mean()

                best = grouped.idxmax()
                value = grouped.max()

                insights.append(
                    f"{best} shows the highest average {num} ({round(value,2)}) within {cat} groups."
                )

            except:
                continue

    return insights[:8]