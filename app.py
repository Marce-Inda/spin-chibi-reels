import sys
import os

# Add backend directory to system path
sys.path.append(os.path.join(os.path.dirname(__file__), "backend"))

from backend.app import app

# Hugging Face Spaces ASGI entry point
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.app:app", host="0.0.0.0", port=7860, reload=False)
