from fastapi import APIRouter, Depends
from app.prediction.predictor import predict_single
from app.auth.jwt_dependency import get_current_user

router = APIRouter()


@router.post("/predict")
def predict(payload: dict, user=Depends(get_current_user)):
    return predict_single(payload)