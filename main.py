from pydantic import BaseModel, Field
from fastapi import FastAPI, HTTPException, Query
from pymongo import MongoClient
from google_secrets import connection_string

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


class Mission(BaseModel):
    name: str
    video: str
    achievement_id: str = Field(..., description="ID of the associated achievement")


class User(BaseModel):
    email: str


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
        users = collection_user.find({}, {"_id": 1, "email": 1})
        return [{"id": str(user["_id"]), "email": user["email"]} for user in users]
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


@app.post("/mission/create", response_model=Mission)
def create_mission(
        name: str = Query(..., description="Name of the mission"),
        video: str = Query(..., description="Video URL of the mission"),
        achievement_id: str = Query(..., description="ID of the associated achievement")
):
    mission = Mission(name=name, video=video, achievement_id=str(achievement_id))
    try:
        result = collection_mission.insert_one(mission.model_dump(by_alias=True))
        mission_data = mission.model_dump(by_alias=True)
        mission_data["id"] = str(result.inserted_id)
        return mission_data
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/user/create", response_model=User)
def create_user(
        email: str = Query(..., description="Email of the user")
):
    user = User(email=email)
    try:
        result = collection_user.insert_one(user.model_dump())
        user_data = user.model_dump()
        user_data["id"] = str(result.inserted_id)
        return user_data
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
        result = collection_mission_user.insert_one(mission_user.model_dump())
        mission_user_data = mission_user.model_dump()
        mission_user_data["id"] = str(result.inserted_id)
        return mission_user_data
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
