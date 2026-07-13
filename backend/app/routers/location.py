from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app.models.location import State, City
from app.schemas.location import StateResponse, CityResponse

router = APIRouter(tags=["Location"])


@router.get("/states", response_model=List[StateResponse])
def get_states(db: Session = Depends(get_db)):
    return db.query(State).order_by(State.name).all()


@router.get("/cities", response_model=List[CityResponse])
def get_cities(
    state_id: Optional[int] = Query(None),
    db: Session = Depends(get_db)
):
    query = db.query(City)
    if state_id:
        query = query.filter(City.state_id == state_id)
    return query.order_by(City.name).all()

@router.get("/cities/{city_id}", response_model=CityResponse)
def get_city_by_id(city_id: int, db: Session = Depends(get_db)):
    city = db.query(City).filter(City.id == city_id).first()
    if not city:
        raise HTTPException(status_code=404, detail="City not found")
    return city