import re


# =====================================
# METRIC DETECTION
# =====================================

def detect_metric(question: str):

    q = question.lower()

    metrics = [
        "sales",
        "profit",
        "quantity",
        "discount"
    ]

    for m in metrics:
        if m in q:
            return m

    return None


# =====================================
# GROUP BY DETECTION
# =====================================

def detect_groupby(question: str):

    q = question.lower()

    groups = [
        "region",
        "category",
        "sub_category",
        "segment",
        "city",
        "state",
        "customer",
        "product"
    ]

    for g in groups:
        if g in q:
            return g

    return None


# =====================================
# INTENT DETECTION
# =====================================

def detect_intent(question: str):

    q = question.lower()

    # =========================
    # ANALYTICAL QUESTIONS
    # =========================

    if any(k in q for k in ["highest", "top", "max"]):
        return "max"

    if any(k in q for k in ["lowest", "min"]):
        return "min"

    if any(k in q for k in ["average", "mean"]):
        return "average"

    if any(k in q for k in ["total", "sum"]):
        return "sum"

    # =========================
    # TREND QUESTIONS
    # =========================

    if any(k in q for k in ["trend", "over time", "monthly", "timeline"]):
        return "trend"

    # =========================
    # CHART REQUESTS
    # =========================

    if any(k in q for k in ["chart", "plot", "show", "visual", "graph"]):
        return "chart"

    # =========================
    # DATASET INSIGHTS
    # =========================

    if any(k in q for k in ["analyze", "analysis", "insight", "explain dataset"]):
        return "insight"

    # =========================
    # FALLBACK
    # =========================

    return "rag"


# =====================================
# CHART TYPE DETECTION
# =====================================

def detect_chart(question: str):

    q = question.lower()

    line_words = [
        "trend", "over time", "timeline", "monthly",
        "yearly", "daily", "growth", "change over time",
        "time series"
    ]

    histogram_words = [
        "distribution", "histogram", "spread of values",
        "frequency", "value distribution"
    ]

    scatter_words = [
        "correlation", "relationship", "compare",
        "vs", "versus", "impact of", "association"
    ]

    box_words = [
        "outlier", "spread", "range",
        "quartile", "variance"
    ]

    pie_words = [
        "share", "percentage", "proportion",
        "composition", "breakdown"
    ]

    area_words = [
        "growth", "cumulative", "accumulated",
        "running total"
    ]

    heatmap_words = [
        "heatmap", "correlation matrix",
        "feature correlation","correlation heatmap"
    ]

    if any(word in q for word in heatmap_words):
        return "heatmap"

    if any(word in q for word in line_words):
        return "line"

    if any(word in q for word in histogram_words):
        return "histogram"

    if any(word in q for word in scatter_words):
        return "scatter"

    if any(word in q for word in box_words):
        return "box"

    if any(word in q for word in pie_words):
        return "pie"

    if any(word in q for word in area_words):
        return "area"

    return "bar"

# =====================================
# MAIN BRAIN FUNCTION
# =====================================

def analyze_question(question: str):

    intent = detect_intent(question)
    metric = detect_metric(question)
    group_by = detect_groupby(question)
    chart = detect_chart(question)

    return {
        "intent": intent,
        "metric": metric,
        "group_by": group_by,
        "chart": chart
    }