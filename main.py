# Import libraries
from fastapi import FastAPI

# Import router endpoints
from routes import ping, smoke_tests, project, target, test_suite

# Initialize FastAPI app
app = FastAPI()

# Include router endpoints
endpoints = [ping, smoke_tests, project, target, test_suite]
for endpoint in endpoints:
    app.include_router(endpoint.router)

# Root endpoint
@app.get("/")
async def root():
    return {"message": "Hello  World!"}