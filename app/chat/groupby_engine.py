import pandas as pd


def compute_groupby(df: pd.DataFrame, value_col: str, group_col: str, agg: str):

    if value_col not in df.columns or group_col not in df.columns:
        return None

    data = df[[group_col, value_col]].copy()

    data[value_col] = pd.to_numeric(data[value_col], errors="coerce")
    data = data.dropna(subset=[value_col])

    if data.empty:
        return None

    if agg in ["average", "mean"]:
        result = data.groupby(group_col)[value_col].mean()
    elif agg == "max":
        result = data.groupby(group_col)[value_col].max()
    elif agg == "min":
        result = data.groupby(group_col)[value_col].min()
    elif agg == "sum":
        result = data.groupby(group_col)[value_col].sum()
    else:
        return None

    return result.reset_index()