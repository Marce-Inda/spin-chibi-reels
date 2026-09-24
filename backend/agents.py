import os
import sys
import json
import httpx
import random
from typing import List, Dict, Any, Optional
from pydantic import BaseModel

backend_dir = os.path.dirname(os.path.abspath(__file__))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from config import config

class Scene(BaseModel):
    id: int
    duration: float
    narration: str
    visual_description: str
    sound_effect: str
    text_overlay: str
    image_prompt: str = ""

# List of 20 creative comedy casino blunder premises
COMEDY_CASINO_PREMISES = [
    "Tropecé bailando de felicidad y presioné la Apuesta Máxima con la rodilla",
    "Estornudé tan fuerte que mi frente tocó la pantalla en la máquina de 777",
    "Confundí la tragamonedas con una máquina expendedora de sodas",
    "Traté de tomarme una selfie y se me cayó el teléfono sobre el botón rojo",
    "Estaba aplaudiendo por la suerte de otro y le pegué a la palanca equivocada",
    "Intenté limpiar un chicle de la pantalla y activé el giro estelar",
    "Buscaba mis lentes en el bolsillo y apreté la pantalla de Apuesta Máxima",
    "Se me cayó una ficha de oro, me agaché a buscarla y golpeé la máquina ganadora",
    "Apreté el botón al ritmo de la música del casino sin mirar la pantalla",
    "Pensé que la máquina estaba apagada y le di un golpecito de suerte",
    "Solté mi vaso de coctel de la impresión y cayó justo en el botón de Spin",
    "Estaba saludando a un amigo a lo lejos y mi codo presionó la tragamonedas",
    "Confundí la máquina de peluches con la tragamonedas de Jackpot",
    "Iba a apostar 50 centavos y por no traer lentes le puse $50 de golpe",
    "Giré para ver el reloj y mi codo activó la ráfaga de giros dorados",
    "Mi amuleto de la suerte cayó sobre la pantalla táctil en el momento exacto",
    "Me asustó el sonido de otra máquina y salté presionando el botón rojo",
    "Iba a sentarme, fallé la silla y al agarrarme de la máquina activé el Jackpot",
    "Intenté ajustar mi chaqueta elegante y el puño rozó el botón de Max Bet",
    "Le pedí permiso a la máquina con una reverencia y al levantarme toqué el Spin"
]

CHIBI_STYLE_BASELINE = (
    "3D chibi anime-inspired character, high quality 3D digital art rendering, "
    "huge expressive sparkling glossy eyes with star-like shine pupils, cute rosy cheeks, "
    "wearing modern fashionable stylish attire (sleek luxury blazer / chic hoodie), "
    "modern high-end casino setting, vibrant neon slot machines glowing in background, "
    "gold coins, cinematic lighting, 8k resolution, vertical 9:16 ratio"
)

from script_database import get_script_by_index, VIRAL_CASINO_SCRIPTS, MASTER_CHIBI_STYLE

def find_matching_script(user_idea: str) -> Optional[dict]:
    """Matches a user prompt or preset chip directly to a script in the 30-script database."""
    idea = user_idea.lower().strip()
    if not idea:
        return None
    for script in VIRAL_CASINO_SCRIPTS:
        if script["title"].lower() in idea or script["story_text"].lower() in idea or script["category"].lower() in idea:
            return script
        if "peluche" in idea or "peluches" in idea:
            if script["id"] == 8:
                return script
        if "soda" in idea or "bebida" in idea or "refresco" in idea:
            if script["id"] == 7:
                return script
        if "estornud" in idea:
            if script["id"] == 1:
                return script
        if "tropez" in idea or "tropece" in idea or "baile" in idea:
            if script["id"] == 2:
                return script
    return None

class StoryAgent:
    """Generates funny casino stories featuring blunders leading to jackpot wins."""
    
    @staticmethod
    async def generate_story_and_script(user_idea: str = "", api_key: str = "", index: int = 0) -> Dict[str, Any]:
        """Loads curated AAA scripts from script_database or generates via LLM with 3D Chibi master prompts."""
        # 1. Check if user prompt matches a script in our 30-script database
        matched_script = find_matching_script(user_idea) if user_idea.strip() else None
        
        if matched_script or not user_idea.strip():
            script_data = matched_script or get_script_by_index(index)
            scenes = [
                Scene(
                    id=s["id"],
                    duration=s["duration"],
                    narration=s["narration"],
                    visual_description=s["visual_description"],
                    sound_effect=s["sound_effect"],
                    text_overlay=s["text_overlay"],
                    image_prompt=s["image_prompt"]
                )
                for s in script_data["scenes"]
            ]
            return {
                "story_text": script_data["story_text"],
                "scenes": scenes,
                "tokens_used": 0,
                "cost_usd": 0.0
            }

        # 2. If no exact database match, fallback to LLM generation
        effective_key = api_key or config.OPENROUTER_API_KEY or config.OPENAI_API_KEY
        if effective_key:
            prompt = (
                f"Crea un guion completo de Reel/TikTok (15-20s) cómico para casino.\n"
                f"PREMISA CÓMICA: '{user_idea}'.\n"
                "REQUISITO: La equivocación graciosa debe resultar en el GRAN JACKPOT DE $100,000.\n\n"
                "Devuelve la respuesta estrictamente en este formato JSON:\n"
                "{\n"
                "  \"story_text\": \"Resumen de la historia en 2 oraciones\",\n"
                "  \"scenes\": [\n"
                "    {\n"
                "      \"id\": 1,\n"
                "      \"duration\": 4.0,\n"
                "      \"narration\": \"Texto en español para voz en off\",\n"
                "      \"visual_description\": \"Detailed 3D chibi character in gala tuxedo...\",\n"
                "      \"sound_effect\": \"slot_spin / oops_buzzer / panic_gasp / jackpot_coins\",\n"
                "      \"text_overlay\": \"¡SUBTÍTULO EN MAYÚSCULAS!\"\n"
                "    }\n"
                "  ]\n"
                "}"
            )
            try:
                async with httpx.AsyncClient(timeout=30.0) as client:
                    headers = {
                        "Authorization": f"Bearer {effective_key}",
                        "Content-Type": "application/json"
                    }
                    data = {
                        "model": config.LLM_MODEL,
                        "messages": [
                            {"role": "system", "content": "Eres un director de cine corto viral para TikTok/Reels estilo 3D Chibi Pixar."},
                            {"role": "user", "content": prompt}
                        ],
                        "response_format": {"type": "json_object"},
                        "temperature": 0.85
                    }
                    resp = await client.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=data)
                    if resp.status_code == 200:
                        json_resp = resp.json()
                        usage = json_resp.get("usage", {})
                        tokens_used = usage.get("total_tokens", 500)
                        raw = json_resp["choices"][0]["message"]["content"]
                        parsed = json.loads(raw)
                        scenes = [
                            Scene(
                                id=s["id"],
                                duration=s.get("duration", 4.0),
                                narration=s.get("narration", ""),
                                visual_description=s.get("visual_description", ""),
                                sound_effect=s.get("sound_effect", "slot_spin"),
                                text_overlay=s.get("text_overlay", ""),
                                image_prompt=f"{s.get('visual_description', '')}, {MASTER_CHIBI_STYLE}"
                            )
                            for s in parsed.get("scenes", [])
                        ]
                        cost_est = (tokens_used / 1000.0) * config.DEEPSEEK_COST_PER_1K_TOKENS
                        return {
                            "story_text": parsed.get("story_text", ""),
                            "scenes": scenes,
                            "tokens_used": tokens_used,
                            "cost_usd": round(cost_est, 6)
                        }
            except Exception as e:
                print(f"Error in story LLM generation: {e}")

        # Fallback to curated script 0
        script_data = VIRAL_CASINO_SCRIPTS[0]
        scenes = [Scene(**s) for s in script_data["scenes"]]
        return {
            "story_text": f"Premisa: {user_idea}. " + script_data["story_text"],
            "scenes": scenes,
            "tokens_used": 0,
            "cost_usd": 0.0
        }

class ScriptAgent:
    @staticmethod
    async def create_script(story_text: str, api_key: str = "") -> List[Scene]:
        res = await StoryAgent.generate_story_and_script(user_idea=story_text, api_key=api_key)
        return res.get("scenes", [])

class VisualDesignAgent:
    @staticmethod
    def generate_prompts(scenes: List[Scene]) -> List[Scene]:
        for scene in scenes:
            if not scene.image_prompt:
                scene.image_prompt = f"{scene.visual_description}, {MASTER_CHIBI_STYLE}"
        return scenes
