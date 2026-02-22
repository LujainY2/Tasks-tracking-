import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId


MONGODB_CONNECTION_STRING = os.environ["MONGODB_CONNECTION_STRING"]
client = AsyncIOMotorClient(MONGODB_CONNECTION_STRING)

db = client.todolist
todos = db.todos

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class TodoItemCreate(BaseModel):
    content: str

@app.post("/todos")
async def create_todo(item: TodoItemCreate):
    result = await todos.insert_one({"content": item.content})
    return {"_id": str(result.inserted_id), "content": item.content}

@app.get("/todos")
async def read_todos():
    items = []
    async for doc in todos.find():
        doc["_id"] = str(doc["_id"])
        items.append(doc)
    return items

@app.delete("/todos/{todo_id}")
async def delete_todo(todo_id: str):
    delete_result = await todos.delete_one({"_id": ObjectId(todo_id)})
    if delete_result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Todo not found")
    return {"message": "Todo deleted successfully"}