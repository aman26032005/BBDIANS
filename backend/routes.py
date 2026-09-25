from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from .database import get_db
from .models import Confession
from .schemas import ConfessionCreate


router = APIRouter(
    prefix="/confessions",
    tags=["Confessions"]
)


@router.post("/")
def create_confession(
    confession: ConfessionCreate,
    db: Session = Depends(get_db)
):
    new_confession = Confession(
        message=confession.message
    )

    db.add(new_confession)
    db.commit()
    db.refresh(new_confession)

    return {
        "message": "Confession submitted successfully!",
        "confession_id": new_confession.id
    }