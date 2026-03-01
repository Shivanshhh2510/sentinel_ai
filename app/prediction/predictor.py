import joblib
import pandas as pd

MODEL_PATH = "models/model.pkl"
ENCODER_PATH = "models/encoders.pkl"
TARGET_ENCODER_PATH = "models/target_encoder.pkl"
FEATURE_PATH = "models/features.pkl"
IMPORTANCE_PATH = "models/feature_importance.pkl"


def load_model():
    model = joblib.load(MODEL_PATH)
    encoders = joblib.load(ENCODER_PATH)
    target_encoder = joblib.load(TARGET_ENCODER_PATH)
    columns = joblib.load(FEATURE_PATH)
    importance = joblib.load(IMPORTANCE_PATH)

    return model, encoders, target_encoder, columns, importance


def predict_single(data):

    model, encoders, target_encoder, columns, importance = load_model()

    df = pd.DataFrame([data])

    if "order_date" in df.columns:
        df["order_date"] = pd.to_datetime(df["order_date"])
        df["order_date_year"] = df["order_date"].dt.year
        df["order_date_month"] = df["order_date"].dt.month
        df["order_date_day"] = df["order_date"].dt.day
        df.drop(columns=["order_date"], inplace=True)

    for col, encoder in encoders.items():
        if col in df.columns:
            df[col] = encoder.transform(df[col])

    df = df[columns]

    prediction = model.predict(df)[0]
    confidence = float(max(model.predict_proba(df)[0]))

    label = target_encoder.inverse_transform([prediction])[0]

    sorted_features = sorted(
        importance.items(),
        key=lambda x: x[1],
        reverse=True
    )

    top_factors = [f[0] for f in sorted_features[:3]]

    return {
        "prediction": label,
        "confidence": round(confidence, 2),
        "top_factors": top_factors
    }
