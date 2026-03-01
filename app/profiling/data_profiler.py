import pandas as pd
import numpy as np


def profile_data(df: pd.DataFrame):

    profile = {}

    # =========================
    # BASIC INFO
    # =========================

    profile["rows"] = int(df.shape[0])
    profile["columns"] = int(df.shape[1])

    # =========================
    # COLUMN TYPE DETECTION
    # =========================

    numeric_cols = df.select_dtypes(include=np.number).columns.tolist()
    categorical_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()
    datetime_cols = df.select_dtypes(include=["datetime64"]).columns.tolist()

    profile["numeric_columns"] = numeric_cols
    profile["categorical_columns"] = categorical_cols
    profile["datetime_columns"] = datetime_cols

    profile["numeric_column_count"] = len(numeric_cols)
    profile["categorical_column_count"] = len(categorical_cols)
    profile["datetime_column_count"] = len(datetime_cols)

    # =========================
    # MISSING VALUES
    # =========================

    profile["missing_values"] = {
        col: int(df[col].isnull().sum())
        for col in df.columns
    }

    profile["total_missing_values"] = int(df.isnull().sum().sum())

    # =========================
    # DUPLICATE ROWS
    # =========================

    profile["duplicate_rows"] = int(df.duplicated().sum())

    # =========================
    # IDENTIFIER COLUMN DETECTION
    # =========================

    identifier_cols = []

    for col in df.columns:

        unique_ratio = df[col].nunique() / len(df)

        if unique_ratio > 0.95:
            identifier_cols.append(col)

    profile["identifier_columns"] = identifier_cols

    # =========================
    # HIGH CARDINALITY COLUMNS
    # =========================

    high_cardinality = []

    for col in df.columns:

        if df[col].dtype == "object":

            if df[col].nunique() > 50:
                high_cardinality.append(col)

    profile["high_cardinality_columns"] = high_cardinality

    # =========================
    # NUMERIC STATISTICS
    # =========================

    stats = {}

    for col in numeric_cols:

        try:
            stats[col] = {
                "mean": float(df[col].mean()),
                "std": float(df[col].std()),
                "min": float(df[col].min()),
                "max": float(df[col].max())
            }

        except Exception:
            continue

    profile["numeric_statistics"] = stats

    # =========================
    # DATASET SIGNALS
    # =========================

    signals = []

    if profile["duplicate_rows"] > 0:
        signals.append("duplicate_rows_detected")

    if profile["total_missing_values"] > 0:
        signals.append("missing_values_present")

    if len(high_cardinality) > 0:
        signals.append("high_cardinality_columns_detected")

    if len(identifier_cols) > 0:
        signals.append("identifier_columns_detected")

    profile["dataset_signals"] = signals

    return profile