// Call Recorder & Transcriber Front-end Logic

let currentMeetings = [];
let selectedMeeting = null;
let currentTranscript = null;

// DOM Elements
const meetingsListEl = document.getElementById("meetingsList");
const meetingsCountEl = document.getElementById("meetingsCount");
const searchInput = document.getElementById("searchInput");
const btnRefreshList = document.getElementById("btnRefreshList");
const btnOpenFinder = document.getElementById("btnOpenFinder");
const btnConfigModal = document.getElementById("btnConfigModal");
const apiKeyBadge = document.getElementById("apiKeyBadge");

const contentPanel = document.getElementById("contentPanel");
const emptyState = document.getElementById("emptyState");
const meetingDetail = document.getElementById("meetingDetail");
const meetingNameInput = document.getElementById("meetingNameInput");
const btnSaveName = document.getElementById("btnSaveName");
const btnOpenMeetingFolder = document.getElementById("btnOpenMeetingFolder");
const btnDeleteMeeting = document.getElementById("btnDeleteMeeting");

const metaDate = document.getElementById("metaDate");
const metaDuration = document.getElementById("metaDuration");
const metaStatus = document.getElementById("metaStatus");
const metaFolder = document.getElementById("metaFolder");

const audioCard = document.getElementById("audioCard");
const audioCardSentinel = document.getElementById("audioCardSentinel");
const audioFloatingTitle = document.getElementById("audioFloatingTitle");
const audioStatusBadge = document.getElementById("audioStatusBadge");
const btnScrollToTop = document.getElementById("btnScrollToTop");
const audioPlayer = document.getElementById("audioPlayer");
const speedButtons = document.querySelectorAll(".btn-speed");

const btnTranscribe = document.getElementById("btnTranscribe");
const selectModel = document.getElementById("selectModel");
const btnSaveTranscript = document.getElementById("btnSaveTranscript");
const btnExportJson = document.getElementById("btnExportJson");
const btnCopyText = document.getElementById("btnCopyText");
const statusBanner = document.getElementById("statusBanner");

const speakersCard = document.getElementById("speakersCard");
const speakersListEl = document.getElementById("speakersList");
const btnApplySpeakers = document.getElementById("btnApplySpeakers");
const btnAddSpeaker = document.getElementById("btnAddSpeaker");

const segmentsListEl = document.getElementById("segmentsList");
const btnAddSegment = document.getElementById("btnAddSegment");
const tabButtons = document.querySelectorAll(".tab-btn");
const tabSegments = document.getElementById("tabSegments");
const tabRawJson = document.getElementById("tabRawJson");
const rawJsonTextarea = document.getElementById("rawJsonTextarea");
const btnApplyRawJson = document.getElementById("btnApplyRawJson");

const configModal = document.getElementById("configModal");
const btnCloseConfigModal = document.getElementById("btnCloseConfigModal");
const btnCancelConfig = document.getElementById("btnCancelConfig");
const btnSaveConfig = document.getElementById("btnSaveConfig");
const inputApiKey = document.getElementById("inputApiKey");
const btnToggleApiKey = document.getElementById("btnToggleApiKey");
const defaultModelSelect = document.getElementById("defaultModelSelect");
const displayRecordingsPath = document.getElementById("displayRecordingsPath");

const toastEl = document.getElementById("toast");

// --- Initialization ---
document.addEventListener("DOMContentLoaded", () => {
  loadConfig();
  loadMeetings();
  setupEventListeners();
  setupFloatingPlayer();
});

function showToast(message, duration = 3000) {
  toastEl.textContent = message;
  toastEl.classList.add("show");
  setTimeout(() => {
    toastEl.classList.remove("show");
  }, duration);
}

// --- API Calls ---
async function loadConfig() {
  try {
    const res = await fetch("/api/config");
    const data = await res.json();
    if (data.has_api_key) {
      apiKeyBadge.classList.add("active");
      apiKeyBadge.title = "Gemini API configurada";
    } else {
      apiKeyBadge.classList.remove("active");
      apiKeyBadge.title = "Falta configurar API de Gemini";
    }
    if (data.recordings_path) {
      displayRecordingsPath.textContent = data.recordings_path;
    }
    if (data.gemini_model) {
      defaultModelSelect.value = data.gemini_model;
      selectModel.value = data.gemini_model;
    }
  } catch (err) {
    console.error("Error loading config:", err);
  }
}

async function loadMeetings(selectIdAfter = null) {
  try {
    const res = await fetch("/api/meetings");
    const data = await res.json();
    currentMeetings = data.meetings || [];
    renderMeetingsList();

    if (selectIdAfter) {
      selectMeetingById(selectIdAfter);
    } else if (selectedMeeting) {
      const stillExists = currentMeetings.find(m => m.id === selectedMeeting.id);
      if (stillExists) {
        selectMeetingById(selectedMeeting.id);
      } else if (currentMeetings.length > 0) {
        selectMeetingById(currentMeetings[0].id);
      } else {
        selectedMeeting = null;
        renderMeetingDetail();
      }
    } else if (currentMeetings.length > 0) {
      selectMeetingById(currentMeetings[0].id);
    } else {
      renderMeetingDetail();
    }
  } catch (err) {
    console.error("Error loading meetings:", err);
    meetingsListEl.innerHTML = `<div class="empty-list-placeholder">Error al cargar llamadas</div>`;
  }
}

function renderMeetingsList() {
  const query = searchInput.value.toLowerCase().trim();
  const filtered = currentMeetings.filter(m => {
    const nameMatch = (m.name || "").toLowerCase().includes(query);
    const folderMatch = (m.folder_name || "").toLowerCase().includes(query);
    return nameMatch || folderMatch;
  });

  meetingsCountEl.textContent = `${filtered.length} llamada${filtered.length === 1 ? "" : "s"}`;

  if (filtered.length === 0) {
    meetingsListEl.innerHTML = `<div class="empty-list-placeholder">No hay llamadas registradas</div>`;
    return;
  }

  meetingsListEl.innerHTML = "";
  filtered.forEach(m => {
    const item = document.createElement("div");
    item.className = `meeting-item ${selectedMeeting && selectedMeeting.id === m.id ? "active" : ""}`;
    item.onclick = () => selectMeetingById(m.id);

    const dateStr = formatDate(m.created_at);
    const durationStr = formatDuration(m.duration_seconds || 0);

    let statusBadgeClass = "badge-recorded";
    let statusText = "Grabado";
    if (m.status === "transcribed" || m.has_transcript) {
      statusBadgeClass = "badge-transcribed";
      statusText = "Transcrito";
    } else if (m.status === "transcribing") {
      statusBadgeClass = "badge-transcribing";
      statusText = "Transcribiendo...";
    } else if (m.status === "error") {
      statusBadgeClass = "badge-error";
      statusText = "Error";
    }

    item.innerHTML = `
      <div class="meeting-item-title" title="${escapeHtml(m.name || m.folder_name)}">
        ${escapeHtml(m.name || m.folder_name)}
      </div>
      <div class="meeting-item-meta">
        <span>${dateStr}</span>
        <span>⏱️ ${durationStr}</span>
      </div>
      <div class="meeting-item-badges">
        <span class="badge ${statusBadgeClass}">${statusText}</span>
      </div>
    `;
    meetingsListEl.appendChild(item);
  });
}

async function selectMeetingById(meetingId) {
  try {
    const res = await fetch(`/api/meetings/${meetingId}`);
    if (!res.ok) throw new Error("Reunión no encontrada");
    selectedMeeting = await res.json();
    currentTranscript = selectedMeeting.transcript || null;
    if (contentPanel) {
      contentPanel.scrollTo({ top: 0, behavior: "auto" });
    }
    if (audioCard) {
      audioCard.classList.remove("is-floating");
      audioCard.classList.remove("is-playing");
    }
    renderMeetingDetail();
    renderMeetingsList(); // To update active highlight
  } catch (err) {
    showToast(`Error al abrir llamada: ${err.message}`);
  }
}

function renderMeetingDetail() {
  if (!selectedMeeting) {
    emptyState.style.display = "flex";
    meetingDetail.style.display = "none";
    return;
  }

  emptyState.style.display = "none";
  meetingDetail.style.display = "flex";

  // Title & Metadata
  const displayName = selectedMeeting.name || selectedMeeting.folder_name || selectedMeeting.id;
  meetingNameInput.value = selectedMeeting.name || "";
  if (audioFloatingTitle) {
    audioFloatingTitle.textContent = displayName;
    audioFloatingTitle.title = displayName;
  }
  metaDate.textContent = `📅 ${formatDate(selectedMeeting.created_at)}`;
  metaDuration.textContent = `⏱️ ${formatDuration(selectedMeeting.duration_seconds || 0)}`;
  metaFolder.textContent = `📁 ${selectedMeeting.folder_name || selectedMeeting.id}`;

  let statusBadgeClass = "badge-recorded";
  let statusText = "Grabado";
  if (selectedMeeting.status === "transcribed" || selectedMeeting.has_transcript) {
    statusBadgeClass = "badge-transcribed";
    statusText = "Transcrito";
  } else if (selectedMeeting.status === "transcribing") {
    statusBadgeClass = "badge-transcribing";
    statusText = "Transcribiendo...";
  } else if (selectedMeeting.status === "error") {
    statusBadgeClass = "badge-error";
    statusText = "Error";
  }
  metaStatus.className = `meta-tag badge ${statusBadgeClass}`;
  metaStatus.textContent = statusText;

  const metaErrorLog = document.getElementById("metaErrorLog");
  if (metaErrorLog) {
    if (selectedMeeting.has_error_log || selectedMeeting.status === "error" || selectedMeeting.error_message) {
      metaErrorLog.style.display = "inline-flex";
      metaErrorLog.title = selectedMeeting.error_message || "Haz clic para ver el log de error de esta llamada";
      metaErrorLog.onclick = () => openLogsModal(selectedMeeting.id);
    } else {
      metaErrorLog.style.display = "none";
    }
  }

  // Audio setup
  if (selectedMeeting.has_audio) {
    audioPlayer.src = `/api/meetings/${selectedMeeting.id}/audio`;
    if (audioCard) audioCard.style.display = "flex";
    audioPlayer.style.display = "block";
  } else {
    audioPlayer.src = "";
    if (audioCard) audioCard.style.display = "none";
    audioPlayer.style.display = "none";
  }

  if (audioStatusBadge) {
    audioStatusBadge.textContent = "⏸️ PAUSADO";
    audioStatusBadge.className = "audio-floating-indicator paused";
  }
  if (audioCard) {
    audioCard.classList.remove("is-playing");
  }

  hideStatusBanner();

  // Show or hide transcript
  renderTranscriptUI();
}

function renderTranscriptUI() {
  if (!currentTranscript || !currentTranscript.segments || currentTranscript.segments.length === 0) {
    speakersCard.style.display = "none";
    segmentsListEl.innerHTML = `
      <div class="no-transcript-msg">
        Esta llamada aún no ha sido transcrita.<br>
        Haz clic en <strong>✨ Transcribir con Gemini</strong> para generar la transcripción automática con interlocutores y marcas de tiempo.
      </div>
    `;
    rawJsonTextarea.value = "";
    return;
  }

  // Populate Speakers Card
  speakersCard.style.display = "block";
  speakersListEl.innerHTML = "";

  const speakers = currentTranscript.speakers || [];
  const mapping = currentTranscript.speaker_mapping || {};

  speakers.forEach(spk => {
    const row = document.createElement("div");
    row.className = "speaker-row";
    const mappedVal = mapping[spk] || spk;
    row.innerHTML = `
      <span class="speaker-key">${escapeHtml(spk)}</span>
      <input type="text" class="speaker-input" data-speaker="${escapeHtml(spk)}" value="${escapeHtml(mappedVal)}" placeholder="Nombre de ${escapeHtml(spk)}" />
    `;
    speakersListEl.appendChild(row);
  });

  // Populate Segments List
  segmentsListEl.innerHTML = "";
  const segments = currentTranscript.segments || [];

  segments.forEach((seg, index) => {
    const segEl = document.createElement("div");
    segEl.className = "segment-item";
    segEl.dataset.index = index;

    // Available speaker choices
    const currentSpeaker = seg.speaker || (speakers[0] || "Speaker 1");
    let optionsHtml = "";
    const uniqueSpeakers = Array.from(new Set([...speakers, currentSpeaker]));
    uniqueSpeakers.forEach(spk => {
      const isSelected = spk === currentSpeaker ? "selected" : "";
      const displayName = mapping[spk] || spk;
      optionsHtml += `<option value="${escapeHtml(spk)}" ${isSelected}>${escapeHtml(displayName)}</option>`;
    });

    segEl.innerHTML = `
      <div class="segment-header">
        <div class="segment-meta">
          <span class="timestamp-badge" title="Clic para reproducir desde este momento" onclick="seekAudioTo(${seg.start_seconds || 0})">
            ▶ [${seg.start_time || "00:00"} - ${seg.end_time || "00:00"}]
          </span>
          <select class="segment-speaker-select" data-index="${index}">
            ${optionsHtml}
          </select>
        </div>
        <button class="btn-icon" title="Eliminar segmento" onclick="deleteSegment(${index})">🗑️</button>
      </div>
      <textarea class="segment-text" data-index="${index}" rows="2">${escapeHtml(seg.text || "")}</textarea>
    `;
    segmentsListEl.appendChild(segEl);
  });

  // Populate Raw JSON
  rawJsonTextarea.value = JSON.stringify(currentTranscript, null, 2);
}

// Seek audio to given seconds
window.seekAudioTo = function(seconds) {
  if (audioPlayer) {
    audioPlayer.currentTime = seconds;
    audioPlayer.play();
  }
};

window.deleteSegment = function(index) {
  if (!currentTranscript || !currentTranscript.segments) return;
  currentTranscript.segments.splice(index, 1);
  renderTranscriptUI();
};

function collectTranscriptFromUI() {
  if (!currentTranscript) return null;

  // Collect speaker mapping
  const mapping = {};
  const speakerInputs = speakersListEl.querySelectorAll(".speaker-input");
  speakerInputs.forEach(input => {
    const originalSpk = input.dataset.speaker;
    const newName = input.value.trim() || originalSpk;
    mapping[originalSpk] = newName;
  });

  currentTranscript.speaker_mapping = mapping;

  // Collect segments
  const segmentItems = segmentsListEl.querySelectorAll(".segment-item");
  const newSegments = [];
  segmentItems.forEach((item, idx) => {
    const origSeg = currentTranscript.segments[idx] || {};
    const speakerSelect = item.querySelector(".segment-speaker-select");
    const textArea = item.querySelector(".segment-text");

    const selectedSpk = speakerSelect ? speakerSelect.value : (origSeg.speaker || "Speaker 1");
    const textVal = textArea ? textArea.value.trim() : (origSeg.text || "");

    newSegments.push({
      ...origSeg,
      id: idx + 1,
      speaker: mapping[selectedSpk] || selectedSpk,
      speaker_raw: origSeg.speaker_raw || selectedSpk,
      text: textVal
    });
  });

  currentTranscript.segments = newSegments;
  currentTranscript.speakers = Object.values(mapping);

  return currentTranscript;
}

// --- Event Listeners ---
function setupEventListeners() {
  // Search
  searchInput.addEventListener("input", () => renderMeetingsList());

  // Refresh
  btnRefreshList.addEventListener("click", () => loadMeetings());

  // Speed controls
  speedButtons.forEach(btn => {
    btn.addEventListener("click", () => {
      speedButtons.forEach(b => b.classList.remove("active"));
      btn.classList.add("active");
      const speed = parseFloat(btn.dataset.speed);
      if (audioPlayer) audioPlayer.playbackRate = speed;
    });
  });

  // Save Meeting Name
  meetingNameInput.addEventListener("keydown", (e) => {
    if (e.key === "Enter") {
      e.preventDefault();
      btnSaveName.click();
    }
  });

  btnSaveName.addEventListener("click", async () => {
    if (!selectedMeeting) return;
    const newName = meetingNameInput.value.trim();
    if (!newName) {
      showToast("El nombre no puede estar vacío");
      return;
    }
    try {
      const res = await fetch(`/api/meetings/${selectedMeeting.id}/rename`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name: newName })
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || "Error al renombrar");
      selectedMeeting.name = newName;
      if (audioFloatingTitle) {
        audioFloatingTitle.textContent = newName;
        audioFloatingTitle.title = newName;
      }
      showToast("Nombre actualizado");
      loadMeetings(selectedMeeting.id);
    } catch (err) {
      showToast(`Error: ${err.message}`);
    }
  });

  // Delete Meeting
  btnDeleteMeeting.addEventListener("click", async () => {
    if (!selectedMeeting) return;
    if (!confirm(`¿Estás seguro de eliminar "${selectedMeeting.name || selectedMeeting.folder_name}"? Esta acción no se puede deshacer.`)) {
      return;
    }
    try {
      const res = await fetch(`/api/meetings/${selectedMeeting.id}`, { method: "DELETE" });
      if (!res.ok) throw new Error("Error al eliminar la llamada");
      showToast("Llamada eliminada");
      selectedMeeting = null;
      loadMeetings();
    } catch (err) {
      showToast(`Error: ${err.message}`);
    }
  });

  // Open folder in Finder
  btnOpenFinder.addEventListener("click", async () => {
    try {
      await fetch("/api/open-folder", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({})
      });
    } catch (err) {
      showToast("No se pudo abrir la carpeta");
    }
  });

  btnOpenMeetingFolder.addEventListener("click", async () => {
    if (!selectedMeeting) return;
    try {
      await fetch("/api/open-folder", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ meeting_id: selectedMeeting.id })
      });
    } catch (err) {
      showToast("No se pudo abrir la carpeta");
    }
  });

  // Transcribe with Gemini
  btnTranscribe.addEventListener("click", async () => {
    if (!selectedMeeting) return;
    const model = selectModel.value;

    btnTranscribe.disabled = true;
    showStatusBanner("✨ Transcribiendo llamada con Gemini... Esto puede tomar desde unos segundos hasta varios minutos en grabaciones extensas. Por favor espera.", "info");

    try {
      const res = await fetch(`/api/meetings/${selectedMeeting.id}/transcribe`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ gemini_model: model })
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || "Error al transcribir");

      selectedMeeting = data.meeting;
      currentTranscript = selectedMeeting.transcript;
      if (data.warning) {
        showToast(`⚠️ ${data.warning}`, 6000);
      } else {
        showToast("¡Transcripción completada con éxito!");
      }
      hideStatusBanner();
      renderMeetingDetail();
      loadMeetings(selectedMeeting.id);
    } catch (err) {
      showStatusBanner(`⚠️ Error en transcripción: ${err.message}`, "error");
    } finally {
      btnTranscribe.disabled = false;
    }
  });

  // Save Transcript
  btnSaveTranscript.addEventListener("click", async () => {
    if (!selectedMeeting || !currentTranscript) return;
    const updatedData = collectTranscriptFromUI();
    try {
      const res = await fetch(`/api/meetings/${selectedMeeting.id}/transcript`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ transcript: updatedData })
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || "Error al guardar");
      selectedMeeting = data.meeting;
      currentTranscript = selectedMeeting.transcript;
      showToast("Transcripción y speakers guardados");
      renderMeetingDetail();
    } catch (err) {
      showToast(`Error al guardar: ${err.message}`);
    }
  });

  // Apply Speakers to all segments
  btnApplySpeakers.addEventListener("click", () => {
    if (!currentTranscript) return;
    collectTranscriptFromUI();
    renderTranscriptUI();
    showToast("Nombres aplicados a los segmentos");
  });

  // Add Speaker
  btnAddSpeaker.addEventListener("click", () => {
    if (!currentTranscript) return;
    const count = (currentTranscript.speakers || []).length + 1;
    const newSpk = `Speaker ${count}`;
    if (!currentTranscript.speakers) currentTranscript.speakers = [];
    currentTranscript.speakers.push(newSpk);
    if (!currentTranscript.speaker_mapping) currentTranscript.speaker_mapping = {};
    currentTranscript.speaker_mapping[newSpk] = newSpk;
    renderTranscriptUI();
  });

  // Add Segment
  btnAddSegment.addEventListener("click", () => {
    if (!currentTranscript) {
      currentTranscript = {
        speakers: ["Speaker 1"],
        speaker_mapping: { "Speaker 1": "Speaker 1" },
        segments: []
      };
    }
    const currentAudioTime = audioPlayer ? Math.floor(audioPlayer.currentTime) : 0;
    const newSeg = {
      id: (currentTranscript.segments.length || 0) + 1,
      speaker: (currentTranscript.speakers && currentTranscript.speakers[0]) || "Speaker 1",
      start_seconds: currentAudioTime,
      end_seconds: currentAudioTime + 5,
      start_time: formatDuration(currentAudioTime),
      end_time: formatDuration(currentAudioTime + 5),
      text: ""
    };
    currentTranscript.segments.push(newSeg);
    renderTranscriptUI();
  });

  // Export JSON
  btnExportJson.addEventListener("click", () => {
    if (!currentTranscript) {
      showToast("No hay transcripción para exportar");
      return;
    }
    collectTranscriptFromUI();
    const blob = new Blob([JSON.stringify(currentTranscript, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `transcripcion_${selectedMeeting.folder_name || "llamada"}.json`;
    a.click();
    URL.revokeObjectURL(url);
    showToast("Archivo JSON descargado");
  });

  // Copy Formatted Text
  btnCopyText.addEventListener("click", () => {
    if (!currentTranscript || !currentTranscript.segments) {
      showToast("No hay transcripción para copiar");
      return;
    }
    collectTranscriptFromUI();
    const lines = currentTranscript.segments.map(s => {
      return `[${s.start_time} - ${s.end_time}] ${s.speaker}: ${s.text}`;
    });
    const text = lines.join("\n\n");
    navigator.clipboard.writeText(text).then(() => {
      showToast("Transcripción copiada al portapapeles");
    }).catch(() => {
      showToast("No se pudo copiar al portapapeles");
    });
  });

  // Tabs
  tabButtons.forEach(btn => {
    btn.addEventListener("click", () => {
      tabButtons.forEach(b => b.classList.remove("active"));
      btn.classList.add("active");
      const tab = btn.dataset.tab;
      if (tab === "segments") {
        tabSegments.style.display = "block";
        tabRawJson.style.display = "none";
      } else {
        collectTranscriptFromUI();
        rawJsonTextarea.value = JSON.stringify(currentTranscript, null, 2);
        tabSegments.style.display = "none";
        tabRawJson.style.display = "block";
      }
    });
  });

  // Apply Raw JSON
  btnApplyRawJson.addEventListener("click", () => {
    try {
      const parsed = JSON.parse(rawJsonTextarea.value);
      currentTranscript = parsed;
      renderTranscriptUI();
      showToast("JSON aplicado correctamente");
    } catch (e) {
      showToast(`Error de sintaxis en JSON: ${e.message}`);
    }
  });

  // Config Modal
  btnConfigModal.addEventListener("click", () => {
    configModal.style.display = "flex";
  });
  btnCloseConfigModal.addEventListener("click", () => {
    configModal.style.display = "none";
  });
  btnCancelConfig.addEventListener("click", () => {
    configModal.style.display = "none";
  });
  btnToggleApiKey.addEventListener("click", () => {
    inputApiKey.type = inputApiKey.type === "password" ? "text" : "password";
  });
  btnSaveConfig.addEventListener("click", async () => {
    const key = inputApiKey.value.trim();
    const model = defaultModelSelect.value;
    const body = { gemini_model: model };
    if (key) body.gemini_api_key = key;

    try {
      const res = await fetch("/api/config", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body)
      });
      if (!res.ok) throw new Error("Error al guardar ajustes");
      showToast("Ajustes guardados");
      configModal.style.display = "none";
      loadConfig();
    } catch (err) {
      showToast(`Error: ${err.message}`);
    }
  });

  // Logs Modal Event Listeners
  const btnLogsModal = document.getElementById("btnLogsModal");
  const btnCloseLogsModal = document.getElementById("btnCloseLogsModal");
  const btnCloseLogs = document.getElementById("btnCloseLogs");
  const btnRefreshLogs = document.getElementById("btnRefreshLogs");
  const btnCopyLogs = document.getElementById("btnCopyLogs");
  const btnClearLogs = document.getElementById("btnClearLogs");

  if (btnLogsModal) {
    btnLogsModal.addEventListener("click", () => openLogsModal(null));
  }
  if (btnCloseLogsModal) {
    btnCloseLogsModal.addEventListener("click", () => {
      document.getElementById("logsModal").style.display = "none";
    });
  }
  if (btnCloseLogs) {
    btnCloseLogs.addEventListener("click", () => {
      document.getElementById("logsModal").style.display = "none";
    });
  }
  if (btnRefreshLogs) {
    btnRefreshLogs.addEventListener("click", () => loadLogs());
  }
  if (btnCopyLogs) {
    btnCopyLogs.addEventListener("click", () => {
      if (!currentLoadedLogs || currentLoadedLogs.length === 0) {
        showToast("No hay logs para copiar");
        return;
      }
      const text = currentLoadedLogs.map(l => {
        let entry = `[${l.timestamp}] [${l.level}] [${l.category}]${l.meeting ? ' [Meeting: ' + l.meeting + ']' : ''} ${l.message}`;
        if (l.details) entry += `\n${l.details}`;
        return entry;
      }).join("\n\n");
      navigator.clipboard.writeText(text).then(() => {
        showToast("Logs copiados al portapapeles");
      }).catch(() => {
        showToast("No se pudo copiar al portapapeles");
      });
    });
  }
  if (btnClearLogs) {
    btnClearLogs.addEventListener("click", async () => {
      if (!confirm("¿Deseas vaciar este registro de errores?")) return;
      const url = currentLogsMeetingId ? `/api/meetings/${currentLogsMeetingId}/logs/clear` : "/api/logs/clear";
      try {
        const res = await fetch(url, { method: "POST" });
        if (!res.ok) throw new Error("Error al limpiar logs");
        showToast("Registro limpiado correctamente");
        await loadLogs();
      } catch (e) {
        showToast(`Error: ${e.message}`);
      }
    });
  }

  // Filter buttons in Logs Modal
  document.querySelectorAll(".btn-filter").forEach(btn => {
    btn.addEventListener("click", () => {
      document.querySelectorAll(".btn-filter").forEach(b => b.classList.remove("active"));
      btn.classList.add("active");
      activeLogFilter = btn.dataset.filter || "all";
      renderLogsList();
    });
  });
}

// Logs State and Logic
let currentLogsMeetingId = null;
let currentLoadedLogs = [];
let activeLogFilter = "all";

async function openLogsModal(meetingId = null) {
  currentLogsMeetingId = meetingId;
  const modal = document.getElementById("logsModal");
  const title = document.getElementById("logsModalTitle");
  if (modal) modal.style.display = "flex";
  if (title) {
    if (meetingId) {
      title.textContent = `📜 Registro de Errores: ${selectedMeeting?.name || meetingId}`;
    } else {
      title.textContent = "📜 Registro de Errores de la Aplicación";
    }
  }
  await loadLogs();
}

async function loadLogs() {
  const container = document.getElementById("logsContainer");
  const pathText = document.getElementById("logsPathText");
  if (container) container.innerHTML = '<div class="logs-empty">Cargando registros...</div>';
  
  const url = currentLogsMeetingId ? `/api/meetings/${currentLogsMeetingId}/logs` : "/api/logs";
  try {
    const res = await fetch(url);
    if (!res.ok) throw new Error("No se pudieron cargar los logs");
    const data = await res.json();
    currentLoadedLogs = data.logs || [];
    if (data.log_path && pathText) {
      pathText.textContent = data.log_path;
    } else if (pathText) {
      pathText.textContent = currentLogsMeetingId ? "error.log (en carpeta de reunión)" : "app_errors.log";
    }
    renderLogsList();
  } catch (err) {
    if (container) {
      container.innerHTML = `<div class="logs-empty" style="color: #ef4444;">Error al cargar logs: ${escapeHtml(err.message)}</div>`;
    }
  }
}

function renderLogsList() {
  const container = document.getElementById("logsContainer");
  if (!container) return;

  let filtered = currentLoadedLogs;
  if (activeLogFilter !== "all") {
    filtered = currentLoadedLogs.filter(l => l.category === activeLogFilter);
  }
  if (filtered.length === 0) {
    container.innerHTML = '<div class="logs-empty">No hay errores ni advertencias registradas en esta categoría.</div>';
    return;
  }

  container.innerHTML = filtered.map(log => {
    const levelClass = (log.level || "info").toLowerCase();
    const meetingBadge = log.meeting ? `<span class="log-meeting-tag">📁 ${escapeHtml(log.meeting)}</span>` : "";
    const detailsHtml = log.details ? `<div class="log-details">${escapeHtml(log.details)}</div>` : "";
    return `
      <div class="log-entry level-${levelClass}">
        <div class="log-header">
          <div class="log-badges">
            <span class="badge-log badge-level-${levelClass}">${escapeHtml(log.level || "INFO")}</span>
            <span class="badge-log badge-category">${escapeHtml(log.category || "GENERAL")}</span>
            ${meetingBadge}
          </div>
          <span class="log-timestamp">${escapeHtml(log.timestamp || "")}</span>
        </div>
        <div class="log-message">${escapeHtml(log.message || "")}</div>
        ${detailsHtml}
      </div>
    `;
  }).join("");
}

function showStatusBanner(msg, type = "info") {
  statusBanner.textContent = msg;
  statusBanner.className = `status-banner ${type}`;
  statusBanner.style.display = "flex";
}

function hideStatusBanner() {
  statusBanner.style.display = "none";
}

// Format helpers
function formatDate(isoStr) {
  if (!isoStr) return "-";
  try {
    const d = new Date(isoStr);
    return d.toLocaleDateString("es-ES", {
      day: "2-digit",
      month: "short",
      year: "numeric",
      hour: "2-digit",
      minute: "2-digit"
    });
  } catch (e) {
    return isoStr;
  }
}

function formatDuration(seconds) {
  const secs = Math.floor(seconds);
  const mins = Math.floor(secs / 60);
  const hrs = Math.floor(mins / 60);
  const remSecs = secs % 60;
  const remMins = mins % 60;
  if (hrs > 0) {
    return `${pad(hrs)}:${pad(remMins)}:${pad(remSecs)}`;
  }
  return `${pad(remMins)}:${pad(remSecs)}`;
}

function pad(num) {
  return num < 10 ? "0" + num : "" + num;
}

function escapeHtml(text) {
  if (!text) return "";
  const div = document.createElement("div");
  div.textContent = text;
  return div.innerHTML;
}

// --- Floating Audio Player & Playback Shortcuts ---
function setupFloatingPlayer() {
  if (!audioCard || !contentPanel) return;

  function updateFloatingState() {
    if (!audioCardSentinel) return;
    const sentinelRect = audioCardSentinel.getBoundingClientRect();
    const panelRect = contentPanel.getBoundingClientRect();
    // When sentinel scrolls out above the visible top edge of contentPanel
    const isFloating = sentinelRect.bottom <= panelRect.top + 2;
    if (isFloating) {
      audioCard.classList.add("is-floating");
    } else {
      audioCard.classList.remove("is-floating");
    }
  }

  // Scroll listener on content panel
  contentPanel.addEventListener("scroll", updateFloatingState, { passive: true });

  // IntersectionObserver for efficient and instant viewport detection
  if ("IntersectionObserver" in window && audioCardSentinel) {
    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (!entry.isIntersecting && entry.boundingClientRect.top < entry.rootBounds.top) {
          audioCard.classList.add("is-floating");
        } else if (entry.isIntersecting) {
          audioCard.classList.remove("is-floating");
        }
      });
    }, {
      root: contentPanel,
      threshold: [0, 1]
    });
    observer.observe(audioCardSentinel);
  }

  // Scroll to top button
  if (btnScrollToTop) {
    btnScrollToTop.addEventListener("click", () => {
      contentPanel.scrollTo({ top: 0, behavior: "smooth" });
    });
  }

  // Audio status and playback events
  if (audioPlayer) {
    audioPlayer.addEventListener("play", () => {
      audioCard.classList.add("is-playing");
      if (audioStatusBadge) {
        audioStatusBadge.textContent = "● REPRODUCIENDO";
        audioStatusBadge.className = "audio-floating-indicator playing";
      }
    });

    audioPlayer.addEventListener("pause", () => {
      audioCard.classList.remove("is-playing");
      if (audioStatusBadge) {
        audioStatusBadge.textContent = "⏸️ PAUSADO";
        audioStatusBadge.className = "audio-floating-indicator paused";
      }
    });

    audioPlayer.addEventListener("ended", () => {
      audioCard.classList.remove("is-playing");
      if (audioStatusBadge) {
        audioStatusBadge.textContent = "⏹️ FINALIZADO";
        audioStatusBadge.className = "audio-floating-indicator ended";
      }
      clearActiveSegmentHighlights();
    });

    // Synchronize active transcript segment highlight while audio plays
    audioPlayer.addEventListener("timeupdate", () => {
      highlightActiveSegment(audioPlayer.currentTime);
    });
  }

  // Global keyboard shortcuts to pause/resume playback
  document.addEventListener("keydown", (e) => {
    if (!audioPlayer || !audioPlayer.src || audioPlayer.style.display === "none") return;

    // Alt+Space or Ctrl+Space: Works anywhere, even while editing text in inputs/textareas
    if ((e.altKey || e.ctrlKey) && (e.code === "Space" || e.key === " " || e.keyCode === 32)) {
      e.preventDefault();
      if (audioPlayer.paused) {
        audioPlayer.play();
      } else {
        audioPlayer.pause();
      }
      return;
    }

    // Space key: Only triggers when NOT actively editing text
    if (e.code === "Space" || e.key === " " || e.keyCode === 32) {
      const active = document.activeElement;
      const tag = active ? active.tagName : "";
      const isEditable = active && (tag === "INPUT" || tag === "TEXTAREA" || tag === "SELECT" || active.isContentEditable);
      if (!isEditable) {
        e.preventDefault();
        if (audioPlayer.paused) {
          audioPlayer.play();
        } else {
          audioPlayer.pause();
        }
      }
    }
  });
}

function clearActiveSegmentHighlights() {
  const activeItems = segmentsListEl.querySelectorAll(".segment-item.active-playing");
  activeItems.forEach(el => el.classList.remove("active-playing"));
}

function highlightActiveSegment(currentTime) {
  if (!currentTranscript || !currentTranscript.segments) return;
  const segments = currentTranscript.segments;
  const segmentItems = segmentsListEl.querySelectorAll(".segment-item");
  if (segmentItems.length === 0) return;

  segmentItems.forEach((item, idx) => {
    const seg = segments[idx];
    if (seg && seg.start_seconds !== undefined && seg.end_seconds !== undefined) {
      if (currentTime >= seg.start_seconds && currentTime <= seg.end_seconds) {
        item.classList.add("active-playing");
      } else {
        item.classList.remove("active-playing");
      }
    }
  });
}
