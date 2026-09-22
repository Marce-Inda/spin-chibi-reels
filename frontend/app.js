// Global App State
let currentStory = "";
let currentScenes = [];

function setPrompt(text) {
    document.getElementById("userPrompt").value = text;
}

document.addEventListener("DOMContentLoaded", () => {
    const btnGenerateStory = document.getElementById("btnGenerateStory");
    const btnCreateScript = document.getElementById("btnCreateScript");
    const btnRenderReel = document.getElementById("btnRenderReel");
    const storyBox = document.getElementById("storyBox");
    const storyContent = document.getElementById("storyContent");
    const scenesContainer = document.getElementById("scenesContainer");
    const scenesList = document.getElementById("scenesList");
    
    const reelVideoPlayer = document.getElementById("reelVideoPlayer");
    const playerPlaceholder = document.getElementById("playerPlaceholder");
    const reelOverlayUi = document.getElementById("reelOverlayUi");
    const downloadBar = document.getElementById("downloadBar");
    
    // Modal elements
    const configModal = document.getElementById("configModal");
    const btnConfigModal = document.getElementById("btnConfigModal");
    const btnCloseModal = document.getElementById("btnCloseModal");
    const btnSaveConfig = document.getElementById("btnSaveConfig");

    // 1-Click Fast Reel Generator
    const btnFastReel = document.getElementById("btnFastReel");
    btnFastReel.addEventListener("click", async () => {
        const userPrompt = document.getElementById("userPrompt").value;
        const openrouterKey = document.getElementById("openrouterKey").value;
        
        btnFastReel.disabled = true;
        btnFastReel.querySelector(".btn-text").innerText = "⚡ Generando Reel Completo (4.3s)...";
        btnFastReel.querySelector(".spinner").classList.remove("hidden");

        try {
            const res = await fetch("/api/generate-full-reel", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ user_prompt: userPrompt, api_key: openrouterKey })
            });
            const data = await res.json();

            if (data.status === "success") {
                currentStory = data.story_text;
                currentScenes = data.scenes;
                
                storyContent.innerText = currentStory;
                storyBox.classList.remove("hidden");
                renderScenes(currentScenes);
                scenesContainer.classList.remove("hidden");

                // Play in phone video player
                playerPlaceholder.classList.add("hidden");
                reelVideoPlayer.src = data.video_url + "?t=" + new Date().getTime();
                reelVideoPlayer.classList.remove("hidden");
                reelVideoPlayer.play();

                reelOverlayUi.classList.remove("hidden");
                downloadBar.classList.remove("hidden");
            }
        } catch (e) {
            alert("Error en 1-Click Reel Generator: " + e.message);
        } finally {
            btnFastReel.disabled = false;
            btnFastReel.querySelector(".btn-text").innerText = "⚡ Crear Reel Completo en 1 Clic (Historia + Audio + Video 9:16)";
            btnFastReel.querySelector(".spinner").classList.add("hidden");
        }
    });

    // Modal Events
    btnConfigModal.addEventListener("click", () => configModal.classList.remove("hidden"));
    btnCloseModal.addEventListener("click", () => configModal.classList.add("hidden"));
    
    btnSaveConfig.addEventListener("click", () => {
        const openrouterKey = document.getElementById("openrouterKey").value;
        const replicateKey = document.getElementById("replicateKey").value;
        const llmModel = document.getElementById("llmSelect").value;
        const videoModel = document.getElementById("videoModelSelect").value;
        
        fetch("/api/update-config", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ 
                openrouter_key: openrouterKey, 
                replicate_key: replicateKey,
                llm_model: llmModel,
                video_model: videoModel
            })
        })
        .then(r => r.json())
        .then(res => {
            alert("Credenciales y modelos guardados correctamente.");
            configModal.classList.add("hidden");
        });
    });

    // 1. Generate Story
    btnGenerateStory.addEventListener("click", async () => {
        const userPrompt = document.getElementById("userPrompt").value;
        const openrouterKey = document.getElementById("openrouterKey").value;
        
        btnGenerateStory.disabled = true;
        btnGenerateStory.querySelector(".btn-text").innerText = "Generando Historia Cómica...";
        btnGenerateStory.querySelector(".spinner").classList.remove("hidden");

        try {
            const res = await fetch("/api/generate-story", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ user_prompt: userPrompt, api_key: openrouterKey })
            });
            const data = await res.json();
            currentStory = data.story_text;

            storyContent.innerText = currentStory;
            storyBox.classList.remove("hidden");
        } catch (e) {
            alert("Error al generar la historia: " + e.message);
        } finally {
            btnGenerateStory.disabled = false;
            btnGenerateStory.querySelector(".btn-text").innerText = "🚀 Generar Historia Cósmica con Agente AI";
            btnGenerateStory.querySelector(".spinner").classList.add("hidden");
        }
    });

    // 2. Create Script Scenes & 3D Chibi Prompts
    btnCreateScript.addEventListener("click", async () => {
        if (!currentStory) return;
        const openrouterKey = document.getElementById("openrouterKey").value;

        btnCreateScript.disabled = true;
        btnCreateScript.innerText = "Creando Guion y Prompts...";

        try {
            const res = await fetch("/api/create-script", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ story_text: currentStory, api_key: openrouterKey })
            });
            const data = await res.json();
            currentScenes = data.scenes;

            renderScenes(currentScenes);
            scenesContainer.classList.remove("hidden");
        } catch (e) {
            alert("Error al desglosar guion: " + e.message);
        } finally {
            btnCreateScript.disabled = false;
            btnCreateScript.innerText = "🎬 Crear Guion y Prompts 3D Chibi (Paso 2)";
        }
    });

    // Render Scene List UI
    function renderScenes(scenes) {
        scenesList.innerHTML = "";
        scenes.forEach((s) => {
            const card = document.createElement("div");
            card.className = "scene-card";
            card.innerHTML = `
                <div class="scene-num">${s.id}</div>
                <div class="scene-info">
                    <h4>Escena ${s.id} (${s.duration}s) — SFX: ${s.sound_effect}</h4>
                    <p><b>Voz en Off:</b> "${s.narration}"</p>
                    <p><b>Subtítulo:</b> ${s.text_overlay}</p>
                    <span class="scene-tag">✨ Prompt 3D Chibi: ${s.visual_description.substring(0, 60)}...</span>
                </div>
            `;
            scenesList.appendChild(card);
        });
    }

    // 3. Render Reel Video
    btnRenderReel.addEventListener("click", async () => {
        if (currentScenes.length === 0) return;

        btnRenderReel.disabled = true;
        btnRenderReel.innerText = "⏳ Renderizando Reel (Sintetizando Voz, SFX y Video 9:16)...";

        try {
            const res = await fetch("/api/render-reel", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ scenes: currentScenes })
            });
            const data = await res.json();

            if (data.status === "success") {
                // Play video in phone player
                playerPlaceholder.classList.add("hidden");
                reelVideoPlayer.src = data.video_url + "?t=" + new Date().getTime();
                reelVideoPlayer.classList.remove("hidden");
                reelVideoPlayer.play();

                reelOverlayUi.classList.remove("hidden");
                downloadBar.classList.remove("hidden");
            } else {
                alert("Ocurrió un error en el renderizado.");
            }
        } catch (e) {
            alert("Error durante el renderizado: " + e.message);
        } finally {
            btnRenderReel.disabled = false;
            btnRenderReel.innerText = "✨ Renderizar Reel Completo (Audio + SFX + Video 9:16)";
        }
    });
});
