from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException, Query
from pymongo.errors import PyMongoError

from app.auth import get_current_user_email
from app.db import collection_mission, collection_mission_user, collection_user
from app.models.schemas import MissionUser, User

router = APIRouter(tags=["users"])


def _serialize_user(user: dict) -> dict:
    return {"id": str(user["_id"]), "email": user["email"], "mission_status": user.get("mission_status", False)}


@router.get("/users", dependencies=[Depends(get_current_user_email)])
def get_users(skip: int = Query(0, ge=0), limit: int = Query(100, ge=1, le=500)):
    try:
        users = collection_user.find({}, {"_id": 1, "email": 1, "mission_status": 1}).skip(skip).limit(limit)
        return [_serialize_user(user) for user in users]
    except PyMongoError:
        raise HTTPException(status_code=500, detail="Failed to fetch users")


@router.get("/users/me")
def get_current_user(email: str = Depends(get_current_user_email)):
    try:
        user = collection_user.find_one({"email": email})
    except PyMongoError:
        raise HTTPException(status_code=500, detail="Failed to fetch user")

    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return _serialize_user(user)


@router.post("/user/create", response_model=User)
def create_user(email: str = Depends(get_current_user_email)):
    try:
        existing_user = collection_user.find_one({"email": email})
        if existing_user:
            raise HTTPException(status_code=400, detail="User already exists")

        user = User(email=email, mission_status=False)
        result = collection_user.insert_one(user.model_dump())
        user_data = user.model_dump()
        user_data["id"] = str(result.inserted_id)

        missions = list(collection_mission.find({}))
        for mission in missions:
            mission_user = MissionUser(user_id=user_data["id"], mission_id=str(mission["_id"]), complete=False)
            collection_mission_user.insert_one(mission_user.model_dump())

        collection_user.update_one({"_id": ObjectId(user_data["id"])}, {"$set": {"mission_status": True}})
        user_data["mission_status"] = True

        return user_data
    except HTTPException:
        raise
    except PyMongoError:
        raise HTTPException(status_code=500, detail="Failed to create user")
