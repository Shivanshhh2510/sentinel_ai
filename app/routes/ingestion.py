import os
import shutil

from app.tasks.training_task import train_model_task
import uuid

from celery.result import AsyncResult
from app.celery_app import celery_app

from fastapi import APIRouter, UploadFile, File
from fastapi.responses import JSONResponse
from fastapi import Depends
from app.auth.jwt_dependency import get_current_user

from app.ingestion.csv_loader import load_csv

router = APIRouter()


@router.post("/ingest/csv")
async def ingest_csv(
    file: UploadFile = File(...),
    user=Depends(get_current_user)
):
    try:
        os.makedirs("uploads", exist_ok=True)

        file_id = str(uuid.uuid4())
        file_path = f"uploads/{file_id}_{file.filename}"

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # 🚀 Enqueue Celery Job
        task = train_model_task.delay(file_path)

        return {
            "status": "queued",
            "job_id": task.id
        }

    except Exception as e:
        import traceback
        traceback.print_exc()

        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )

@router.get("/job/{job_id}")
def get_job_status(job_id: str):

    task_result = AsyncResult(job_id, app=celery_app)

    if task_result.state == "PENDING":
        return {"status": "pending"}

    if task_result.state == "PROGRESS":
        return {"status": "processing"}

    if task_result.state == "SUCCESS":
        return task_result.result

    if task_result.state == "FAILURE":
        return {
            "status": "failed",
            "error": str(task_result.info)
        }

    return {"status": task_result.state}