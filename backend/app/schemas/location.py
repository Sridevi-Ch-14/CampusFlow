from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict

class RoomResponse(BaseModel):
    id: str
    floor_id: str
    room_number: str
    room_type: str

    model_config = ConfigDict(from_attributes=True)

class FloorResponse(BaseModel):
    id: str
    building_id: str
    floor_number: int
    name: str
    rooms: List[RoomResponse] = []

    model_config = ConfigDict(from_attributes=True)

class BuildingResponse(BaseModel):
    id: str
    campus_id: str
    name: str
    code: str
    floors: List[FloorResponse] = []

    model_config = ConfigDict(from_attributes=True)

class CampusResponse(BaseModel):
    id: str
    name: str
    code: str
    buildings: List[BuildingResponse] = []

    model_config = ConfigDict(from_attributes=True)

class RoomDetailResponse(RoomResponse):
    floor_name: Optional[str] = None
    building_name: Optional[str] = None
    campus_name: Optional[str] = None
    full_location_string: Optional[str] = None
