from fastapi import APIRouter, Depends, HTTPException, Query
from pymongo.errors import PyMongoError

from app.auth import get_current_user_email
from app.db import collection_achievement
from app.models.schemas import Achievement

router = APIRouter(tags=["achievements"])


@router.get("/achievements")
def get_achievements(skip: int = Query(0, ge=0), limit: int = Query(100, ge=1, le=500)):
    try:
        achievements = collection_achievement.find({}, {"_id": 1, "name": 1}).skip(skip).limit(limit)
        return [{"id": str(achievement["_id"]), "name": achievement["name"]} for achievement in achievements]
    except PyMongoError:
        raise HTTPException(status_code=500, detail="Failed to fetch achievements")


@router.post("/achievement/create", response_model=Achievement, dependencies=[Depends(get_current_user_email)])
def create_achievement(achievement: Achievement):
    try:
        result = collection_achievement.insert_one(achievement.model_dump())
        achievement_data = achievement.model_dump()
        achievement_data["id"] = str(result.inserted_id)
        return achievement_data
    except PyMongoError:
        raise HTTPException(status_code=500, detail="Failed to create achievement")
