from fastapi import APIRouter
from app.analytics.chart_engine import generate_charts

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/charts")
def get_charts():

    charts = generate_charts()

    return {
        "status": "success",
        "charts": charts
    }