import os
from pydantic import BaseModel

class AppConfig(BaseModel):
    # API Keys for Cloud services
    OPENROUTER_API_KEY: str = os.getenv("OPENROUTER_API_KEY", "")
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    REPLICATE_API_KEY: str = os.getenv("REPLICATE_API_KEY", "")
    FAL_API_KEY: str = os.getenv("FAL_API_KEY", "")
    ELEVENLABS_API_KEY: str = os.getenv("ELEVENLABS_API_KEY", "")
    
    # Model preferences
    LLM_MODEL: str = os.getenv("LLM_MODEL", "google/gemini-2.5-flash")
    IMAGE_MODEL: str = os.getenv("IMAGE_MODEL", "black-forest-labs/flux-1.1-pro")
    TTS_VOICE: str = os.getenv("TTS_VOICE", "es-ES-AlvaroNeural")  # Spanish expressivity
    
    # Paths
    BASE_DIR: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    OUTPUT_DIR: str = os.path.join(BASE_DIR, "output")
    ASSETS_DIR: str = os.path.join(BASE_DIR, "assets")

config = AppConfig()
os.makedirs(config.OUTPUT_DIR, exist_ok=True)
os.makedirs(config.ASSETS_DIR, exist_ok=True)
