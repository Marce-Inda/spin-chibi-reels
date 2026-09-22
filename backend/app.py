import time

def cleanup_old_files(directory: str, max_age_seconds: int = 3 * 24 * 3600):
    """Deletes output video files and cached assets older than 3 days (72 hours)."""
    now = time.time()
    if not os.path.exists(directory):
        return
    for filename in os.listdir(directory):
        filepath = os.path.join(directory, filename)
        if os.path.isfile(filepath):
            file_age = now - os.path.getmtime(filepath)
            if file_age > max_age_seconds:
                try:
                    os.remove(filepath)
                except Exception as e:
                    print(f"Error removing old file {filepath}: {e}")
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
    llm_model: Optional[str] = ""
    video_model: Optional[str] = ""

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
    if req.llm_model:
        config.LLM_MODEL = req.llm_model
    if req.video_model:
        config.VIDEO_MODEL = req.video_model
    return {"message": "Configuración de credenciales y modelos actualizada exitosamente."}

@app.post("/api/generate-story")
async def generate_story(req: StoryRequest):
    result = await StoryAgent.generate_story_and_script(user_idea=req.user_prompt, api_key=req.api_key)
    return result

@app.post("/api/generate-full-reel")
async def generate_full_reel(req: StoryRequest):
    """1-Click Generation: Generates story, script, prompts, and renders 9:16 Reel video in 1 request."""
    try:
        story_and_script = await StoryAgent.generate_story_and_script(user_idea=req.user_prompt, api_key=req.api_key)
        scenes = VisualDesignAgent.generate_prompts(story_and_script.get("scenes", []))
        output_file = await MediaEngine.assemble_reel(scenes, output_filename="casino_reel.mp4")
        return {
            "status": "success",
            "story_text": story_and_script.get("story_text", ""),
            "scenes": [s.model_dump() for s in scenes],
            "video_url": "/api/download-reel",
            "file_path": output_file
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en 1-Click Reel Generator: {str(e)}")

@app.post("/api/create-script")
async def create_script(req: ScriptRequest):
    scenes = await ScriptAgent.create_script(story_text=req.story_text, api_key=req.api_key)
    scenes_with_prompts = VisualDesignAgent.generate_prompts(scenes)
    return {"scenes": [s.model_dump() for s in scenes_with_prompts]}

@app.post("/api/render-reel")
async def render_reel(req: RenderRequest):
    try:
        cleanup_old_files(config.OUTPUT_DIR)
        cleanup_old_files(os.path.join(config.OUTPUT_DIR, "cache"))
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
