from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from analysis_service import analyze_scope
from schemas import ScopeAnalysisRequest, ScopeAnalysisResponse

app = FastAPI(
    title="ScopeSentry API",
    description="API for detecting scope creep in client requests.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {
        "message": "Welcome to ScopeSentry API",
        "docs": "/docs",
    }


@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "application": "ScopeSentry",
    }


@app.post("/analyze", response_model=ScopeAnalysisResponse)
async def analyze(request: ScopeAnalysisRequest) -> ScopeAnalysisResponse:
    return await analyze_scope(request)
