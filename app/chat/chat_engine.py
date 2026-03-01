# app/chat/chat_engine.py

import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression

from app.ingestion.csv_loader import get_current_df
from app.chat.intent_engine import detect_intent
from app.chat.planner import plan_query


# ======================================================
# MEMORY STATE
# ======================================================

LAST_RESULT_DF = None
LAST_CHART_TYPE = "bar"
LAST_TITLE = None
LAST_METRIC = None
LAST_GROUP_BY = None
LAST_AGGREGATION = None


# ======================================================
# DATE DETECTION
# ======================================================

def detect_date_column(df):
    for col in df.columns:
        if pd.api.types.is_datetime64_any_dtype(df[col]):
            return col

        if df[col].dtype == "object":
            try:
                converted = pd.to_datetime(df[col], errors="coerce")
                if converted.notna().sum() > len(df) * 0.6:
                    return col
            except:
                continue

    return None


# ======================================================
# TREND DATA BUILDER
# ======================================================

def build_trend_dataframe(df, metric, date_col):

    df_temp = df.copy()
    df_temp[date_col] = pd.to_datetime(df_temp[date_col])

    df_trend = (
        df_temp
        .groupby(date_col)[metric]
        .sum()
        .reset_index()
        .sort_values(by=date_col)
    )

    return df_trend


# ======================================================
# ADVANCED TREND INTELLIGENCE (v2)
# ======================================================

def generate_trend_analysis(df, metric, date_col):

    try:
        df_trend = build_trend_dataframe(df, metric, date_col)

        if len(df_trend) < 4:
            return ""

        y = df_trend[metric].values.reshape(-1, 1)
        X = np.arange(len(y)).reshape(-1, 1)

        model = LinearRegression()
        model.fit(X, y)

        slope = model.coef_[0][0]
        growth_pct = ((y[-1][0] - y[0][0]) / y[0][0] * 100) if y[0][0] != 0 else 0
        volatility = np.std(y) / np.mean(y)

        # -----------------------------------
        # Growth Classification
        # -----------------------------------

        if growth_pct > 25:
            growth_phase = "Rapid Expansion"
        elif growth_pct > 5:
            growth_phase = "Moderate Growth"
        elif growth_pct > -5:
            growth_phase = "Stable Phase"
        elif growth_pct > -25:
            growth_phase = "Moderate Contraction"
        else:
            growth_phase = "Severe Decline"

        # -----------------------------------
        # Volatility Classification
        # -----------------------------------

        if volatility < 0.15:
            volatility_level = "Stable Series"
        elif volatility < 0.35:
            volatility_level = "Moderate Variation"
        else:
            volatility_level = "High Instability"

        # -----------------------------------
        # Momentum Signal
        # -----------------------------------

        midpoint = len(y) // 2
        first_half = y[:midpoint]
        second_half = y[midpoint:]

        if len(first_half) > 1 and len(second_half) > 1:

            X1 = np.arange(len(first_half)).reshape(-1, 1)
            X2 = np.arange(len(second_half)).reshape(-1, 1)

            m1 = LinearRegression().fit(X1, first_half).coef_[0][0]
            m2 = LinearRegression().fit(X2, second_half).coef_[0][0]

            if m2 > m1:
                momentum = "Acceleration detected"
            elif m2 < m1:
                momentum = "Deceleration detected"
            else:
                momentum = "Momentum stable"
        else:
            momentum = "Insufficient data for momentum analysis"

        # -----------------------------------
        # Risk Flag
        # -----------------------------------

        if growth_pct < 0 and volatility > 0.35:
            risk_flag = "⚠ Emerging performance instability"
        elif volatility > 0.5:
            risk_flag = "⚠ High operational volatility"
        else:
            risk_flag = "No immediate systemic risk detected"

        # -----------------------------------
        # Executive Interpretation
        # -----------------------------------

        interpretation = (
            f"{metric} is currently in a {growth_phase} "
            f"with {volatility_level.lower()}. "
            f"{momentum}."
        )

        return f"""
Trend Intelligence:
• Growth Phase: {growth_phase}
• Total Growth: {round(growth_pct,2)}%
• Volatility Index: {round(volatility,2)} ({volatility_level})
• Momentum Signal: {momentum}
• Risk Signal: {risk_flag}

Executive Trend Interpretation:
{interpretation}
"""

    except:
        return ""


# ======================================================
# GROUPBY ENGINE
# ======================================================

def deterministic_groupby(df, metric, group_by, aggregation):

    if aggregation == "mean":
        return df.groupby(group_by)[metric].mean().reset_index()
    if aggregation == "sum":
        return df.groupby(group_by)[metric].sum().reset_index()
    if aggregation == "max":
        return df.groupby(group_by)[metric].max().reset_index()
    if aggregation == "min":
        return df.groupby(group_by)[metric].min().reset_index()

    return None


# ======================================================
# EXECUTIVE DIAGNOSTIC ENGINE
# ======================================================

def generate_diagnostic(agg_df, original_df, metric, group_by, aggregation):

    y_col = agg_df.columns[1]
    values = agg_df[y_col].values

    total_groups = len(agg_df)
    total_metric_value = original_df[metric].sum()

    mean_val = np.mean(values)
    std_val = np.std(values)
    cv = std_val / mean_val if mean_val != 0 else 0

    median_val = np.median(values)
    value_range = max(values) - min(values)

    if cv < 0.25:
        cv_interpretation = "Low variability (stable distribution)"
    elif cv < 0.6:
        cv_interpretation = "Moderate variability"
    else:
        cv_interpretation = "High concentration risk"

    sorted_df = agg_df.sort_values(by=y_col, ascending=False)
    leader = sorted_df.iloc[0]
    runner = sorted_df.iloc[1] if len(sorted_df) > 1 else None

    if runner is not None and runner[y_col] != 0:
        leader_gap_pct = round((leader[y_col] - runner[y_col]) / runner[y_col] * 100, 2)
    else:
        leader_gap_pct = 0

    total_df = original_df.groupby(group_by)[metric].sum().reset_index()
    total_metric = total_df[metric].sum()
    total_df["share_pct"] = (total_df[metric] / total_metric) * 100
    leader_total = total_df.loc[total_df[metric].idxmax()]
    leader_share = round(leader_total["share_pct"], 2)
    leader_total_value = round(leader_total[metric], 2)

    return f"""
Scope:
• Groups analyzed: {total_groups}
• Total {metric}: {round(total_metric_value,2)}

Distribution Analysis:
• Median {aggregation}: {round(median_val,2)}
• Range: {round(value_range,2)}
• Coefficient of Variation: {round(cv,2)} ({cv_interpretation})
• Leader exceeds runner-up by {leader_gap_pct}%

Contribution Analysis:
• {leader_total[group_by]} contributes {leader_share}% ({leader_total_value}) of total {metric}
"""


# ======================================================
# INSIGHT ENGINE
# ======================================================

def generate_insight(agg_df, original_df, metric, group_by, aggregation):

    x_col = agg_df.columns[0]
    y_col = agg_df.columns[1]

    max_row = agg_df.loc[agg_df[y_col].idxmax()]
    min_row = agg_df.loc[agg_df[y_col].idxmin()]
    diff = round(max_row[y_col] - min_row[y_col], 2)

    aggregation_label = aggregation if aggregation != "mean" else "average"

    diagnostic = generate_diagnostic(
        agg_df,
        original_df,
        metric,
        group_by,
        aggregation_label
    )

    date_col = detect_date_column(original_df)
    trend = generate_trend_analysis(original_df, metric, date_col) if date_col else ""

    return f"""
Performance Overview:
• Highest {aggregation_label} {metric}: {max_row[x_col]} ({round(max_row[y_col],2)})
• Lowest {aggregation_label} {metric}: {min_row[x_col]} ({round(min_row[y_col],2)})
• Absolute Performance Gap: {diff}

{diagnostic}

{trend}

Executive Interpretation:
{max_row[x_col]} currently leads {metric} performance.
Performance dispersion and concentration metrics should guide resource allocation decisions.
"""


# ======================================================
# MAIN ENGINE
# ======================================================

def chat_with_data(question: str, filters: dict = None):

    global LAST_RESULT_DF, LAST_CHART_TYPE, LAST_TITLE
    global LAST_METRIC, LAST_GROUP_BY, LAST_AGGREGATION

    df = get_current_df()
    if df is None:
        return {"type": "text", "answer": "No dataset uploaded."}

    intent = detect_intent(question, list(df.columns))
    metric = intent.get("metric")
    group_by = intent.get("group_by")
    aggregation = intent.get("aggregation")

    # ---------- CORRELATION ----------
    if intent.get("analysis_type") == "correlation":

        col1 = intent.get("metric")
        col2 = intent.get("secondary_metric")

        if col1 in df.columns and col2 in df.columns:

            x = df[col1].values.reshape(-1, 1)
            y = df[col2].values

            model = LinearRegression()
            model.fit(x, y)
            predicted = model.predict(x)

            correlation = np.corrcoef(df[col1], df[col2])[0, 1]

            strength = (
                "Strong" if abs(correlation) > 0.7
                else "Moderate" if abs(correlation) > 0.4
                else "Weak"
            )

            direction = "Positive" if correlation > 0 else "Negative"

            insight = f"""
Correlation Intelligence:
• Correlation Coefficient: {round(correlation,3)}
• {strength} {direction} relationship detected.

Executive Interpretation:
Changes in {col1} appear to influence {col2}.
"""

            return {
                "type": "correlation_plot",
                "x": df[col1].tolist(),
                "y": df[col2].tolist(),
                "predicted": predicted.tolist(),
                "xlabel": col1,
                "ylabel": col2,
                "insight": insight
            }

    plan = plan_query(question, intent, list(df.columns))
    if plan["action"] != "proceed":
        return {"type": "text", "answer": plan["message"]}

    if metric and group_by and aggregation:

        agg_df = deterministic_groupby(df, metric, group_by, aggregation)

        LAST_RESULT_DF = agg_df
        LAST_METRIC = metric
        LAST_GROUP_BY = group_by
        LAST_AGGREGATION = aggregation
        LAST_TITLE = question

        insight_text = generate_insight(
            agg_df,
            df,
            metric,
            group_by,
            aggregation
        )

        return {"type": "text", "answer": insight_text}

    return {"type": "text", "answer": "Try: 'average <metric> by <column>'."}