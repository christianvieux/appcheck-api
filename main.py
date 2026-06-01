# Import libraries
from fastapi import FastAPI

# Import router endpoints
from routers import ping, run_tests

# Initialize FastAPI app
app = FastAPI()

# Include router endpoints
app.include_router(ping.router)
app.include_router(run_tests.router)

# Root endpoint
@app.get("/")
async def root():
    return {"message": "Hello  World!"}