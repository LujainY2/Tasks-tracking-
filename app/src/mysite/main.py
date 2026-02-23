import os
from datetime import datetime
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId

# -------------------------
# Database Connection
# -------------------------

MONGODB_CONNECTION_STRING = os.environ["MONGODB_CONNECTION_STRING"]
client = AsyncIOMotorClient(MONGODB_CONNECTION_STRING)

db = client.tasktracker
tasks_collection = db.tasks

# -------------------------
# FastAPI App
# -------------------------

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------
# Static Files (SAFE PATH)
# -------------------------

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/")
async def root():
    return FileResponse(os.path.join(STATIC_DIR, "index.html"))

# -------------------------
# Models
# -------------------------

class TaskCreate(BaseModel):
    title: str
    description: str
    priority: str
    due_date: str


class TaskUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    priority: str | None = None
    status: str | None = None
    due_date: str | None = None

# -------------------------
# Routes
# -------------------------

@app.post("/tasks")
async def create_task(task: TaskCreate):
    task_dict = task.model_dump()
    task_dict["status"] = "Pending"
    task_dict["created_at"] = datetime.utcnow()

    result = await tasks_collection.insert_one(task_dict)
    task_dict["_id"] = str(result.inserted_id)

    return task_dict


@app.get("/tasks")
async def get_tasks():
    tasks = []
    async for task in tasks_collection.find():
        task["_id"] = str(task["_id"])
        tasks.append(task)
    return tasks


@app.put("/tasks/{task_id}")
async def update_task(task_id: str, task: TaskUpdate):
    update_data = {k: v for k, v in task.model_dump().items() if v is not None}

    update_result = await tasks_collection.update_one(
        {"_id": ObjectId(task_id)},
        {"$set": update_data}
    )

    if update_result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Task not found")

    return {"message": "Task updated successfully"}


@app.delete("/tasks/{task_id}")
async def delete_task(task_id: str):
    delete_result = await tasks_collection.delete_one({"_id": ObjectId(task_id)})

    if delete_result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Task not found")

    return {"message": "Task deleted successfully"}
