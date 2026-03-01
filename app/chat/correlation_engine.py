# app/chat/correlation_engine.py

import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression


def classify_strength(corr_value):

    abs_corr = abs(corr_value)

    if abs_corr < 0.3:
        return "Weak relationship"
    elif abs_corr < 0.6:
        return "Moderate relationship"
    else:
        return "Strong relationship"


def generate_correlation_analysis(df, metric_x, metric_y):

    if metric_x not in df.columns or metric_y not in df.columns:
        return None

    if not np.issubdtype(df[metric_x].dtype, np.number):
        return None

    if not np.issubdtype(df[metric_y].dtype, np.number):
        return None

    clean_df = df[[metric_x, metric_y]].dropna()

    if len(clean_df) < 3:
        return None

    correlation = clean_df[metric_x].corr(clean_df[metric_y])
    strength = classify_strength(correlation)

    direction = (
        "Positive correlation detected."
        if correlation > 0
        else "Negative correlation detected."
    )

    # Regression for visualization
    X = clean_df[[metric_x]].values
    y = clean_df[metric_y].values

    model = LinearRegression()
    model.fit(X, y)

    predicted = model.predict(X)

    insight = f"""
Correlation Intelligence:

• Correlation Coefficient: {round(correlation,3)}
• {strength}
• {direction}

Executive Interpretation:
Changes in {metric_x} appear to {'increase' if correlation > 0 else 'decrease'} {metric_y}.
Strategic decisions should evaluate causal drivers before acting on this relationship.
"""

    return {
        "correlation": round(correlation, 3),
        "strength": strength,
        "direction": direction,
        "x": clean_df[metric_x].tolist(),
        "y": clean_df[metric_y].tolist(),
        "predicted": predicted.tolist(),
        "insight": insight
    }