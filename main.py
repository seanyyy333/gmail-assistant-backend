from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import emails

app = FastAPI(
    title="Gmail Assistant Backend",
    description="A FastAPI backend to interact with Gmail and generate AI-powered replies.",
    version="1.0.0",
)

# Allow CORS if you need to call this API from a frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include the emails router
app.include_router(
    emails.router,
    prefix="/emails",
    tags=["Emails"],
)

@app.get("/")
def read_root():
    return {"message": "Gmail Assistant API is running."}
