from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.db import crud
from app.schemas import schemas

router = APIRouter(prefix="/conditions", tags=["conditions"])


@router.get("/", response_model=list[schemas.ConditionOut])
def list_conditions(db: Session = Depends(get_db)):
    return crud.get_conditions(db)


@router.get("/{condition_id}", response_model=schemas.ConditionOut)
def get_condition(condition_id: int, db: Session = Depends(get_db)):
    condition = crud.get_condition(db, condition_id)
    if not condition:
        raise HTTPException(status_code=404, detail="Condition not found")
    return condition
