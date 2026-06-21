from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware

from app.db.session import engine, Base
from app.routers import patients, conditions, visits, disease_prediction
from app.auth import require_api_key

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="AI Emergency Decision Support Platform",
    description="Phase 1-4: CRUD API with ML risk engine, auth, and tests.",
    version="0.4.0",
    dependencies=[Depends(require_api_key)],  # protects every route globally
)

# Allows the React frontend (different port) to call this API during dev.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(patients.router)
app.include_router(conditions.router)
app.include_router(visits.router)
app.include_router(disease_prediction.router)


@app.get("/")
def root():
    return {"status": "ok", "message": "Emergency Decision Support API is running"}
