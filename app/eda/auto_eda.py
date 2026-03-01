import pandas as pd
import numpy as np

def auto_eda(df: pd.DataFrame):

    result = {}

    numeric_df = df.select_dtypes(include=np.number)

    if numeric_df.shape[1] > 1:
        corr = numeric_df.corr()
        result["correlations"] = corr.round(3).to_dict()
    else:
        result["correlations"] = {}

    distributions = {}
    for col in numeric_df.columns:
        distributions[col] = {
            "mean": float(numeric_df[col].mean()),
            "median": float(numeric_df[col].median()),
            "std": float(numeric_df[col].std())
        }

    result["distributions"] = distributions

    return result
