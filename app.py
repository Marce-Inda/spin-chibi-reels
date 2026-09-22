import sys
import os

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
        <div style="text-align: center; padding: 25px; background: #090714; border-radius: 16px; font-family: 'Plus Jakarta Sans', sans-serif;">
            <h1 style="color: #ffd700; font-size: 2.5rem; margin-bottom: 8px;">🎰 CasinoReels.AI</h1>
            <p style="color: #00f5d4; font-size: 1.1rem; margin-bottom: 20px;">Sistema Autónomo Multi-Agente de Reels/TikToks de Casino (3D Chibi)</p>
            <a href="/" target="_self" style="background: linear-gradient(135deg, #ffb703, #ffd700); color: #1a1000; padding: 16px 32px; border-radius: 10px; text-decoration: none; font-weight: 800; font-size: 1.2rem; display: inline-block; box-shadow: 0 6px 20px rgba(255,215,0,0.5);">
                🚀 Abrir Panel de Control Completo (Dashboard HD 9:16)
            </a>
        </div>
        """
    )

# Mount FastAPI app onto Gradio (Hugging Face Spaces compatible)
app = gr.mount_gradio_app(fastapi_app, demo, path="/gradio")

# Launch Gradio server continuously for Hugging Face Spaces
if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860)
