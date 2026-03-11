import re
import pandas as pd
import pandasql

from app.llm.llm_factory import get_llm


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
# RULE BASED SQL (SAFE FALLBACK)
# ============================================================

def generate_sql_rule_based(question: str, columns: list[str]) -> str:

    q = question.lower()

    if "count" in q or "how many" in q:
        return "SELECT COUNT(*) AS count FROM data"

    if "average" in q or "avg" in q:
        col = columns[0]
        return f"SELECT AVG({col}) AS average FROM data"

    if "sum" in q or "total" in q:
        col = columns[0]
        return f"SELECT SUM({col}) AS total FROM data"

    if "max" in q or "highest" in q:
        col = columns[0]
        return f"SELECT MAX({col}) AS max FROM data"

    if "min" in q or "lowest" in q:
        col = columns[0]
        return f"SELECT MIN({col}) AS min FROM data"

    return "SELECT * FROM data LIMIT 10"


# ============================================================
# GEMINI SQL GENERATION
# ============================================================

def generate_sql_gemini(question: str, columns: list[str]) -> str:

    llm = get_llm()

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

    response = llm.generate(prompt)

    return clean_sql(response)


# ============================================================
# MASTER FUNCTION
# ============================================================

def generate_sql(question: str, columns: list[str]) -> str:

    q = question.lower()

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

    if detected_agg and detected_group:
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

    try:
        return generate_sql_gemini(question, columns)
    except Exception:
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