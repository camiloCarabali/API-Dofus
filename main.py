from fastapi import FastAPI, HTTPException
from pymongo import MongoClient
from bson.json_util import dumps
from google_secrets import connection_string

client = MongoClient(connection_string)
db = client["Misiones"]
collection = db["General"]

app = FastAPI()


@app.get("/misiones/general")
def read_items():
    try:
        items = list(collection.find())
        return dumps(items)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
