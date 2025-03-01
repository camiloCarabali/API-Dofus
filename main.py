from pydantic import BaseModel, Field
from fastapi import FastAPI, HTTPException, Query
from pymongo import MongoClient
from bson.json_util import dumps
from google_secrets import connection_string

client = MongoClient(connection_string)
db = client["Codex"]
collection_achievement = db["Logros"]
collection_mission = db["Misiones"]

app = FastAPI()


class Achievement(BaseModel):
    name: str
    description: str
    type_achievement: str


class Mission(BaseModel):
    nombre: str
    video: str
    checklist: bool = Field(default=False, description="Checklist status for the mission")
    achievement_id: str = Field(..., description="ID of the associated achievement")


@app.get("/achievements")
def get_achievements():
    try:
        achievements = list(collection_achievement.find())
        return dumps(achievements)
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
        nombre: str = Query(..., description="Name of the mission"),
        video: str = Query(..., description="Video URL of the mission"),
        checklist: bool = Query(False, description="Checklist status for the mission"),
        achievement_id: str = Query(..., description="ID of the associated achievement")
):
    mission = Mission(nombre=nombre, video=video, checklist=checklist, achievement_id=str(achievement_id))
    try:
        result = collection_mission.insert_one(mission.model_dump(by_alias=True))
        mission_data = mission.model_dump(by_alias=True)
        mission_data["id"] = str(result.inserted_id)
        return mission_data
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
