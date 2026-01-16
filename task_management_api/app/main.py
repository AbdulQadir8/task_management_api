from fastapi import FastAPI
from app.routes import tasks
from app.database import engine, create_db_and_tables
import uvicorn

app = FastAPI(
    title="Task Management API",
    description="A complete Task Management API with full CRUD operations",
    version="1.0.0"
)

# Include the task routes
app.include_router(tasks.router, prefix="/api/v1", tags=["tasks"])

@app.on_event("startup")
def startup_event():
    create_db_and_tables()

@app.get("/")
async def root():
    return {"message": "Task Management API"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)