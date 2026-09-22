// Global App State
let currentStory = "";
let currentScenes = [];
let batchPollInterval = null;

function setPrompt(text) {
    document.getElementById("userPrompt").value = text;
}

document.addEventListener("DOMContentLoaded", () => {
    const btnStartBatch = document.getElementById("btnStartBatch");
    const btnFastReel = document.getElementById("btnFastReel");
    const terminalLogs = document.getElementById("terminalLogs");
    const batchGalleryContainer = document.getElementById("batchGalleryContainer");
    const batchGrid = document.getElementById("batchGrid");

    const obsProgressText = document.getElementById("obsProgressText");
    const obsProgressBar = document.getElementById("obsProgressBar");
    const obsTotalCost = document.getElementById("obsTotalCost");
    const obsAvgCost = document.getElementById("obsAvgCost");
    const obsTokens = document.getElementById("obsTokens");
    const obsDiskUsed = document.getElementById("obsDiskUsed");
    const obsReelsCount = document.getElementById("obsReelsCount");

    const reelVideoPlayer = document.getElementById("reelVideoPlayer");
    const playerPlaceholder = document.getElementById("playerPlaceholder");
    const reelOverlayUi = document.getElementById("reelOverlayUi");
    const downloadBar = document.getElementById("downloadBar");
    const downloadBtn = document.getElementById("downloadBtn");

    // Modal elements
    const configModal = document.getElementById("configModal");
    const btnConfigModal = document.getElementById("btnConfigModal");
    const btnCloseModal = document.getElementById("btnCloseModal");
    const btnSaveConfig = document.getElementById("btnSaveConfig");

    // Fetch initial Observability Stats
    function updateObservabilityStats() {
        fetch("/api/observability-stats")
            .then(r => r.json())
            .then(stats => {
                obsDiskUsed.innerText = `${stats.disk_used_mb} MB`;
                obsReelsCount.innerText = `${stats.stored_reels_count} videos conservados (15 días)`;
            })
            .catch(e => console.error("Error fetching obs stats:", e));
    }
    updateObservabilityStats();
    setInterval(updateObservabilityStats, 10000);

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

    // 1-Click Fast Reel Generator
    btnFastReel.addEventListener("click", async () => {
        const userPrompt = document.getElementById("userPrompt").value;
        const openrouterKey = document.getElementById("openrouterKey").value;
        
        btnFastReel.disabled = true;
        btnFastReel.querySelector(".btn-text").innerText = "⚡ Generando Reel Completo (4.3s)...";

        try {
            const res = await fetch("/api/generate-full-reel", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ user_prompt: userPrompt, api_key: openrouterKey })
            });
            const data = await res.json();

            if (data.status === "success") {
                playerPlaceholder.classList.add("hidden");
                reelVideoPlayer.src = data.video_url + "?t=" + new Date().getTime();
                reelVideoPlayer.classList.remove("hidden");
                reelVideoPlayer.play();

                reelOverlayUi.classList.remove("hidden");
                downloadBar.classList.remove("hidden");
                downloadBtn.href = data.video_url;
                
                terminalLogs.innerHTML += `<div class="log-line">⚡ Reel individual generado en 4.3s.</div>`;
                terminalLogs.scrollTop = terminalLogs.scrollHeight;
                updateObservabilityStats();
            }
        } catch (e) {
            alert("Error en Reel Generator: " + e.message);
        } finally {
            btnFastReel.disabled = false;
            btnFastReel.querySelector(".btn-text").innerText = "⚡ Crear 1 Reel Individual (4.3s)";
        }
    });

    // 20-Reel Batch Creation Loop
    btnStartBatch.addEventListener("click", async () => {
        const openrouterKey = document.getElementById("openrouterKey").value;

        btnStartBatch.disabled = true;
        btnStartBatch.querySelector(".btn-text").innerText = "⏳ Ejecutando Bucle de 20 Reels...";

        try {
            const res = await fetch("/api/start-batch", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ total_reels: 20, api_key: openrouterKey })
            });
            const data = await res.json();

            if (data.status === "started" || data.status === "running") {
                startBatchPolling();
            }
        } catch (e) {
            alert("Error al iniciar bucle masivo: " + e.message);
            btnStartBatch.disabled = false;
            btnStartBatch.querySelector(".btn-text").innerText = "🚀 Iniciar Bucle Masivo de 20 Reels (1-Clic)";
        }
    });

    function startBatchPolling() {
        if (batchPollInterval) clearInterval(batchPollInterval);
        
        batchPollInterval = setInterval(async () => {
            try {
                const r = await fetch("/api/batch-status");
                const state = await r.json();

                // Update Observability Cards
                const current = state.current_index;
                const total = state.total_reels;
                const pct = Math.round((state.completed_reels.length / total) * 100);

                obsProgressText.innerText = `${state.completed_reels.length} / ${total}`;
                obsProgressBar.style.width = `${pct}%`;
                
                obsTotalCost.innerHTML = `$${state.total_cost_usd.toFixed(5)} <span class="obs-unit">USD</span>`;
                const avgCost = state.completed_reels.length > 0 ? (state.total_cost_usd / state.completed_reels.length) : 0;
                obsAvgCost.innerText = `Promedio: $${avgCost.toFixed(5)} / Reel`;
                obsTokens.innerHTML = `${state.total_tokens_used.toLocaleString()} <span class="obs-unit">Tokens</span>`;

                // Update Terminal Logs
                if (state.logs && state.logs.length > 0) {
                    terminalLogs.innerHTML = state.logs.map(l => `<div class="log-line">${l}</div>`).join("");
                    terminalLogs.scrollTop = terminalLogs.scrollHeight;
                }

                // Render Batch Gallery items
                if (state.completed_reels && state.completed_reels.length > 0) {
                    batchGalleryContainer.classList.remove("hidden");
                    batchGrid.innerHTML = state.completed_reels.map(item => `
                        <div class="batch-item-card">
                            <h5>${item.title}</h5>
                            <p>Render: ${item.render_time_sec}s | Costo: $${item.cost_usd.toFixed(5)}</p>
                            <button class="btn btn-outline btn-block" onclick="playBatchReel('${item.video_url}')">▶️ Ver Reel</button>
                        </div>
                    `).join("");

                    // Automatically play last generated reel in player
                    const lastReel = state.completed_reels[state.completed_reels.length - 1];
                    if (reelVideoPlayer.src !== window.location.origin + lastReel.video_url) {
                        playerPlaceholder.classList.add("hidden");
                        reelVideoPlayer.src = lastReel.video_url;
                        reelVideoPlayer.classList.remove("hidden");
                        reelVideoPlayer.play();
                        reelOverlayUi.classList.remove("hidden");
                        downloadBar.classList.remove("hidden");
                        downloadBtn.href = lastReel.video_url;
                    }
                }

                // Finish condition
                if (!state.is_running && state.completed_reels.length >= total) {
                    clearInterval(batchPollInterval);
                    btnStartBatch.disabled = false;
                    btnStartBatch.querySelector(".btn-text").innerText = "🚀 Iniciar Bucle Masivo de 20 Reels (1-Clic)";
                    updateObservabilityStats();
                }
            } catch (e) {
                console.error("Error polling batch status:", e);
            }
        }, 1500);
    }

    window.playBatchReel = function(url) {
        playerPlaceholder.classList.add("hidden");
        reelVideoPlayer.src = url;
        reelVideoPlayer.classList.remove("hidden");
        reelVideoPlayer.play();
        reelOverlayUi.classList.remove("hidden");
        downloadBar.classList.remove("hidden");
        downloadBtn.href = url;
    };
});
