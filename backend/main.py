"""
main.py - FastAPI application entry point for PolicyPilot

Sets up the FastAPI app with CORS middleware and route includes.
Run with: uvicorn main:app --reload
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
import sys

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from backend.routes.analyze import router as analyze_router

# Create FastAPI app
app = FastAPI(
    title="PolicyPilot API",
    description="AI-Powered Government Scheme Discovery Platform",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS middleware - allow frontend to call backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",       # React dev server
        "http://localhost:8000",        # Same origin
        "https://policypilot.vercel.app",  # Production frontend
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(analyze_router, prefix="/api", tags=["analysis"])


@app.get("/")
async def root():
    """Root endpoint with API info."""
    return {
        "name": "PolicyPilot API",
        "version": "1.0.0",
        "description": "AI-Powered Government Scheme Discovery Platform",
        "docs": "/docs",
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
