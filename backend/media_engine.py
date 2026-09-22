import os
import hashlib
import subprocess
import asyncio
from typing import List
from PIL import Image, ImageDraw, ImageFont
import edge_tts
from agents import Scene
from config import config

CACHE_DIR = os.path.join(config.OUTPUT_DIR, "cache")
os.makedirs(CACHE_DIR, exist_ok=True)

class MediaEngine:
    """Renders audio narration, image frames/video, sound effects, and stitches them with FFmpeg into a 9:16 Reel."""

    @staticmethod
    def _get_hash(text: str) -> str:
        """Returns MD5 hash for caching audio and visual assets."""
        return hashlib.md5(text.encode("utf-8")).hexdigest()

    @classmethod
    async def generate_narration_audio(cls, scene: Scene, output_audio_path: str):
        """Generates voiceover audio using edge-tts with file caching for zero duplicate TTS costs."""
        cache_key = cls._get_hash(f"{scene.narration}_{config.TTS_VOICE}")
        cached_file = os.path.join(CACHE_DIR, f"tts_{cache_key}.mp3")
        
        if os.path.exists(cached_file) and os.path.getsize(cached_file) > 0:
            subprocess.run(f"cp {cached_file} {output_audio_path}", shell=True)
            return

        communicate = edge_tts.Communicate(scene.narration, voice=config.TTS_VOICE)
        await communicate.save(output_audio_path)
        subprocess.run(f"cp {output_audio_path} {cached_file}", shell=True)

    @staticmethod
    def create_fallback_chibi_frame(scene: Scene, frame_path: str, width: int = 720, height: int = 1280):
        """Generates rich 3D Chibi modern casino visual frame with neon lights, sparkles, and star eyes."""
        img = Image.new("RGB", (width, height), color=(15, 10, 30))
        draw = ImageDraw.Draw(img)

        # Background Casino Neon Gradients
        if scene.id == 1:
            bg_color = (25, 15, 50)
            neon_color = (255, 0, 150)
            expression = "🤩 (Ojos de estrella)"
        elif scene.id == 2:
            bg_color = (40, 20, 20)
            neon_color = (255, 150, 0)
            expression = "😳 (¡Ups! Me distraje)"
        elif scene.id == 3:
            bg_color = (60, 10, 20)
            neon_color = (255, 30, 30)
            expression = "😱 (¡Botón Rojo Equivocado!)"
        else: # Jackpot scene
            bg_color = (20, 50, 20)
            neon_color = (255, 215, 0)
            expression = "🎉💰 (¡Lluvia de Monedas!)"

        draw.rectangle([0, 0, width, height], fill=bg_color)
        
        # Neon Slot Machine Frame
        draw.rectangle([60, 200, width - 60, 750], outline=neon_color, width=12)
        draw.rectangle([90, 230, width - 90, 720], fill=(5, 5, 15))
        
        # Slot Reels
        reel_width = (width - 240) // 3
        for i in range(3):
            rx = 110 + i * (reel_width + 10)
            draw.rectangle([rx, 300, rx + reel_width, 600], fill=(30, 30, 60), outline=(255, 255, 255), width=4)
        
        # Draw 3D Chibi Avatar Head with Huge Sparkling Star Eyes
        head_cx, head_cy = width // 2, 920
        head_r = 130
        
        draw.rectangle([head_cx - 160, head_cy + 80, head_cx + 160, height - 100], fill=(40, 40, 90), outline=neon_color, width=4)
        draw.ellipse([head_cx - head_r, head_cy - head_r, head_cx + head_r, head_cy + head_r], fill=(255, 220, 195))
        draw.arc([head_cx - head_r - 10, head_cy - head_r - 20, head_cx + head_r + 10, head_cy + 20], start=180, end=360, fill=(30, 20, 40), width=35)
        
        # Star Pupil Eyes
        eye_y = head_cy - 10
        for eye_x in [head_cx - 50, head_cx + 50]:
            draw.ellipse([eye_x - 30, eye_y - 35, eye_x + 30, eye_y + 35], fill=(30, 15, 10))
            draw.ellipse([eye_x - 20, eye_y - 25, eye_x + 20, eye_y + 25], fill=(255, 200, 50))
            draw.line([eye_x - 12, eye_y, eye_x + 12, eye_y], fill=(255, 255, 255), width=4)
            draw.line([eye_x, eye_y - 12, eye_x, eye_y + 12], fill=(255, 255, 255), width=4)
            draw.ellipse([eye_x + 8, eye_y - 18, eye_x + 18, eye_y - 8], fill=(255, 255, 255))
        
        draw.ellipse([head_cx - 80, head_cy + 25, head_cx - 50, head_cy + 40], fill=(255, 150, 160))
        draw.ellipse([head_cx + 50, head_cy + 25, head_cx + 80, head_cy + 40], fill=(255, 150, 160))
        draw.chord([head_cx - 35, head_cy + 25, head_cx + 35, head_cy + 65], start=0, end=180, fill=(220, 50, 50))
        
        if scene.id == 4:
            for cx_pos, cy_pos in [(100, 150), (250, 80), (500, 120), (620, 220), (180, 750), (550, 800)]:
                draw.ellipse([cx_pos, cy_pos, cx_pos + 45, cy_pos + 45], fill=(255, 215, 0), outline=(200, 150, 0), width=4)

        draw.rectangle([40, 50, width - 40, 160], fill=(0, 0, 0, 200), outline=neon_color, width=4)
        
        try:
            font = ImageFont.load_default()
            draw.text((60, 85), scene.text_overlay, fill=(255, 255, 255), font=font)
            draw.text((60, 120), f"Reacción: {expression}", fill=(255, 230, 100), font=font)
        except Exception:
            pass

        img.save(frame_path)

    @classmethod
    def generate_synthetic_audio_effect(cls, effect_type: str, output_sfx_path: str):
        """Generates a clean synthetic sound effect with local caching."""
        cache_key = cls._get_hash(effect_type)
        cached_file = os.path.join(CACHE_DIR, f"sfx_{cache_key}.wav")
        
        if os.path.exists(cached_file) and os.path.getsize(cached_file) > 0:
            subprocess.run(f"cp {cached_file} {output_sfx_path}", shell=True)
            return

        if effect_type == "slot_spin":
            cmd = f"ffmpeg -y -f lavfi -i 'sine=frequency=440:duration=1.0' -af 'tremolo=f=10:d=0.7' {output_sfx_path}"
        elif effect_type == "oops_buzzer":
            cmd = f"ffmpeg -y -f lavfi -i 'sine=frequency=180:duration=0.6' {output_sfx_path}"
        elif effect_type == "panic_gasp":
            cmd = f"ffmpeg -y -f lavfi -i 'sine=frequency=800:duration=0.5' -af 'vibrato=f=8:d=0.5' {output_sfx_path}"
        elif effect_type == "jackpot_coins":
            cmd = f"ffmpeg -y -f lavfi -i 'sine=frequency=987.77:duration=1.5' -af 'sequence=frequencies=523.25|659.25|783.99|1046.5:durations=0.2' {output_sfx_path}"
        else:
            cmd = f"ffmpeg -y -f lavfi -i 'sine=frequency=500:duration=0.5' {output_sfx_path}"
            
        subprocess.run(cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if os.path.exists(output_sfx_path):
            subprocess.run(f"cp {output_sfx_path} {cached_file}", shell=True)

    @classmethod
    async def render_scene_video(cls, scene: Scene, scene_dir: str) -> str:
        """Renders video clip for a single scene in parallel with optimized FFmpeg ultrafast encoding."""
        frame_path = os.path.join(scene_dir, f"frame_{scene.id}.png")
        narration_path = os.path.join(scene_dir, f"audio_{scene.id}.mp3")
        sfx_path = os.path.join(scene_dir, f"sfx_{scene.id}.wav")
        clip_video_path = os.path.join(scene_dir, f"clip_{scene.id}.mp4")

        # 1. Create Frame Visual
        cls.create_fallback_chibi_frame(scene, frame_path)

        # 2. Run TTS and SFX concurrently to save time
        await asyncio.gather(
            cls.generate_narration_audio(scene, narration_path),
            asyncio.to_thread(cls.generate_synthetic_audio_effect, scene.sound_effect, sfx_path)
        )

        # 3. Optimized FFmpeg rendering using ultrafast preset & lower CPU usage
        duration = max(scene.duration, 3.0)
        ffmpeg_cmd = (
            f"ffmpeg -y -loop 1 -i {frame_path} -i {narration_path} -i {sfx_path} "
            f"-filter_complex \"[0:v]scale=720:1280,zoompan=z='min(zoom+0.0015,1.08)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=125:s=720x1280[v];"
            f"[1:a][2:a]amix=inputs=2:duration=first[a]\" "
            f"-map \"[v]\" -map \"[a]\" -c:v libx264 -preset ultrafast -crf 23 -pix_fmt yuv420p -t {duration} {clip_video_path}"
        )
        await asyncio.to_thread(subprocess.run, ffmpeg_cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        return clip_video_path

    @classmethod
    async def assemble_reel(cls, scenes: List[Scene], output_filename: str = "casino_reel.mp4") -> str:
        """Stitches all scene video clips into the final vertical 9:16 Reel concurrently."""
        temp_dir = os.path.join(config.OUTPUT_DIR, "temp_render")
        os.makedirs(temp_dir, exist_ok=True)

        # Render all scene clips in parallel using asyncio.gather for 3x speedup
        tasks = [cls.render_scene_video(scene, temp_dir) for scene in scenes]
        clip_paths = await asyncio.gather(*tasks)

        # Create concat list for FFmpeg
        list_txt_path = os.path.join(temp_dir, "concat_list.txt")
        with open(list_txt_path, "w") as f:
            for p in clip_paths:
                f.write(f"file '{os.path.abspath(p)}'\n")

        final_output_path = os.path.join(config.OUTPUT_DIR, output_filename)
        
        # Concat video clips with ultrafast encoding preset
        concat_cmd = (
            f"ffmpeg -y -f concat -safe 0 -i {list_txt_path} "
            f"-c:v libx264 -preset ultrafast -crf 23 -c:a aac -b:a 192k {final_output_path}"
        )
        await asyncio.to_thread(subprocess.run, concat_cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        return final_output_path
