import json

from fastapi import APIRouter, Depends, HTTPException, Query
from pymongo.errors import PyMongoError

from app.auth import get_current_user_email
from app.db import collection_mission

router = APIRouter(tags=["missions"])


@router.get("/missions")
def get_missions(skip: int = Query(0, ge=0), limit: int = Query(100, ge=1, le=500)):
    try:
        missions = list(
            collection_mission.find({}, {"_id": 1, "name": 1, "achievement_id": 1, "video": 1}).skip(skip).limit(limit)
        )
        return [{"id": str(mission["_id"]), "name": mission["name"], "achievement_id": mission["achievement_id"],
                 "video": mission["video"]} for mission in missions]
    except PyMongoError:
        raise HTTPException(status_code=500, detail="Failed to fetch missions")


@router.post("/mission/create", dependencies=[Depends(get_current_user_email)])
def create_missions():
    try:
        with open("missions.json", "r") as file:
            missions = json.load(file)
    except (OSError, json.JSONDecodeError):
        raise HTTPException(status_code=500, detail="Failed to read missions seed file")

    try:
        for mission in missions:
            existing_mission = collection_mission.find_one({"name": mission["name"]})
            if existing_mission:
                continue
            collection_mission.insert_one(mission)
    except PyMongoError:
        raise HTTPException(status_code=500, detail="Failed to create missions")

    return {"message": "Missions created successfully"}
