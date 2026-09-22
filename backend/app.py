import os
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Dict, Any, Optional

from config import config
from agents import StoryAgent, ScriptAgent, VisualDesignAgent, Scene
from media_engine import MediaEngine

app = FastAPI(title="Casino Reels Agent System API", version="1.0.0")

# Serve frontend static assets
FRONTEND_DIR = os.path.join(config.BASE_DIR, "frontend")
OUTPUT_DIR = config.OUTPUT_DIR

class StoryRequest(BaseModel):
    user_prompt: Optional[str] = ""
    api_key: Optional[str] = ""

class ScriptRequest(BaseModel):
    story_text: str
    api_key: Optional[str] = ""

class RenderRequest(BaseModel):
    scenes: List[Scene]

class ConfigUpdateRequest(BaseModel):
    openrouter_key: Optional[str] = ""
    replicate_key: Optional[str] = ""
    fal_key: Optional[str] = ""
    elevenlabs_key: Optional[str] = ""

@app.get("/api/health")
def health_check():
    return {
        "status": "online",
        "has_openrouter": bool(config.OPENROUTER_API_KEY or config.OPENAI_API_KEY),
        "has_replicate": bool(config.REPLICATE_API_KEY),
        "has_fal": bool(config.FAL_API_KEY),
        "output_dir": config.OUTPUT_DIR
    }

@app.post("/api/update-config")
def update_configuration(req: ConfigUpdateRequest):
    if req.openrouter_key:
        config.OPENROUTER_API_KEY = req.openrouter_key
    if req.replicate_key:
        config.REPLICATE_API_KEY = req.replicate_key
    if req.fal_key:
        config.FAL_API_KEY = req.fal_key
    if req.elevenlabs_key:
        config.ELEVENLABS_API_KEY = req.elevenlabs_key
    return {"message": "Configuración de credenciales actualizada exitosamente."}

@app.post("/api/generate-story")
async def generate_story(req: StoryRequest):
    result = await StoryAgent.generate_story(user_idea=req.user_prompt, api_key=req.api_key)
    return result

@app.post("/api/create-script")
async def create_script(req: ScriptRequest):
    scenes = await ScriptAgent.create_script(story_text=req.story_text, api_key=req.api_key)
    scenes_with_prompts = VisualDesignAgent.generate_prompts(scenes)
    return {"scenes": [s.model_dump() for s in scenes_with_prompts]}

@app.post("/api/render-reel")
async def render_reel(req: RenderRequest):
    try:
        output_file = await MediaEngine.assemble_reel(req.scenes, output_filename="casino_reel.mp4")
        return {
            "status": "success",
            "video_url": "/api/download-reel",
            "file_path": output_file
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error durante el renderizado del video: {str(e)}")

@app.get("/api/download-reel")
def download_reel():
    reel_path = os.path.join(OUTPUT_DIR, "casino_reel.mp4")
    if not os.path.exists(reel_path):
        raise HTTPException(status_code=404, detail="El archivo de Reel no existe. Genera uno primero.")
    return FileResponse(reel_path, media_type="video/mp4", filename="casino_reel_916.mp4")

# Mount static frontend directory
app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")
