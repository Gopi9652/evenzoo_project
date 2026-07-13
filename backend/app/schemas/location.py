from pydantic import BaseModel


class StateResponse(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True


class CityResponse(BaseModel):
    id: int
    name: str
    state_id: int

    class Config:
        from_attributes = True