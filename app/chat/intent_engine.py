# app/chat/intent_engine.py

import re
import difflib

# ---------------------------------------
# Keywords
# ---------------------------------------

AGG_KEYWORDS = {
    "average": "mean",
    "avg": "mean",
    "mean": "mean",
    "sum": "sum",
    "total": "sum",
    "max": "max",
    "highest": "max",
    "min": "min",
    "lowest": "min"
}

CHART_KEYWORDS = [
    "bar", "line", "pie", "heatmap", "scatter", "histogram"
]

TEXT_KEYWORDS = [
    "explain", "why", "insight", "summary", "analysis"
]

CORRELATION_KEYWORDS = [
    "relationship",
    "correlation",
    "correlate",
    "association",
    "impact between",
    "relationship between",
    "correlation between"
]

STOPWORDS = [
    "show", "me", "the", "a", "an", "of", "for",
    "by", "to", "is", "are", "and", "with",
    "between"
]

# ---------------------------------------
# Helpers
# ---------------------------------------

def normalize(text: str):
    return text.lower().strip()


def closest_match(word, columns):
    """
    Case-insensitive column matching.
    Returns the ORIGINAL column name.
    """

    columns_lower = {c.lower(): c for c in columns}

    matches = difflib.get_close_matches(
        word,
        columns_lower.keys(),
        n=1,
        cutoff=0.6
    )

    if matches:
        return columns_lower[matches[0]]

    return None


# ---------------------------------------
# Main Intent Function
# ---------------------------------------

def detect_intent(question: str, columns: list):

    q = normalize(question)

    tokens = q.split()
    tokens = [t for t in tokens if t not in STOPWORDS]

    metric = None
    group_by = None
    secondary_metric = None
    agg = None
    chart_type = None
    wants_text = False
    analysis_type = None

    # -------------------------------------------------
    # CORRELATION DETECTION
    # -------------------------------------------------

    if any(keyword in q for keyword in CORRELATION_KEYWORDS):

        analysis_type = "correlation"

        detected_cols = []

        for word in tokens:

            col = closest_match(word, columns)

            if col and col not in detected_cols:
                detected_cols.append(col)

        if len(detected_cols) >= 2:
            metric = detected_cols[0]
            secondary_metric = detected_cols[1]

        return {
            "analysis_type": analysis_type,
            "metric": metric,
            "secondary_metric": secondary_metric,
            "group_by": None,
            "aggregation": None,
            "chart_type": "scatter",
            "wants_text": True
        }

    # ---------------------------------------
    # Aggregation Detection
    # ---------------------------------------

    for word in tokens:
        if word in AGG_KEYWORDS:
            agg = AGG_KEYWORDS[word]

    # ---------------------------------------
    # Chart Detection
    # ---------------------------------------

    for word in tokens:
        if word in CHART_KEYWORDS:
            chart_type = word

    # ---------------------------------------
    # Text Request Detection
    # ---------------------------------------

    if any(w in q for w in TEXT_KEYWORDS):
        wants_text = True

    # ---------------------------------------
    # Column Detection (metric by group)
    # ---------------------------------------

    if " by " in q:

        parts = q.split(" by ")

        left = parts[0].split()
        right = parts[1].split()

        # Detect metric (skip aggregation words)
        for word in left:

            if word in AGG_KEYWORDS:
                continue

            col = closest_match(word, columns)

            if col:
                metric = col
                break

        # Detect group_by
        for word in right:
            col = closest_match(word, columns)
            if col and col != metric:
                group_by = col
                break

    # ---------------------------------------
    # Fallback Column Detection
    # ---------------------------------------

    detected_columns = []

    for word in tokens:

        col = closest_match(word, columns)

        if col and col not in detected_columns:
            detected_columns.append(col)

    if metric is None and detected_columns:
        metric = detected_columns[0]

    if group_by is None and len(detected_columns) > 1:

        for col in detected_columns:
            if col != metric:
                group_by = col
                break

    top_n = None

    for token in tokens:
        if token.isdigit():
            top_n = int(token)

    if "top" in q and top_n is None:
        top_n = 5


    return {
        "analysis_type": None,
        "metric": metric,
        "secondary_metric": None,
        "group_by": group_by,
        "aggregation": agg,
        "chart_type": chart_type,
        "wants_text": wants_text,
        "top_n": top_n
    }