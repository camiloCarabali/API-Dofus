from pydantic import BaseModel, Field


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


class MissionUserUpdate(BaseModel):
    complete: bool = Field(..., description="Completion status of the mission")
