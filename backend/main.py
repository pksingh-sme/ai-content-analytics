from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .api import router as api_router
from .api.blip2_routes import router as blip2_router
from .api.rag_routes import router as rag_router
from .api.agent_routes import router as agent_router
from .evaluation.api import router as evaluation_router
from .logging.api import router as logging_router
from .config import settings

app = FastAPI(
    title="Multi-Modal Content Analytics API",
    description="API for processing documents, images, audio, and video with AI-powered analytics",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_router, prefix="/api/v1")
app.include_router(blip2_router, prefix="/api/v1/blip2")
app.include_router(rag_router, prefix="/api/v1")
app.include_router(agent_router, prefix="/api/v1")
app.include_router(evaluation_router, prefix="/api/v1")
app.include_router(logging_router, prefix="/api/v1")

@app.get("/")
async def root():
    return {"message": "Multi-Modal Content Analytics API is running!"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}