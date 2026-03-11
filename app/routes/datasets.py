from fastapi import APIRouter, UploadFile, File, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.dataset_service import save_dataset, list_datasets, get_dataset_details, get_dataset_preview

from fastapi import Body
from app.services.dataset_query_service import query_dataset

router = APIRouter(prefix="/datasets", tags=["Datasets"])

@router.get("/")
def get_datasets(db: Session = Depends(get_db)):

    # Temporary user_id
    user_id = 1

    datasets = list_datasets(user_id, db)

    return {
        "status": "success",
        "datasets": datasets
    }

@router.post("/upload")
def upload_dataset(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):

    # Temporary user_id (authentication will come later)
    user_id = 1

    result = save_dataset(file, user_id, db)

    return {
        "status": "success",
        "dataset": result
    }

@router.get("/{dataset_id}")
def dataset_details(dataset_id: int, db: Session = Depends(get_db)):

    result = get_dataset_details(dataset_id, db)

    if not result:
        return {
            "status": "error",
            "message": "Dataset not found"
        }

    return {
        "status": "success",
        "dataset": result
    }

@router.get("/{dataset_id}/preview")
def dataset_preview(dataset_id: int, db: Session = Depends(get_db)):

    result = get_dataset_preview(dataset_id, db)

    if not result:
        return {
            "status": "error",
            "message": "Dataset not found"
        }

    return {
        "status": "success",
        "preview": result
    }

@router.post("/{dataset_id}/query")
def dataset_query(
    dataset_id: int,
    question: str = Body(..., embed=True),
    db: Session = Depends(get_db)
):

    result = query_dataset(dataset_id, question, db)

    if not result:
        return {
            "status": "error",
            "message": "Dataset not found"
        }

    return {
        "status": "success",
        "query_result": result
    }