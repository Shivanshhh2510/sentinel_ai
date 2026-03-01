import pandas as pd
import numpy as np

def get_feature_importance(model, X):

    if hasattr(model, "feature_importances_"):
        importances = model.feature_importances_

    elif hasattr(model, "coef_"):
        importances = np.abs(model.coef_[0])

    else:
        return []

    features = X.columns.tolist()

    data = list(zip(features, importances))
    data.sort(key=lambda x: x[1], reverse=True)

    top = [{"feature": f, "importance": round(float(i), 4)} for f, i in data[:10]]

    return top
