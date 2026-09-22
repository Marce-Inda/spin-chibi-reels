---
title: SpinChibi Reels AI
emoji: 🎰
colorFrom: purple
colorTo: yellow
sdk: gradio
sdk_version: 5.0.0
app_file: app.py
pinned: false
---

# SpinChibi-Reels 🎰✨

> **Sistema Autónomo Multi-Agente para la Generación de Reels e Instagram/TikTok Shorts (9:16) de Casino**
> Personajes estilo **3D Chibi con vestimenta moderna y ojos expresivos**, historias cómicas con equivocaciones/tropezones y finales felices llenos de victoria y Jackpots.

![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green?logo=fastapi)
![Docker](https://img.shields.io/badge/Docker-HuggingFace_Spaces-orange?logo=docker)
![FFmpeg](https://img.shields.io/badge/FFmpeg-6.1-red?logo=ffmpeg)

---

## 🌟 Características Principales

- 🤖 **Arquitectura Multi-Agente**:
  - **`StoryAgent`**: Genera historias cómicas virales de casino con equivocaciones inesperadas (ej: tropezarse, estornudar, presionar la apuesta máxima por error con una bebida) que activan de forma sorpresiva el **Jackpot de $100,000**.
  - **`ScriptAgent`**: Desglosa la historia en escenas cronometradas (9:16), genera la locución en voz en off (español), subtítulos animados y marcas de sonido (`[slot_spin]`, `[oops_buzzer]`, `[jackpot_coins]`).
  - **`VisualDesignAgent`**: Construye los prompts visuales manteniendo la consistencia estética **3D Chibi con ojos estelares brillantes** y atuendos modernos de gala.
- 🗣️ **Voz en Off Neural (Edge-TTS)**: Voces expresivas en español integradas sin costo.
- 🎬 **Motor de Renderizado 9:16 (FFmpeg)**: Animación de cámara Ken Burns, sincronización de audio + música + efectos de sonido (SFX) de monedas y tragamonedas.
- 🔑 **Soporte Abierto para Créditos Cloud**: Integra credenciales de **OpenRouter, OpenAI, Replicate o Fal.ai** directamente desde el panel web.

---

## 📱 Vista Previa del Panel de Control

La interfaz web incluye una maqueta interactiva en tiempo real con reproductor de video en formato de pantalla móvil vertical (9:16), editor de escenas y visualizador de prompts.

---

## 🛠️ Instalación y Uso Local

### Prerrequisitos
- Python 3.10+
- FFmpeg instalado en el sistema (`sudo apt install ffmpeg`)

### Pasos
```bash
# 1. Clonar el repositorio
git clone https://github.com/Marce-Inda/spin-chibi-reels.git
cd spin-chibi-reels

# 2. Crear entorno virtual e instalar dependencias
python3 -m venv venv
source venv/bin/activate
pip install -r backend/requirements.txt

# 3. Iniciar el servidor FastAPI
uvicorn backend.app:app --reload --port 8000
```
Abre tu navegador en `http://localhost:8000`.

---

## ☁️ Despliegue Gratuito en Hugging Face Spaces (Docker)

Este proyecto está 100% optimizado para ejecutarse de forma gratuita en **Hugging Face Spaces** utilizando Docker (16 GB RAM gratis sin sobrecargar tu PC):

1. Crea un nuevo **Space** en Hugging Face.
2. Selecciona **Docker** como SDK.
3. Conecta o sube este repositorio a Hugging Face.
4. ¡Listo! La app se iniciará automáticamente en la nube.

---

## 📄 Licencia

MIT License — Creado para generación de contenido de casino en redes sociales.
