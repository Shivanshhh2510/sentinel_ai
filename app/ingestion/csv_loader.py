import pandas as pd
import os
import redis

from app.automl.automl_engine import run_automl
from app.ai.llm_engine import generate_explanation
from app.llm.gemini_sql import sanitize_columns
from app.profiling.data_profiler import profile_data
from app.vector.vector_factory import get_vector_store


# ==================================
# REDIS CONNECTION
# ==================================

redis_client = redis.Redis(host="localhost", port=6379, db=0)


# ==================================
# GLOBAL DATA STORAGE (fallback only)
# ==================================

CURRENT_DF_RAW = None
CURRENT_DF_ENCODED = None


# ==================================
# SET CURRENT DATAFRAME (NEW)
# ==================================

def set_current_df(df: pd.DataFrame):
    """
    Allows external services (dataset_query_service, chat_engine)
    to update the active dataset in memory.
    """
    global CURRENT_DF_RAW
    CURRENT_DF_RAW = df


def get_current_df():
    """
    Used by analytics engine.
    Loads dataset using Redis stored file path.
    """

    global CURRENT_DF_RAW

    file_path = redis_client.get("current_dataset_path")

    if file_path:

        try:

            file_path = file_path.decode()

            ext = os.path.splitext(file_path)[1].lower()

            if ext == ".csv":

                try:
                    df = pd.read_csv(file_path, encoding="utf-8")
                except UnicodeDecodeError:
                    df = pd.read_csv(file_path, encoding="latin1")

            elif ext in [".xlsx", ".xls"]:

                df = pd.read_excel(file_path)

            else:
                return CURRENT_DF_RAW

            CURRENT_DF_RAW = df
            return df

        except Exception:
            return CURRENT_DF_RAW

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
    # SAVE DATASET PATH IN REDIS
    # --------------------------------

    try:
        redis_client.set("current_dataset_path", file_path)
    except Exception as e:
        print("Redis dataset path store failed:", e)

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
    # BUILD VECTOR STORE (Qdrant)
    # ==================================

    try:

        documents = []

        for _, row in df.iterrows():

            text_parts = []

            for col, val in row.items():

                if pd.notna(val):
                    text_parts.append(f"{col}: {val}")

            documents.append(" | ".join(text_parts))

        vector_store = get_vector_store()
        vector_store.upsert(documents)

    except Exception as e:
        print("Vector store build failed:", e)

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