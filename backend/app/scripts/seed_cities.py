import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.database import SessionLocal
from app.models.location import State, City

db = SessionLocal()

# name, state, latitude, longitude
cities_data = [
    ("Hyderabad", "Telangana", 17.3850, 78.4867),
    ("Warangal", "Telangana", 17.9689, 79.5941),
    ("Karimnagar", "Telangana", 18.4386, 79.1288),
    ("Nizamabad", "Telangana", 18.6725, 78.0941),
    ("Vijayawada", "Andhra Pradesh", 16.5062, 80.6480),
    ("Visakhapatnam", "Andhra Pradesh", 17.6868, 83.2185),
    ("Guntur", "Andhra Pradesh", 16.3067, 80.4365),
    ("Narasaraopet", "Andhra Pradesh", 16.2358, 80.0499),
    ("Tirupati", "Andhra Pradesh", 13.6288, 79.4192),
    ("Bangalore", "Karnataka", 12.9716, 77.5946),
    ("Mysore", "Karnataka", 12.2958, 76.6394),
    ("Mangalore", "Karnataka", 12.9141, 74.8560),
    ("Hubli", "Karnataka", 15.3647, 75.1240),
    ("Chennai", "Tamil Nadu", 13.0827, 80.2707),
    ("Coimbatore", "Tamil Nadu", 11.0168, 76.9558),
    ("Madurai", "Tamil Nadu", 9.9252, 78.1198),
    ("Trichy", "Tamil Nadu", 10.7905, 78.7047),
    ("Mumbai", "Maharashtra", 19.0760, 72.8777),
    ("Pune", "Maharashtra", 18.5204, 73.8567),
    ("Nagpur", "Maharashtra", 21.1458, 79.0882),
    ("Nashik", "Maharashtra", 19.9975, 73.7898),
]

states_cache = {}

for city_name, state_name, lat, lng in cities_data:
    if state_name not in states_cache:
        state = db.query(State).filter(State.name == state_name).first()
        if not state:
            state = State(name=state_name)
            db.add(state)
            db.flush()
        states_cache[state_name] = state

    state = states_cache[state_name]

    existing = db.query(City).filter(
        City.name == city_name,
        City.state_id == state.id
    ).first()

    if existing:
        existing.latitude = lat
        existing.longitude = lng
    else:
        db.add(City(name=city_name, state_id=state.id, latitude=lat, longitude=lng))

db.commit()
db.close()
print("✅ States and cities seeded/updated with coordinates")