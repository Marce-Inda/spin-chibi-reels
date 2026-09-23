import os
import sys
import time
import asyncio

# Ensure backend directory is in python sys.path
backend_dir = os.path.dirname(os.path.abspath(__file__))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Dict, Any, Optional

from config import config
from agents import StoryAgent, ScriptAgent, VisualDesignAgent, Scene, COMEDY_CASINO_PREMISES
from media_engine import MediaEngine

app = FastAPI(title="Casino Reels Agent System API", version="2.0.0")

# Serve frontend static assets
FRONTEND_DIR = os.path.join(config.BASE_DIR, "frontend")
OUTPUT_DIR = config.OUTPUT_DIR

def cleanup_old_files(directory: str, max_age_seconds: int = config.RETENTION_SECONDS):
    """Deletes ONLY final rendered video files (.mp4) older than 15 days, permanently preserving reusable audio/visual assets in cache."""
    now = time.time()
    if not os.path.exists(directory):
        return
    for filename in os.listdir(directory):
        filepath = os.path.join(directory, filename)
        # Only clean final .mp4 videos, preserve all reusable cache assets
        if os.path.isfile(filepath) and filename.endswith(".mp4"):
            file_age = now - os.path.getmtime(filepath)
            if file_age > max_age_seconds:
                try:
                    os.remove(filepath)
                    print(f"🗑️ Cleaned up old reel video: {filename}")
                except Exception as e:
                    print(f"Error removing old file {filepath}: {e}")

# Global Batch State for Observability Dashboard
batch_state = {
    "is_running": False,
    "current_index": 0,
    "total_reels": 20,
    "completed_reels": [],
    "logs": [],
    "total_tokens_used": 0,
    "total_cost_usd": 0.0,
    "start_time": 0.0,
    "elapsed_seconds": 0.0
}

class StoryRequest(BaseModel):
    user_prompt: Optional[str] = ""
    api_key: Optional[str] = ""

class BatchRequest(BaseModel):
    total_reels: Optional[int] = 20
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

async def run_batch_generation_task(total_reels: int, api_key: str):
    """Background task to generate N (default 20) complete Reels sequentially with live logging & cost tracking."""
    global batch_state
    batch_state["is_running"] = True
    batch_state["current_index"] = 0
    batch_state["total_reels"] = total_reels
    batch_state["completed_reels"] = []
    batch_state["logs"] = []
    batch_state["total_tokens_used"] = 0
    batch_state["total_cost_usd"] = 0.0
    batch_state["start_time"] = time.time()

    cleanup_old_files(OUTPUT_DIR)
    cleanup_old_files(os.path.join(OUTPUT_DIR, "cache"))

    for i in range(total_reels):
        reel_num = i + 1
        batch_state["current_index"] = reel_num
        start_reel_time = time.time()
        
        batch_state["logs"].append(f"[{time.strftime('%H:%M:%S')}] 🎬 Reel #{reel_num}/{total_reels}: Generando historia y guion con IA...")

        def log_scene_step(sub_msg: str):
            batch_state["logs"].append(f"[{time.strftime('%H:%M:%S')}] ⚙️ Reel #{reel_num}/{total_reels}: {sub_msg}")

        try:
            # 1. Generate Story & Scenes
            story_res = await StoryAgent.generate_story_and_script(api_key=api_key, index=i)
            scenes = VisualDesignAgent.generate_prompts(story_res.get("scenes", []))
            
            tokens = story_res.get("tokens_used", 450)
            cost = story_res.get("cost_usd", 0.00015)
            
            # 2. Render Video Reel (Sequential Scene Processing to stay under 512MB RAM)
            filename = f"reel_batch_{reel_num}.mp4"
            output_path = await MediaEngine.assemble_reel(scenes, output_filename=filename, log_callback=log_scene_step)
            duration_rendered = round(time.time() - start_reel_time, 2)

            batch_state["total_tokens_used"] += tokens
            batch_state["total_cost_usd"] += cost

            reel_data = {
                "id": reel_num,
                "title": f"Reel #{reel_num} — {COMEDY_CASINO_PREMISES[i % len(COMEDY_CASINO_PREMISES)][:30]}...",
                "story": story_res.get("story_text", ""),
                "video_url": f"/api/download-reel-by-name/{filename}",
                "file_path": output_path,
                "render_time_sec": duration_rendered,
                "tokens_used": tokens,
                "cost_usd": cost
            }
            batch_state["completed_reels"].append(reel_data)
            batch_state["logs"].append(f"[{time.strftime('%H:%M:%S')}] ✅ Reel #{reel_num}/{total_reels} completado en {duration_rendered}s. Costo est: ${cost:.5f}")
        except Exception as e:
            batch_state["logs"].append(f"[{time.strftime('%H:%M:%S')}] ❌ Error en Reel #{reel_num}: {str(e)}")

        batch_state["elapsed_seconds"] = round(time.time() - batch_state["start_time"], 2)

    batch_state["is_running"] = False
    batch_state["logs"].append(f"[{time.strftime('%H:%M:%S')}] 🎉 ¡Lote de {total_reels} Reels completado con éxito! Costo total: ${batch_state['total_cost_usd']:.5f}")

@app.get("/api/health")
def health_check():
    return {
        "status": "online",
        "has_openrouter": bool(config.OPENROUTER_API_KEY or config.OPENAI_API_KEY),
        "retention_days": config.RETENTION_DAYS,
        "output_dir": config.OUTPUT_DIR
    }

@app.post("/api/start-batch")
async def start_batch(req: BatchRequest, background_tasks: BackgroundTasks):
    if batch_state["is_running"]:
        return {"status": "running", "message": "Ya hay una sesión de lotes en ejecución."}
    
    total = req.total_reels or 20
    background_tasks.add_task(run_batch_generation_task, total, req.api_key)
    return {"status": "started", "message": f"Sesión de {total} Reels iniciada en segundo plano."}

@app.get("/api/batch-status")
def get_batch_status():
    if batch_state["is_running"]:
        batch_state["elapsed_seconds"] = round(time.time() - batch_state["start_time"], 2)
    return batch_state

@app.get("/api/observability-stats")
def get_observability_stats():
    """Returns disk usage, file count, retention policy metrics, and session cost statistics."""
    total_size_bytes = 0
    file_count = 0
    
    if os.path.exists(OUTPUT_DIR):
        for root, dirs, files in os.walk(OUTPUT_DIR):
            for f in files:
                fp = os.path.join(root, f)
                total_size_bytes += os.path.getsize(fp)
                if f.endswith(".mp4"):
                    file_count += 1
                    
    size_mb = round(total_size_bytes / (1024 * 1024), 2)
    
    return {
        "stored_reels_count": file_count,
        "disk_used_mb": size_mb,
        "retention_days": config.RETENTION_DAYS,
        "retention_policy": "Archivos conservados durante 15 días (360 horas) antes de borrado automático",
        "current_session_cost_usd": round(batch_state["total_cost_usd"], 5),
        "total_tokens_used": batch_state["total_tokens_used"],
        "cost_per_reel_avg_usd": round(batch_state["total_cost_usd"] / max(len(batch_state["completed_reels"]), 1), 6)
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
        cleanup_old_files(OUTPUT_DIR)
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

@app.get("/api/download-reel-by-name/{filename}")
def download_reel_by_name(filename: str):
    reel_path = os.path.join(OUTPUT_DIR, filename)
    if not os.path.exists(reel_path):
        raise HTTPException(status_code=404, detail=f"El archivo {filename} no existe.")
    return FileResponse(reel_path, media_type="video/mp4", filename=filename)

# Mount static frontend directory
app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")
