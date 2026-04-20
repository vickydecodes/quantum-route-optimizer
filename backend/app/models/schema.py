from pydantic import BaseModel, validator
from typing import List, Optional


class Location(BaseModel):
    lat: float
    lng: float

    @validator("lat")
    def validate_lat(cls, v):
        if not (-90 <= v <= 90):
            raise ValueError("Latitude must be between -90 and 90")
        return round(v, 6)

    @validator("lng")
    def validate_lng(cls, v):
        if not (-180 <= v <= 180):
            raise ValueError("Longitude must be between -180 and 180")
        return round(v, 6)


class DeliveryRequest(BaseModel):
    locations: List[Location]

    @validator("locations")
    def validate_locations(cls, v):
        if len(v) < 2:
            raise ValueError("At least 2 locations are required")
        return v