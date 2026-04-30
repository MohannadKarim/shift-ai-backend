from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.config import settings
from app.services.firebase import init_firebase
from app.routers import auth, workflows, agents, prompts, submissions, users, admin


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    init_firebase()
    print("✅ Firebase initialized")
    yield
    # Shutdown (add cleanup here if needed)
    print("👋 Shutting down")


app = FastAPI(
    title="Shift AI Platform",
    description="AI-native operating system for Telfaz11 creative agency",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS — lock this down to your frontend domain in production
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(auth.router,        prefix="/auth",        tags=["Auth"])
app.include_router(users.router,       prefix="/users",       tags=["Users"])
app.include_router(workflows.router,   prefix="/workflows",   tags=["Workflows"])
app.include_router(agents.router,      prefix="/agents",      tags=["Agents"])
app.include_router(prompts.router,     prefix="/prompts",     tags=["Prompts"])
app.include_router(submissions.router, prefix="/submissions", tags=["Submissions"])
app.include_router(admin.router,       prefix="/admin",       tags=["Admin"])


@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "ok", "version": "1.0.0"}
