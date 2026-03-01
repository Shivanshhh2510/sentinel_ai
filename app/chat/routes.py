from fastapi import APIRouter, Depends
from app.auth.jwt_dependency import get_current_user
from app.chat.chat_engine import chat_with_data

router = APIRouter(tags=["Chat"])

@router.post("/chat")
def chat(payload: dict, user=Depends(get_current_user)):

    print("CHAT ROUTE HIT")
    print("Payload:", payload)
    print("User:", user)

    question = payload.get("question")
    filters = payload.get("filters", {})

    if not question:
        return {"type": "text", "answer": "Question is empty."}

    result = chat_with_data(question, filters)

    print("Chat result:", result)

    return result