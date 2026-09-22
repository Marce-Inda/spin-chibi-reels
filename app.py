import sys
import os

# Top-level ZeroGPU requirement check for Hugging Face Spaces AST parser
try:
    import spaces
    @spaces.GPU
    def zero_gpu_render_function(data: str):
        return data
except Exception:
    def zero_gpu_render_function(data: str):
        return data

# Bulletproof patch for Hugging Face Spaces environment (HfFolder deprecation fix)
try:
    import huggingface_hub
    if not hasattr(huggingface_hub, "HfFolder"):
        class HfFolder:
            @staticmethod
            def get_token():
                return os.getenv("HF_TOKEN", None)
            @staticmethod
            def save_token(token):
                pass
        huggingface_hub.HfFolder = HfFolder
except Exception as e:
    print("Patching HfFolder warning:", e)

# Add backend directory to system path
sys.path.append(os.path.join(os.path.dirname(__file__), "backend"))

import gradio as gr
from backend.app import app as fastapi_app

# Create a clean Gradio interface wrapper for Hugging Face Spaces free tier
with gr.Blocks(title="CasinoReels.AI") as demo:
    gr.HTML(
        """
        <div style="text-align: center; padding: 20px; background: #090714; border-radius: 12px; font-family: sans-serif;">
            <h1 style="color: #ffd700; font-size: 2.2rem; margin-bottom: 5px;">🎰 CasinoReels.AI</h1>
            <p style="color: #00f5d4; font-size: 1rem;">Sistema Autónomo Multi-Agente de Reels/TikToks de Casino (3D Chibi)</p>
            <p style="margin-top: 15px;">
                <a href="/" target="_self" style="background: linear-gradient(135deg, #ffb703, #ffd700); color: #1a1000; padding: 14px 28px; border-radius: 8px; text-decoration: none; font-weight: bold; font-size: 1.1rem; display: inline-block; box-shadow: 0 4px 15px rgba(255,215,0,0.4);">
                    🚀 Abrir Panel de Control Completo (Dashboard HD 9:16)
                </a>
            </p>
        </div>
        """
    )

# Mount FastAPI app onto Gradio (Hugging Face Spaces compatible)
app = gr.mount_gradio_app(fastapi_app, demo, path="/gradio")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7860)
