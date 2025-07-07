from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import your email router
from .routers import emails

app = FastAPI(
    title="Gmail Assistant API",
    description="API backend to fetch, process, and reply to Gmail emails using GPT",
    version="0.1.0"
)

# Allow CORS if you're connecting from a frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict this!
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include the email routes
app.include_router(emails.router, prefix="/emails", tags=["Emails"])

@app.get("/")
def root():
    return {"message": "Gmail Assistant API is running."}
