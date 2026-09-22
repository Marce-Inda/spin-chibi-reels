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
    LLM_MODEL: str = os.getenv("LLM_MODEL", "deepseek/deepseek-chat")
    IMAGE_MODEL: str = os.getenv("IMAGE_MODEL", "fal-ai/flux/schnell")
    VIDEO_MODEL: str = os.getenv("VIDEO_MODEL", "fal-ai/minimax-video")
    
    TTS_VOICE: str = os.getenv("TTS_VOICE", "es-ES-AlvaroNeural")
    
    # Retention period (15 days in seconds)
    RETENTION_DAYS: int = 15
    RETENTION_SECONDS: int = 15 * 24 * 3600
    
    # Pricing estimates (USD per 1M tokens / per generation)
    DEEPSEEK_COST_PER_1K_TOKENS: float = 0.00015  # ~$0.15 / 1M tokens
    FAL_IMAGE_COST_PER_SCENE: float = 0.003
    EDGE_TTS_COST: float = 0.0  # Free
    
    # Paths
    BASE_DIR: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    OUTPUT_DIR: str = os.path.join(BASE_DIR, "output")
    ASSETS_DIR: str = os.path.join(BASE_DIR, "assets")

config = AppConfig()
os.makedirs(config.OUTPUT_DIR, exist_ok=True)
os.makedirs(config.ASSETS_DIR, exist_ok=True)
