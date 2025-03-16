from bson import ObjectId
from pydantic import BaseModel, Field
from fastapi import FastAPI, HTTPException, Query
from pymongo import MongoClient
from google_secrets import connection_string
import json

client = MongoClient(connection_string)
db = client["Codex"]
collection_achievement = db["Logros"]
collection_mission = db["Misiones"]
collection_user = db["Usuarios"]
collection_mission_user = db["Misiones_Usuarios"]

app = FastAPI()


class Achievement(BaseModel):
    name: str
    description: str
    type_achievement: str


class User(BaseModel):
    email: str
    mission_status: bool = Field(False, description="Status of the user's mission")


class MissionUser(BaseModel):
    user_id: str = Field(..., description="ID of the user")
    mission_id: str = Field(..., description="ID of the mission")
    complete: bool = Field(False, description="Completion status of the mission")


@app.get("/achievements")
def get_achievements():
    try:
        achievements = collection_achievement.find({}, {"_id": 1, "name": 1})
        return [{"id": str(achievement["_id"]), "name": achievement["name"]} for achievement in achievements]
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/missions")
def get_missions():
    try:
        missions = list(
            collection_mission.find({}, {"_id": 1, "name": 1, "video": 1, "checklist": 1, "achievement_id": 1}))
        return [{"id": str(mission["_id"]), "name": mission["name"], "video": mission["video"],
                 "checklist": mission["checklist"], "achievement_id": mission["achievement_id"]} for mission in
                missions]
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/users")
def get_users():
    try:
        users = collection_user.find({}, {"_id": 1, "email": 1, "mission_status": 1})
        return [{"id": str(user["_id"]), "email": user["email"], "mission_status": user.get("mission_status", False)}
                for user in users]
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/mission_users")
def get_mission_users():
    try:
        mission_users = collection_mission_user.find({}, {"_id": 1, "user_id": 1, "mission_id": 1, "complete": 1})
        return [{"id": str(mission_user["_id"]), "user_id": mission_user["user_id"],
                 "mission_id": mission_user["mission_id"], "complete": mission_user["complete"]} for mission_user in
                mission_users]
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/achievement/create", response_model=Achievement)
def create_achievement(
        name: str = Query(..., description="Name of the achievement"),
        description: str = Query(..., description="Description of the achievement"),
        type_achievement: str = Query(..., description="Type of the achievement")
):
    achievement = Achievement(name=name, description=description, type_achievement=type_achievement)
    try:
        result = collection_achievement.insert_one(achievement.model_dump())
        achievement_data = achievement.model_dump()
        achievement_data["id"] = str(result.inserted_id)
        return achievement_data
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/mission/create")
def create_missions():
    try:
        with open('missions.json', 'r') as file:
            missions = json.load(file)
            for mission in missions:
                existing_mission = collection_mission.find_one({"name": mission["name"]})
                if existing_mission:
                    continue

                collection_mission.insert_one(mission)

        return {"message": "Missions created successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/user/create", response_model=User)
def create_user(
        email: str = Query(..., description="Email of the user"),
        mission_status: bool = Query(False, description="Status of the user's mission")
):
    user = User(email=email, mission_status=mission_status)
    try:
        existing_user = collection_user.find_one({"email": email})
        if existing_user:
            raise HTTPException(status_code=400, detail="User already exists")

        result = collection_user.insert_one(user.model_dump())
        user_data = user.model_dump()
        user_data["id"] = str(result.inserted_id)

        missions = list(collection_mission.find({}))
        for mission in missions:
            mission_user = MissionUser(user_id=user_data["id"], mission_id=str(mission["_id"]), complete=False)
            collection_mission_user.insert_one(mission_user.model_dump())

        # Update the user's mission status to true
        collection_user.update_one({"_id": ObjectId(user_data["id"])}, {"$set": {"mission_status": True}})
        user_data["mission_status"] = True

        return user_data
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/mission_user/create", response_model=MissionUser)
def create_mission_user(
        user_id: str = Query(..., description="ID of the user"),
        mission_id: str = Query(..., description="ID of the mission"),
        complete: bool = Query(False, description="Completion status of the mission")
):
    mission_user = MissionUser(user_id=user_id, mission_id=mission_id, complete=complete)
    try:
        existing_mission_user = collection_mission_user.find_one({"user_id": user_id, "mission_id": mission_id})
        if existing_mission_user:
            raise HTTPException(status_code=400, detail="Mission already assigned to user")

        result = collection_mission_user.insert_one(mission_user.model_dump())
        mission_user_data = mission_user.model_dump()
        mission_user_data["id"] = str(result.inserted_id)
        return mission_user_data
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.put("/mission_user/update_complete/{id}", response_model=MissionUser)
def update_mission_user_complete(id: str, complete: bool = Query(..., description="Completion status of the mission")):
    try:
        if not ObjectId.is_valid(id):
            raise HTTPException(status_code=400, detail="Invalid ID format")

        result = collection_mission_user.update_one({"_id": ObjectId(id)}, {"$set": {"complete": complete}})
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="MissionUser not found")

        mission_user = collection_mission_user.find_one({"_id": ObjectId(id)})
        mission_user["id"] = str(mission_user["_id"])
        return mission_user
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
