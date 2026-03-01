import os
import re
import pandas as pd
import pandasql

# New Gemini SDK
from google import genai


# ============================================================
# CONFIG
# ============================================================

GEMINI_KEY = os.getenv("GEMINI_API_KEY")
MODEL_NAME = "gemini-2.0-flash"


# ============================================================
# INIT GEMINI CLIENT (OPTIONAL)
# ============================================================

client = None

if GEMINI_KEY:
    try:
        client = genai.Client(
            api_key=GEMINI_KEY,
            http_options={"api_version": "v1beta"}
        )
        print("[OK] Gemini client initialized")
    except Exception as e:
        print("[WARN] Gemini init failed:", e)
else:
    print("[WARN] GEMINI_API_KEY not found")


# ============================================================
# SANITIZE COLUMNS
# ============================================================

def sanitize_columns(df: pd.DataFrame) -> pd.DataFrame:
    df.columns = (
        df.columns.str.strip()
        .str.lower()
        .str.replace(r"[^a-z0-9_]", "_", regex=True)
        .str.replace(r"__+", "_", regex=True)
    )
    return df


# ============================================================
# CLEAN SQL
# ============================================================

def clean_sql(text: str) -> str:
    text = text.strip()
    text = re.sub(r"^```sql", "", text, flags=re.I)
    text = re.sub(r"^```", "", text)
    text = re.sub(r"```$", "", text)
    return text.strip()


# ============================================================
# RULE BASED SQL (ALWAYS WORKS)
# ============================================================

def generate_sql_rule_based(question: str, columns: list[str]) -> str:

    q = question.lower()

    # COUNT
    if "count" in q or "how many" in q:
        return "SELECT COUNT(*) AS count FROM data"

    # AVG
    if "average" in q or "avg" in q:
        col = columns[0]
        return f"SELECT AVG({col}) AS average FROM data"

    # SUM
    if "sum" in q or "total" in q:
        col = columns[0]
        return f"SELECT SUM({col}) AS total FROM data"

    # MAX
    if "max" in q or "highest" in q:
        col = columns[0]
        return f"SELECT MAX({col}) AS max FROM data"

    # MIN
    if "min" in q or "lowest" in q:
        col = columns[0]
        return f"SELECT MIN({col}) AS min FROM data"

    # SHOW ROWS
    return "SELECT * FROM data LIMIT 10"


# ============================================================
# GEMINI SQL
# ============================================================

def generate_sql_gemini(question: str, columns: list[str]) -> str:

    if not client:
        raise RuntimeError("Gemini not available")

    cols = "\n".join(columns)

    prompt = f"""
You are a data analyst.

Table: data

Columns:
{cols}

Rules:
- Return ONLY SQLite SQL
- No explanation
- No markdown

Question:
{question}

SQL:
"""

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt
    )

    return clean_sql(response.text)


# ============================================================
# MASTER FUNCTION
# ============================================================

def generate_sql(question: str, columns: list[str]) -> str:

    q = question.lower()

    # ----------------------------
    # SMART GROUP BY RULE
    # ----------------------------

    agg_map = {
        "average": "AVG",
        "avg": "AVG",
        "sum": "SUM",
        "total": "SUM",
        "max": "MAX",
        "highest": "MAX",
        "min": "MIN",
        "lowest": "MIN"
    }

    detected_agg = None
    for k in agg_map:
        if k in q:
            detected_agg = agg_map[k]
            break

    detected_group = None
    for col in columns:
        if col.lower() in q:
            detected_group = col
            break

    # If both aggregation + grouping column found
    if detected_agg and detected_group:
        # guess metric column
        metric = None
        for col in columns:
            if col != detected_group:
                metric = col
                break

        return f"""
        SELECT {detected_group},
               {detected_agg}({metric}) AS value
        FROM data
        GROUP BY {detected_group}
        """

    # ----------------------------
    # TRY GEMINI
    # ----------------------------
    try:
        return generate_sql_gemini(question, columns)
    except Exception:
        pass

    # ----------------------------
    # FINAL FALLBACK
    # ----------------------------
    return generate_sql_rule_based(question, columns)

# ============================================================
# RUN SQL
# ============================================================

def run_sql_on_df(df: pd.DataFrame, sql: str):

    try:
        return pandasql.sqldf(sql, {"data": df})
    except Exception as e:
        print("[SQL ERROR]", e)
        return None