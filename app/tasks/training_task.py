from celery import shared_task
from app.ingestion.csv_loader import load_csv
import redis
import json

r = redis.Redis(host="localhost", port=6379, db=0)


@shared_task(bind=True)
def train_model_task(self, file_path: str):
    try:
        self.update_state(state="PROGRESS")

        summary = load_csv(file_path)

        # store latest dataset path in redis
        r.set("current_dataset_path", file_path)

        return {
            "status": "completed",
            "summary": summary
        }

    except Exception as e:
        return {
            "status": "failed",
            "error": str(e)
        }