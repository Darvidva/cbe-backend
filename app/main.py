from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.routing import APIRouter
from app.core.config import settings
from app.db.session import Base, engine, SessionLocal
from app.db.seed import seed_admin
from app.api.v1.routes import auth, subjects, questions, exams, results
import traceback

app = FastAPI(title="CBE Backend")

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    print(f"Global exception handler caught: {exc}")
    print("🔗 Connected to database:", settings.DATABASE_URL)
    print("Traceback:")
    traceback.print_exc()
    return JSONResponse(
        status_code=500,
        content={"detail": str(exc)}
    )

# Configure CORS - must be added before any routes
origins = [
    "http://localhost:3000",
    "https://cbe-frontend-work.vercel.app",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {
        "message": "CBE Backend API",
        "version": "1.0.0",
        "docs_url": "/docs"
    }

@app.on_event("startup")
async def on_startup():
    print("🔗 Connected to database:", settings.DATABASE_URL)
    # create tables
    Base.metadata.create_all(bind=engine)
    # seed admin
    db = SessionLocal()
    try:
        seed_admin(db)
    finally:
        db.close()

# Create API v1 router
api_v1 = APIRouter(prefix="/api/v1")

# Add routes to v1 router
api_v1.include_router(auth.router, prefix="/auth", tags=["auth"])
api_v1.include_router(subjects.router, prefix="/subjects", tags=["subjects"])
api_v1.include_router(questions.router, prefix="/questions", tags=["questions"])
api_v1.include_router(exams.router, prefix="/exams", tags=["exams"])
api_v1.include_router(results.router, prefix="/results", tags=["results"])

# Include v1 router in main app
app.include_router(api_v1)
