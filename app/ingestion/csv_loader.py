import pandas as pd
import os

from app.automl.automl_engine import run_automl
from app.ai.llm_engine import generate_explanation
from app.llm.gemini_sql import sanitize_columns
from app.profiling.data_profiler import profile_data
from app.vector.endee_store import build_endee_store


# ==================================
# GLOBAL DATA STORAGE
# ==================================

CURRENT_DF_RAW = None
CURRENT_DF_ENCODED = None


def get_current_df():
    """
    Used by analytics engine.
    Must return RAW dataframe.
    """
    return CURRENT_DF_RAW


def get_encoded_df():
    """
    Used internally for ML models.
    """
    return CURRENT_DF_ENCODED


# ==================================
# SMART TARGET DETECTION
# ==================================

def detect_target_column(df):

    categorical_cols = list(df.select_dtypes(include=["object", "category"]).columns)
    numeric_cols = list(df.select_dtypes(include=["int64", "float64"]).columns)

    # Prefer categorical classification targets
    for col in categorical_cols:
        classes = df[col].nunique()

        if 2 <= classes <= 20:
            return col, "classification", f"categorical column with {classes} classes"

    # Fallback numeric regression
    for col in numeric_cols:

        unique_ratio = df[col].nunique() / len(df)

        if unique_ratio < 0.9:
            return col, "regression", "numeric column with reasonable distribution"

    return df.columns[-1], "classification", "fallback target column"


# ==================================
# ENCODE CATEGORICAL FEATURES
# ==================================

def encode_categorical(df):

    for col in df.columns:

        if df[col].dtype == "object":

            df[col] = df[col].astype("category").cat.codes

    return df


# ==================================
# LOAD DATASET + TRAIN
# ==================================

def load_csv(file_path: str):

    global CURRENT_DF_RAW
    global CURRENT_DF_ENCODED

    ext = os.path.splitext(file_path)[1].lower()

    # --------------------------------
    # SAFE CSV READER
    # --------------------------------

    if ext == ".csv":

        try:
            df = pd.read_csv(file_path, encoding="utf-8")

        except UnicodeDecodeError:
            df = pd.read_csv(file_path, encoding="latin1")

    elif ext in [".xlsx", ".xls"]:

        df = pd.read_excel(file_path)

    else:

        return {
            "status": "error",
            "message": "Unsupported file format"
        }

    # --------------------------------
    # SANITIZE COLUMN NAMES
    # --------------------------------

    df = sanitize_columns(df)

    # --------------------------------
    # SAVE RAW DATASET
    # --------------------------------

    CURRENT_DF_RAW = df.copy()

    # --------------------------------
    # DATASET PROFILING
    # --------------------------------

    profile = profile_data(df)

    # --------------------------------
    # TARGET DETECTION
    # --------------------------------

    target_column, problem_type, target_reason = detect_target_column(df)

    # --------------------------------
    # ENCODE CATEGORICAL FOR ML
    # --------------------------------

    df_encoded = encode_categorical(df.copy())

    CURRENT_DF_ENCODED = df_encoded

    # ==================================
    # BUILD ENDEE STORE (RAG)
    # ==================================

    try:

        documents = []

        for _, row in df.iterrows():
            text_parts = []

            for col, val in row.items():
                if pd.notna(val):
                    text_parts.append(f"{col}: {val}")

            documents.append(" | ".join(text_parts))

        build_endee_store(documents)

    except Exception as e:
        print("Endee store build failed:", e)

    # --------------------------------
    # RUN AUTOML
    # --------------------------------

    try:

        automl_results = run_automl(df_encoded, target_column)

        best_model = automl_results["best_model"]
        leaderboard = automl_results["leaderboard"]
        feature_importance = automl_results["feature_importance"]

        best_score = leaderboard.get(best_model, 0)

    except Exception as e:

        return {
            "rows": len(df),
            "target_column": target_column,
            "problem_type": problem_type,
            "target_reason": target_reason,
            "profile": profile,
            "best_model": "AutoML failed",
            "best_score": 0,
            "model_scores": {},
            "models": [],
            "leaderboard": {},
            "ai_summary": f"Training failed: {str(e)}"
        }

    # --------------------------------
    # MODEL TABLE
    # --------------------------------

    models_table = []

    for model_name, score in leaderboard.items():

        models_table.append({
            "Model": model_name,
            "Score": round(score, 4)
        })

    model_scores = {

        model_name: round(score, 4)

        for model_name, score in leaderboard.items()

        if score > 0
    }

    top_features = sorted(
    feature_importance,
    key=feature_importance.get,
    reverse=True
    )[:5]

    # --------------------------------
    # AI EXPLANATION
    # --------------------------------

    ai_text = generate_explanation(
        prediction="Model Trained",
        confidence=best_score,
        top_features=top_features
    )

    # --------------------------------
    # FINAL RESPONSE
    # --------------------------------

    return {

        "rows": len(df),
        "target_column": target_column,
        "problem_type": problem_type,
        "target_reason": target_reason,

        "profile": profile,

        "best_model": best_model,
        "best_score": round(best_score, 4),

        "model_scores": model_scores,
        "models": models_table,
        "leaderboard": leaderboard,

        "top_features": feature_importance,

        "ai_summary": ai_text
    }