from pymongo import MongoClient
from google_secrets import connection_string

client = MongoClient(connection_string)
db = client["Codex"]

collection_achievement = db["Logros"]
collection_mission = db["Misiones"]
collection_user = db["Usuarios"]
collection_mission_user = db["Misiones_Usuarios"]
