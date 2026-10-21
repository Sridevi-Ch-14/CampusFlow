from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session, joinedload
from app.core.database import get_db
from app.models.location import Campus, Building, Floor, Room
from app.schemas.location import CampusResponse, BuildingResponse, FloorResponse, RoomResponse

router = APIRouter(prefix="/locations", tags=["Locations"])

@router.get("/hierarchy", response_model=List[CampusResponse])
def get_location_hierarchy(db: Session = Depends(get_db)):
    campuses = db.query(Campus).options(
        joinedload(Campus.buildings).joinedload(Building.floors).joinedload(Floor.rooms)
    ).all()
    return campuses

@router.get("/rooms", response_model=List[RoomResponse])
def get_rooms(building_id: str = None, db: Session = Depends(get_db)):
    query = db.query(Room)
    if building_id:
        query = query.join(Floor).filter(Floor.building_id == building_id)
    return query.all()
