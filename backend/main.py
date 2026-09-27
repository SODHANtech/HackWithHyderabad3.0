import os
from pathlib import Path
from typing import Dict, Any, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from pydantic import BaseModel

from backend.config import settings
from backend.services.hindsight_service import hindsight_service
from backend.orchestrator import orchestration_agent

app = FastAPI(
    title="Hindsight AI Website Architect API",
    description="Autonomous Website Builder with Hindsight Reflection & Self-Healing Loop",
    version="1.0.0"
)

# Enable CORS for local testing & preview
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class GenerateRequest(BaseModel):
    name: str = "Austin Smile Studio"
    category: str = "Dental Clinic"
    location: str = "Austin, TX"
    phone: str = "+1 (512) 555-0198"
    whatsapp: Optional[str] = "15125550198"
    services: Optional[str] = "Teeth Whitening, Dental Implants, Emergency Care"
    instructions: Optional[str] = None

class VoiceCommandRequest(BaseModel):
    transcript: str
    current_html: str
    business_data: Dict[str, Any]

class RetainRequest(BaseModel):
    content: str
    tags: Optional[list[str]] = None
    metadata: Optional[Dict[str, str]] = None

class RecallRequest(BaseModel):
    query: str
    tags: Optional[list[str]] = None

class ReflectRequest(BaseModel):
    query: str
    context: Optional[str] = None


@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "hindsight_connected": bool(hindsight_service.client),
        "hindsight_bank": settings.hindsight_bank_id,
        "groq_configured": settings.has_groq_credentials,
        "mode": "cloud" if hindsight_service.client else "local_resilient"
    }


@app.post("/api/generate")
def generate_website(req: GenerateRequest):
    """Run full pipeline: Intake -> Copy -> Design -> Code -> Critics -> Hindsight Reflection -> Healing"""
    try:
        biz_data = req.model_dump()
        result = orchestration_agent.run_pipeline(biz_data, initial_prompt=req.instructions)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/voice-command")
def process_voice_command(req: VoiceCommandRequest):
    """
    Process user voice instruction, retain command into Hindsight as user preference,
    and trigger self-correction re-generation.
    """
    try:
        # Retain the user's voice preference in Hindsight
        hindsight_service.retain(
            content=f"User voice instruction: '{req.transcript}'. Requested on business {req.business_data.get('name')}.",
            tags=["voice_command", "user_preference"],
            metadata={"type": "experience"}
        )

        # Reflect on how to apply the instruction
        patch_instruction = hindsight_service.reflect(
            query=f"How to modify website layout or features for request: {req.transcript}",
            context=f"Business: {req.business_data.get('name')}"
        )

        # Re-run pipeline with refined instruction
        biz_data = req.business_data
        result = orchestration_agent.run_pipeline(biz_data, initial_prompt=f"{req.transcript}. {patch_instruction}")
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/memories")
def get_memories():
    """Retrieve all active memories in the Hindsight bank"""
    return {
        "count": len(hindsight_service.get_all_memories()),
        "memories": hindsight_service.get_all_memories()
    }


@app.post("/api/retain")
def retain_endpoint(req: RetainRequest):
    """Direct retain endpoint"""
    return hindsight_service.retain(content=req.content, tags=req.tags, metadata=req.metadata)


@app.post("/api/recall")
def recall_endpoint(req: RecallRequest):
    """Direct recall endpoint using TEMPR search"""
    return hindsight_service.recall(query=req.query, tags=req.tags)


@app.post("/api/reflect")
def reflect_endpoint(req: ReflectRequest):
    """Direct reflect endpoint"""
    return {"reflection": hindsight_service.reflect(query=req.query, context=req.context)}


# Mount static frontend directory
STATIC_DIR = Path(__file__).resolve().parent.parent / "frontend"
if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

@app.get("/")
def serve_index():
    index_path = STATIC_DIR / "index.html"
    if index_path.exists():
        return FileResponse(index_path)
    return HTMLResponse("<h1>Hindsight Website Architect API is Running!</h1><p>Visit /docs for API specs.</p>")
