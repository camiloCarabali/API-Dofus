from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException, Query
from pymongo.errors import PyMongoError

from app.auth import get_current_user_email
from app.db import collection_mission_user, collection_user
from app.models.schemas import MissionUser, MissionUserUpdate

router = APIRouter(tags=["mission_users"])


def _owned_user_id(email: str) -> str:
    user = collection_user.find_one({"email": email})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return str(user["_id"])


@router.get("/mission_users", dependencies=[Depends(get_current_user_email)])
def get_mission_users(skip: int = Query(0, ge=0), limit: int = Query(200, ge=1, le=1000)):
    try:
        mission_users = collection_mission_user.find(
            {}, {"_id": 1, "user_id": 1, "mission_id": 1, "complete": 1}
        ).skip(skip).limit(limit)
        return [{"id": str(mission_user["_id"]), "user_id": mission_user["user_id"],
                 "mission_id": mission_user["mission_id"], "complete": mission_user["complete"]}
                for mission_user in mission_users]
    except PyMongoError:
        raise HTTPException(status_code=500, detail="Failed to fetch mission users")


@router.post("/mission_user/create", response_model=MissionUser, dependencies=[Depends(get_current_user_email)])
def create_mission_user(mission_user: MissionUser):
    try:
        existing_mission_user = collection_mission_user.find_one(
            {"user_id": mission_user.user_id, "mission_id": mission_user.mission_id}
        )
        if existing_mission_user:
            raise HTTPException(status_code=400, detail="Mission already assigned to user")

        result = collection_mission_user.insert_one(mission_user.model_dump())
        mission_user_data = mission_user.model_dump()
        mission_user_data["id"] = str(result.inserted_id)
        return mission_user_data
    except HTTPException:
        raise
    except PyMongoError:
        raise HTTPException(status_code=500, detail="Failed to create mission user")


@router.put("/mission_user/update_complete/{id}", response_model=MissionUser)
def update_mission_user_complete(id: str, payload: MissionUserUpdate, email: str = Depends(get_current_user_email)):
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=400, detail="Invalid ID format")

    try:
        mission_user = collection_mission_user.find_one({"_id": ObjectId(id)})
        if not mission_user:
            raise HTTPException(status_code=404, detail="MissionUser not found")

        if mission_user["user_id"] != _owned_user_id(email):
            raise HTTPException(status_code=403, detail="Cannot modify another user's mission")

        collection_mission_user.update_one({"_id": ObjectId(id)}, {"$set": {"complete": payload.complete}})
        mission_user["complete"] = payload.complete
        mission_user["id"] = str(mission_user["_id"])
        return mission_user
    except HTTPException:
        raise
    except PyMongoError:
        raise HTTPException(status_code=500, detail="Failed to update mission user")
