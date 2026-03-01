# app/chat/aggregator.py

import pandas as pd


def compute_aggregation(df: pd.DataFrame, column: str, agg: str):

    if column not in df.columns:
        return None

    if agg == "average":
        return round(float(df[column].mean()), 3)

    if agg == "max":
        return round(float(df[column].max()), 3)

    if agg == "min":
        return round(float(df[column].min()), 3)

    if agg == "sum":
        return round(float(df[column].sum()), 3)

    return None
