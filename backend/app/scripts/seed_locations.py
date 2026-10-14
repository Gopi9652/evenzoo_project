import sys
import os
import requests

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.database import SessionLocal
from app.models.location import State, City

db = SessionLocal()

response = requests.post(
    "https://countriesnow.space/api/v0.1/countries/states",
    json={"country": "India"}
)
states_data = response.json()["data"]["states"]

for state_info in states_data:
    state_name = state_info["name"]
    if state_name not in ["Andhra Pradesh", "Telangana"]:
        continue;

    existing_state = db.query(State).filter(State.name == state_name).first()
    if not existing_state:
        existing_state = State(name=state_name)
        db.add(existing_state)
        db.flush()

    # Fetch cities for this state
    city_response = requests.post(
        "https://countriesnow.space/api/v0.1/countries/state/cities",
        json={"country": "India", "state": state_name}
    )
    if city_response.status_code == 200:
        cities = city_response.json().get("data", [])
        for city_name in cities:
            existing_city = db.query(City).filter(
                City.name == city_name,
                City.state_id == existing_state.id
            ).first()
            if not existing_city:
                db.add(City(name=city_name, state_id=existing_state.id))

    db.commit()

db.close()