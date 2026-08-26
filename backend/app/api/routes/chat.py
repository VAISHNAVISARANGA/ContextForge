import json

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.models import ChatMessage, User
from app.schemas.schemas import ChatMessageOut, ChatRequest, ChatResponse
from app.services.rag_service import answer_query

router = APIRouter(prefix="/api/chat", tags=["chat"])


@router.post("/", response_model=ChatResponse)
def chat(
    payload: ChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = answer_query(current_user.id, payload.query)

    # persist both sides of the conversation
    db.add(ChatMessage(user_id=current_user.id, role="user", content=payload.query))
    db.add(
        ChatMessage(
            user_id=current_user.id,
            role="assistant",
            content=result["answer"],
            sources=json.dumps(result["sources"]),
        )
    )
    db.commit()

    return ChatResponse(answer=result["answer"], sources=result["sources"])


@router.get("/history", response_model=list[ChatMessageOut])
def get_history(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    return (
        db.query(ChatMessage)
        .filter(ChatMessage.user_id == current_user.id)
        .order_by(ChatMessage.created_at.asc())
        .all()
    )
