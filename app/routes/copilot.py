from fastapi import APIRouter, Body
from app.ai.copilot_engine import run_copilot

router = APIRouter(prefix="/copilot", tags=["AI Copilot"])


@router.post("/ask")
def ask_copilot(question: str = Body(..., embed=True)):

    result = run_copilot(question)

    return result