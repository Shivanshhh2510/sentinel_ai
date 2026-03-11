from fastapi import FastAPI, Body

from app.analytics.query_engine import run_analytical_query

from app.routes.ingestion import router as ingest_router
from app.routes.prediction import router as predict_router
from app.routes.reports import router as report_router
from app.chat.routes import router as chat_router
from app.auth.auth_routes import router as auth_router
from app.routes.rag_query import router as rag_router
from app.routes.charts import router as charts_router
from app.routes.copilot import router as copilot_router
from app.routes.datasets import router as dataset_router

# Import database and models so Alembic/SQLAlchemy knows them
from app.database import engine, Base
from app.models import user, dataset


# ================================
# FASTAPI APP
# ================================

app = FastAPI(
    title="SentinelAI",
    debug=True
)


# ================================
# ROUTERS
# ================================

app.include_router(auth_router)
app.include_router(ingest_router)
app.include_router(predict_router)
app.include_router(report_router)
app.include_router(chat_router)
app.include_router(rag_router)
app.include_router(charts_router)
app.include_router(copilot_router)
app.include_router(dataset_router)


# ================================
# ANALYTICS QUERY ENDPOINT
# ================================

@app.post("/analytics/query")
def query_data(question: str = Body(..., embed=True)):

    result = run_analytical_query(question)

    return {
        "status": "success",
        "question": question,
        "result": result
    }


# ================================
# HEALTH CHECK
# ================================

@app.get("/")
def home():
    return {"status": "SentinelAI Running"}