import pandas as pd
from sqlalchemy.orm import Session

from app.models.dataset import Dataset
from app.chat.chat_engine import chat_with_data
from app.ingestion.csv_loader import set_current_df


def query_dataset(dataset_id: int, question: str, db: Session):

    dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()

    if not dataset:
        return None

    file_path = dataset.file_path

    # Load dataset
    if file_path.endswith(".csv"):
        df = pd.read_csv(file_path)
    else:
        df = pd.read_excel(file_path)

    # Set dataframe for chat engine
    set_current_df(df)

    # Run AI query
    result = chat_with_data(question, df)

    return {
        "dataset_id": dataset.id,
        "question": question,
        "analysis": result
    }