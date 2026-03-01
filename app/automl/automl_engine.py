import os
import joblib
import numpy as np
import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline

from sklearn.metrics import accuracy_score, r2_score

from sklearn.linear_model import LogisticRegression, LinearRegression
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.ensemble import ExtraTreesClassifier, ExtraTreesRegressor

from xgboost import XGBClassifier, XGBRegressor
from lightgbm import LGBMClassifier, LGBMRegressor


MODEL_PATH = "models/model.pkl"
ENCODER_PATH = "models/encoders.pkl"
TARGET_ENCODER_PATH = "models/target_encoder.pkl"
FEATURE_PATH = "models/features.pkl"
IMPORTANCE_PATH = "models/feature_importance.pkl"


# ======================================
# DETECT PROBLEM TYPE
# ======================================

def detect_problem_type(y):

    if y.dtype in ["int64", "float64"]:

        unique_ratio = y.nunique() / len(y)

        if unique_ratio > 0.1:
            return "regression"

    return "classification"


# ======================================
# REMOVE BAD FEATURES
# ======================================

def remove_bad_features(df):

    drop_cols = []

    # Manual identifier blacklist
    id_columns = [
        "row_id",
        "order_id",
        "customer_id",
        "customer_name",
        "product_id",
        "product_name",
        "postal_code"
    ]

    for col in df.columns:

        if col in id_columns:
            drop_cols.append(col)
            continue

        unique_ratio = df[col].nunique() / len(df)

        if unique_ratio > 0.95:
            drop_cols.append(col)

        if df[col].dtype == "object" and df[col].nunique() > 100:
            drop_cols.append(col)

    df = df.drop(columns=list(set(drop_cols)), errors="ignore")

    return df


# ======================================
# MODEL CANDIDATES
# ======================================

def get_models(problem_type):

    if problem_type == "classification":

        return {

            "LogisticRegression":
                LogisticRegression(max_iter=2000),

            "RandomForest":
                RandomForestClassifier(n_estimators=200),

            "ExtraTrees":
                ExtraTreesClassifier(n_estimators=200),

            "XGBoost":
                XGBClassifier(
                    eval_metric="logloss",
                    use_label_encoder=False
                ),

            "LightGBM":
                LGBMClassifier()
        }

    else:

        return {

            "LinearRegression":
                LinearRegression(),

            "RandomForest":
                RandomForestRegressor(n_estimators=200),

            "ExtraTrees":
                ExtraTreesRegressor(n_estimators=200),

            "XGBoost":
                XGBRegressor(),

            "LightGBM":
                LGBMRegressor()
        }


# ======================================
# RUN AUTOML
# ======================================

def run_automl(df, target_column):

    os.makedirs("models", exist_ok=True)

    # -----------------------------
    # FEATURE ENGINEERING
    # -----------------------------

    if "order_date" in df.columns:

        df["order_date"] = pd.to_datetime(df["order_date"])

        df["order_date_year"] = df["order_date"].dt.year
        df["order_date_month"] = df["order_date"].dt.month
        df["order_date_day"] = df["order_date"].dt.day

        df.drop(columns=["order_date"], inplace=True)

    # Remove noisy features
    df = remove_bad_features(df)

    y = df[target_column]
    X = df.drop(columns=[target_column])

    problem_type = detect_problem_type(y)

    # -----------------------------
    # PREPROCESSING
    # -----------------------------

    categorical_cols = X.select_dtypes(include=["object", "category"]).columns
    numeric_cols = X.select_dtypes(include=["int64", "float64"]).columns

    preprocessor = ColumnTransformer(
        transformers=[
            ("cat", OneHotEncoder(handle_unknown="ignore"), categorical_cols),
            ("num", "passthrough", numeric_cols)
        ]
    )

    # -----------------------------
    # TRAIN TEST SPLIT
    # -----------------------------

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=42
    )

    models = get_models(problem_type)

    leaderboard = {}
    trained_models = {}

    # -----------------------------
    # TRAIN MODELS
    # -----------------------------

    for name, model in models.items():

        pipeline = Pipeline([
            ("preprocessor", preprocessor),
            ("model", model)
        ])

        pipeline.fit(X_train, y_train)

        preds = pipeline.predict(X_test)

        if problem_type == "classification":
            score = accuracy_score(y_test, preds)
        else:
            score = r2_score(y_test, preds)

        leaderboard[name] = score
        trained_models[name] = pipeline

    # -----------------------------
    # SELECT BEST MODEL
    # -----------------------------

    best_model_name = max(leaderboard, key=leaderboard.get)
    best_model = trained_models[best_model_name]

    # -----------------------------
    # FEATURE IMPORTANCE
    # -----------------------------

    feature_importance = {}

    try:

        model = best_model.named_steps["model"]

        if hasattr(model, "feature_importances_"):

            importances = model.feature_importances_

            for feature, score in zip(X.columns, importances[:len(X.columns)]):

                feature_importance[feature] = float(score)

        elif hasattr(model, "coef_"):

            importances = np.abs(model.coef_[0])

            for feature, score in zip(X.columns, importances[:len(X.columns)]):

                feature_importance[feature] = float(score)

    except Exception:

        feature_importance = {}

    # -----------------------------
    # SAVE MODEL
    # -----------------------------

    joblib.dump(best_model, MODEL_PATH)
    joblib.dump(list(X.columns), FEATURE_PATH)
    joblib.dump(feature_importance, IMPORTANCE_PATH)

    joblib.dump({}, ENCODER_PATH)
    joblib.dump({}, TARGET_ENCODER_PATH)

    # -----------------------------
    # TOP FEATURES
    # -----------------------------

    top_features = dict(
        sorted(feature_importance.items(), key=lambda x: x[1], reverse=True)[:10]
    )

    return {

        "best_model": best_model_name,
        "leaderboard": leaderboard,
        "feature_importance": feature_importance,
        "top_features": top_features
    }