import json
import httpx
import asyncio
from typing import List, Dict, Any
from pydantic import BaseModel
from config import config

class Scene(BaseModel):
    id: int
    duration: float  # seconds
    narration: str   # Spanish voiceover text
    visual_description: str  # visual scene beat
    sound_effect: str  # e.g., 'slot_spin', 'oops_buzzer', 'jackpot_coins', 'cheer'
    text_overlay: str  # On-screen caption
    image_prompt: str = "" # Generated prompt by VisualDesignAgent

class StoryReel(BaseModel):
    title: str
    concept: str
    moral: str
    scenes: List[Scene]

# Baseline Master Style Prompt for consistent 3D Chibi Modern aesthetics
CHIBI_STYLE_BASELINE = (
    "3D chibi anime-inspired character, high quality 3D digital art rendering, "
    "huge expressive sparkling glossy eyes with star-like shine pupils, cute rosy cheeks, "
    "wearing modern fashionable stylish attire (sleek luxury blazer / chic hoodie), "
    "modern high-end casino setting, vibrant neon slot machines glowing in background, "
    "gold coins, cinematic lighting, 8k resolution, vertical 9:16 ratio"
)

class StoryAgent:
    """Generates funny casino stories featuring mistakes/blunders leading to a jackpot win."""
    
    @staticmethod
    async def generate_story(user_idea: str = "", api_key: str = "") -> Dict[str, Any]:
        prompt = (
            "Crea una micro-historia cómica e inspiradora para un Reel/TikTok (15 a 25 segundos) sobre un casino y tragamonedas.\n"
            "REQUISITO OBLIGATORIO: El personaje debe cometer una equivocación, torpeza o error gracioso "
            "(ejemplo: tropezarse y presionar el botón de Apuesta Máxima, estornudar y tocar la pantalla, "
            "confundir la tragamonedas con una máquina de peluches, etc.), pero esa equivocación desencadena "
            "de manera sorpresiva e imprevista el GRAN JACKPOT O PREMIO MAYOR.\n"
            "El tono debe ser muy divertido, lleno de emoción y con final súper feliz de victoria.\n\n"
            f"Idea base del usuario: '{user_idea if user_idea else 'Un día con suerte inesperada en el casino'}'"
        )
        
        effective_key = api_key or config.OPENROUTER_API_KEY or config.OPENAI_API_KEY
        
        if effective_key:
            try:
                async with httpx.AsyncClient(timeout=30.0) as client:
                    headers = {
                        "Authorization": f"Bearer {effective_key}",
                        "Content-Type": "application/json"
                    }
                    data = {
                        "model": config.LLM_MODEL,
                        "messages": [
                            {"role": "system", "content": "Eres un guionista experto en Reels cómicos virales de TikTok/Instagram para casinos y juegos."},
                            {"role": "user", "content": prompt}
                        ],
                        "temperature": 0.8
                    }
                    resp = await client.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=data)
                    if resp.status_code == 200:
                        content = resp.json()["choices"][0]["message"]["content"]
                        return {"story_text": content}
            except Exception as e:
                print(f"Error calling LLM API: {e}")
                
        # Fallback offline templates if API key is not provided yet
        return {
            "story_text": (
                "Un joven elegante entra al casino buscando una máquina tragamonedas. "
                "Al intentar tomar su bebida, tropieza accidentalmente y presiona con el codo el botón de 'APUESTA MÁXIMA'. "
                "Entra en pánico con los ojos abiertos de par en par... ¡pero la tragamonedas empieza a encender todas sus luces neón "
                "y estalla en una lluvia de monedas de oro entregándole el Jackpot de $100,000!"
            )
        }

class ScriptAgent:
    """Transforms a story into a structured scene-by-scene Reel script."""
    
    @staticmethod
    async def create_script(story_text: str, api_key: str = "") -> List[Scene]:
        effective_key = api_key or config.OPENROUTER_API_KEY or config.OPENAI_API_KEY
        
        if effective_key:
            system_prompt = (
                "Eres un director de cine corto. Convierte la historia en exactamente 4 o 5 escenas breves en formato JSON.\n"
                "Formato JSON requerido (lista de objetos):\n"
                "[\n"
                "  {\n"
                "    \"id\": 1,\n"
                "    \"duration\": 4.0,\n"
                "    \"narration\": \"Texto en español corto para voz en off\",\n"
                "    \"visual_description\": \"Descripción visual del personaje 3D chibi y su acción graciosa\",\n"
                "    \"sound_effect\": \"slot_spin / oops_buzzer / panic_gasp / jackpot_coins / cheer\",\n"
                "    \"text_overlay\": \"SUBTÍTULO EN MAYÚSCULAS PARA PANTALLA\"\n"
                "  }\n"
                "]"
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
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": f"Historia:\n{story_text}"}
                        ],
                        "response_format": {"type": "json_object"}
                    }
                    resp = await client.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=data)
                    if resp.status_code == 200:
                        raw_json = resp.json()["choices"][0]["message"]["content"]
                        parsed = json.loads(raw_json)
                        scenes_data = parsed if isinstance(parsed, list) else parsed.get("scenes", [])
                        return [Scene(**s) for s in scenes_data]
            except Exception as e:
                print(f"Script parsing error: {e}")

        # Structured default scenes with funny mistake + jackpot win
        return [
            Scene(
                id=1,
                duration=4.0,
                narration="Entré al casino con toda la actitud y mis mejores ropas modernas...",
                visual_description="Cute 3D chibi character in fashionable modern luxury attire stepping into a bright futuristic casino, looking confident with huge sparkling eyes.",
                sound_effect="casino_ambient",
                text_overlay="¡ENTRANDO AL CASINO CON ACTITUD! 🎰✨"
            ),
            Scene(
                id=2,
                duration=3.5,
                narration="Iba a presionar el botón de 1 dólar, pero por voltear a ver un cocktail...",
                visual_description="Chibi character holding a soda cup, getting distracted and looking sideways with an exaggerated funny blush reaction.",
                sound_effect="oops_buzzer",
                text_overlay="¡OH NO! ¡ME DISTRAJE! 🍹😅"
            ),
            Scene(
                id=3,
                duration=4.0,
                narration="¡Tropecé y presioné el botón de APUESTA MÁXIMA por error!",
                visual_description="Chibi character slipping funny and slamming hands onto the red glowing MAX BET button of a slot machine, eyes popping out in hilarious shock.",
                sound_effect="panic_gasp",
                text_overlay="¡PRESIONÉ APUESTA MÁXIMA POR ERROR! 😱💥"
            ),
            Scene(
                id=4,
                duration=5.0,
                narration="¡Y la máquina estalló en luces neón regalándome el JACKPOT DE SU VIDA!",
                visual_description="The slot machine flashes 777 GOLDEN JACKPOT, golden coins fountain spraying everywhere, chibi character crying tears of happiness with star pupil eyes celebrating wildly.",
                sound_effect="jackpot_coins",
                text_overlay="¡¡¡GANAMOS EL JACKPOT DE $100,000!!! 🎉💰🏆"
            )
        ]

class VisualDesignAgent:
    """Enriches visual descriptions with modern 3D chibi style parameters."""
    
    @staticmethod
    def generate_prompts(scenes: List[Scene]) -> List[Scene]:
        for scene in scenes:
            scene.image_prompt = f"{scene.visual_description}, {CHIBI_STYLE_BASELINE}"
        return scenes
