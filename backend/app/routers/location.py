from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app.models.location import State, City
from app.schemas.location import StateResponse, CityResponse
import math
from app.schemas.location import NearestCityResponse

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


def haversine_distance(lat1, lng1, lat2, lng2):
    """Calculates distance in km between two lat/lng points."""
    R = 6371  # Earth's radius in km
    dlat = math.radians(lat2 - lat1)
    dlng = math.radians(lng2 - lng1)
    a = (math.sin(dlat / 2) ** 2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
         math.sin(dlng / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c


@router.get("/nearest-city", response_model=NearestCityResponse)
def find_nearest_city(
    lat: float = Query(..., description="Latitude from browser geolocation"),
    lng: float = Query(..., description="Longitude from browser geolocation"),
    db: Session = Depends(get_db)
):
    cities = db.query(City).filter(
        City.latitude.isnot(None),
        City.longitude.isnot(None)
    ).all()

    if not cities:
        raise HTTPException(status_code=404, detail="No cities with location data available")

    nearest = None
    min_distance = float("inf")

    for city in cities:
        distance = haversine_distance(lat, lng, city.latitude, city.longitude)
        if distance < min_distance:
            min_distance = distance
            nearest = city

    state = db.query(State).filter(State.id == nearest.state_id).first()

    return {
        "city_id": nearest.id,
        "city_name": nearest.name,
        "state_id": nearest.state_id,
        "state_name": state.name if state else "Unknown",
        "distance_km": round(min_distance, 1)
    }