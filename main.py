# Import libraries
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import app settings
from config import get_settings

# Import router endpoints
from routes import assertions, ping, smoke_tests, project, target, test_suite

# Load settings
settings = get_settings()

# Initialize FastAPI app
app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_frontend_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include router endpoints
endpoints = [ping, assertions, smoke_tests, project, target, test_suite]
for endpoint in endpoints:
    app.include_router(endpoint.router)

# Root endpoint
@app.get("/")
async def root():
    return {"message": "Hello  World!"}