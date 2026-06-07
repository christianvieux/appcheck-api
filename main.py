# Import libraries
from fastapi import FastAPI

# Import router endpoints
from routers import ping, run_tests, project, target

# Initialize FastAPI app
app = FastAPI()

# Include router endpoints
endpoints = [ping, run_tests, project, target]
for endpoint in endpoints:
    app.include_router(endpoint.router)

# Root endpoint
@app.get("/")
async def root():
    return {"message": "Hello  World!"}