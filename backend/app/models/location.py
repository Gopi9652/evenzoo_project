from sqlalchemy import Column, Integer, String, ForeignKey, Float
from sqlalchemy.orm import relationship
from app.database import Base

class State(Base):
    __tablename__ = "states"

    id   = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)

    cities = relationship("City", back_populates="state")


class City(Base):
    __tablename__ = "cities"

    id        = Column(Integer, primary_key=True)
    state_id  = Column(Integer, ForeignKey("states.id"))
    name      = Column(String(100), nullable=False)
    latitude  = Column(Float, nullable=True)   # ← new
    longitude = Column(Float, nullable=True)   # ← new

    state = relationship("State", back_populates="cities")