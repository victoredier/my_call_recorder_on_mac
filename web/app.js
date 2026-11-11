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
const btnOpenSegmentModal = document.getElementById("btnOpenSegmentModal");
const btnAudioCardSegment = document.getElementById("btnAudioCardSegment");
const btnTranscriptHeaderSegment = document.getElementById("btnTranscriptHeaderSegment");
const selectModel = document.getElementById("selectModel");
const btnRefreshModels = document.getElementById("btnRefreshModels");
const inputParticipantsContext = document.getElementById("inputParticipantsContext");
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

// Segment Modal Elements
const segmentModal = document.getElementById("segmentModal");
const btnCloseSegmentModal = document.getElementById("btnCloseSegmentModal");
const btnCancelSegmentModal = document.getElementById("btnCancelSegmentModal");
const btnExecuteSegmentTranscribe = document.getElementById("btnExecuteSegmentTranscribe");
const segmentCallName = document.getElementById("segmentCallName");
const segmentCallTotalDuration = document.getElementById("segmentCallTotalDuration");
const inputSegmentStart = document.getElementById("inputSegmentStart");
const inputSegmentEnd = document.getElementById("inputSegmentEnd");
const btnSetStartToCurrent = document.getElementById("btnSetStartToCurrent");
const startCurrentPosBadge = document.getElementById("startCurrentPosBadge");
const btnSetEndToCurrent = document.getElementById("btnSetEndToCurrent");
const endCurrentPosBadge = document.getElementById("endCurrentPosBadge");
const btnSetEndToTotal = document.getElementById("btnSetEndToTotal");
const segmentCalculatedDuration = document.getElementById("segmentCalculatedDuration");
const segmentRangeSummary = document.getElementById("segmentRangeSummary");
const btnPreviewSegmentAudio = document.getElementById("btnPreviewSegmentAudio");
const btnStopPreviewSegmentAudio = document.getElementById("btnStopPreviewSegmentAudio");
const segmentModelSelect = document.getElementById("segmentModelSelect");
const segmentParticipantsContext = document.getElementById("segmentParticipantsContext");
const mergeOptionGroup = document.getElementById("mergeOptionGroup");

let isSegmentPreviewActive = false;
let segmentPreviewEndSec = null;

const configModal = document.getElementById("configModal");
const btnCloseConfigModal = document.getElementById("btnCloseConfigModal");
const btnCancelConfig = document.getElementById("btnCancelConfig");
const btnSaveConfig = document.getElementById("btnSaveConfig");
const inputApiKey = document.getElementById("inputApiKey");
const btnToggleApiKey = document.getElementById("btnToggleApiKey");
const defaultModelSelect = document.getElementById("defaultModelSelect");
const btnConfigRefreshModels = document.getElementById("btnConfigRefreshModels");
const modelsDetectStatus = document.getElementById("modelsDetectStatus");
const displayRecordingsPath = document.getElementById("displayRecordingsPath");

// Search & Replace DOM Elements
const btnToggleSearchReplace = document.getElementById("btnToggleSearchReplace");
const searchReplaceBar = document.getElementById("searchReplaceBar");
const btnSrClose = document.getElementById("btnSrClose");
const srSearchInput = document.getElementById("srSearchInput");
const srReplaceInput = document.getElementById("srReplaceInput");
const srMatchCounter = document.getElementById("srMatchCounter");
const btnSrPrev = document.getElementById("btnSrPrev");
const btnSrNext = document.getElementById("btnSrNext");
const srCaseSensitive = document.getElementById("srCaseSensitive");
const srWholeWord = document.getElementById("srWholeWord");
const btnSrReplaceOne = document.getElementById("btnSrReplaceOne");
const btnSrReplaceAll = document.getElementById("btnSrReplaceAll");
const btnSrSaveToCentral = document.getElementById("btnSrSaveToCentral");
const srStatusText = document.getElementById("srStatusText");

// Replacements Alert Banner Elements
const replacementsAlertBanner = document.getElementById("replacementsAlertBanner");
const repAlertSubtitle = document.getElementById("repAlertSubtitle");
const repAlertTotalCount = document.getElementById("repAlertTotalCount");
const btnApplyAllDetectedRep = document.getElementById("btnApplyAllDetectedRep");
const btnOpenRepFromBanner = document.getElementById("btnOpenRepFromBanner");
const btnDismissRepAlert = document.getElementById("btnDismissRepAlert");
const repAlertChips = document.getElementById("repAlertChips");

// Centralized Replacements Modal Elements
const btnReplacementsModal = document.getElementById("btnReplacementsModal");
const replacementsModal = document.getElementById("replacementsModal");
const btnCloseReplacementsModal = document.getElementById("btnCloseReplacementsModal");
const btnExitReplacementsModal = document.getElementById("btnExitReplacementsModal");
const repFormTitle = document.getElementById("repFormTitle");
const inputEditRepId = document.getElementById("inputEditRepId");
const inputNewRepFind = document.getElementById("inputNewRepFind");
const inputNewRepReplace = document.getElementById("inputNewRepReplace");
const checkNewRepWholeWord = document.getElementById("checkNewRepWholeWord");
const checkNewRepCase = document.getElementById("checkNewRepCase");
const btnAddNewReplacement = document.getElementById("btnAddNewReplacement");
const btnCancelEditRep = document.getElementById("btnCancelEditRep");
const repFilterInput = document.getElementById("repFilterInput");
const repTotalRulesBadge = document.getElementById("repTotalRulesBadge");
const repItemsList = document.getElementById("repItemsList");
const btnModalApplyAllToMeeting = document.getElementById("btnModalApplyAllToMeeting");
const modalMatchesCount = document.getElementById("modalMatchesCount");

// Search and Replacements State
let centralizedReplacements = [];
let activeDetectedMatches = [];
let searchMatches = [];
let currentMatchIndex = -1;
let isSearchReplaceOpen = false;
let dismissedMeetingAlerts = new Set();

const toastEl = document.getElementById("toast");

// --- Initialization ---
document.addEventListener("DOMContentLoaded", () => {
  loadConfig();
  loadMeetings();
  loadCentralizedReplacements();
  setupEventListeners();
  setupFloatingPlayer();
  setupSearchReplaceAndReplacements();
});

function showToast(message, duration = 3000) {
  toastEl.textContent = message;
  toastEl.classList.add("show");
  setTimeout(() => {
    toastEl.classList.remove("show");
  }, duration);
}

// --- API Calls ---
async function fetchAvailableModels(apiKey = null) {
  try {
    const url = apiKey ? `/api/gemini/models?key=${encodeURIComponent(apiKey)}` : `/api/gemini/models`;
    const res = await fetch(url);
    const data = await res.json();
    if (data.success && Array.isArray(data.models) && data.models.length > 0) {
      updateModelSelectOptions(data.models);
      return data.models;
    }
  } catch (err) {
    console.warn("No se pudieron cargar modelos dinámicos de Gemini:", err);
  }
  return null;
}

function updateModelSelectOptions(models) {
  const selects = [selectModel, segmentModelSelect, defaultModelSelect];
  selects.forEach(sel => {
    if (!sel) return;
    const currentVal = sel.value;
    sel.innerHTML = "";
    models.forEach(m => {
      const opt = document.createElement("option");
      opt.value = m.id;
      opt.textContent = m.name || m.display_name || m.id;
      sel.appendChild(opt);
    });
    // Restore previous selection if still available
    const exists = models.some(m => m.id === currentVal);
    if (exists) {
      sel.value = currentVal;
    } else {
      const defaultMod = models.find(m => m.is_default) || models[0];
      if (defaultMod) sel.value = defaultMod.id;
    }
  });
}

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

    // Attempt to load dynamic models
    await fetchAvailableModels();

    if (data.gemini_model) {
      if (defaultModelSelect) defaultModelSelect.value = data.gemini_model;
      if (selectModel) selectModel.value = data.gemini_model;
      if (segmentModelSelect) segmentModelSelect.value = data.gemini_model;
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

  // Populate participants context if transcript exists
  if (inputParticipantsContext) {
    if (selectedMeeting.transcript && Array.isArray(selectedMeeting.transcript.speakers)) {
      const mapping = selectedMeeting.transcript.speaker_mapping || {};
      const names = selectedMeeting.transcript.speakers.map(s => mapping[s] || s).filter(n => !/^Speaker\s*\d+$/i.test(n));
      inputParticipantsContext.value = names.join(", ");
    } else {
      inputParticipantsContext.value = "";
    }
  }

  // Show or hide transcript
  renderTranscriptUI();
}

function renderTranscriptUI() {
  if (!currentTranscript || !currentTranscript.segments || currentTranscript.segments.length === 0) {
    speakersCard.style.display = "none";
    if (searchReplaceBar) searchReplaceBar.style.display = "none";
    if (replacementsAlertBanner) replacementsAlertBanner.style.display = "none";
    segmentsListEl.innerHTML = `
      <div class="no-transcript-msg">
        Esta llamada aún no ha sido transcrita.<br>
        Haz clic en <strong>✨ Transcribir Todo</strong> para la llamada completa, o en <strong>⏱️ Transcribir Segmento</strong> para seleccionar y procesar un intervalo de tiempo específico con Gemini.
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

    const txtArea = segEl.querySelector(".segment-text");
    if (txtArea) {
      txtArea.addEventListener("input", (e) => {
        if (currentTranscript && currentTranscript.segments && currentTranscript.segments[index]) {
          currentTranscript.segments[index].text = e.target.value;
        }
        if (debounceUiRefresh) {
          debounceUiRefresh();
        }
      });
    }

    segmentsListEl.appendChild(segEl);
  });

  // Populate Raw JSON
  rawJsonTextarea.value = JSON.stringify(currentTranscript, null, 2);

  // Check centralized replacements and search matches
  checkDetectedReplacements();
  if (isSearchReplaceOpen) {
    performSearch(false);
  }
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
    const context = inputParticipantsContext ? inputParticipantsContext.value.trim() : "";

    btnTranscribe.disabled = true;
    showStatusBanner("✨ Transcribiendo llamada con Gemini... Esto puede tomar desde unos segundos hasta varios minutos en grabaciones extensas. Por favor espera.", "info");

    try {
      const res = await fetch(`/api/meetings/${selectedMeeting.id}/transcribe`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          gemini_model: model,
          speakers_context: context
        })
      });
      const data = await res.json();
      if (!res.ok) {
        let errMsg = data.error || "Error al transcribir";
        if (errMsg.includes("not found") || errMsg.includes("not supported") || errMsg.includes("404")) {
          errMsg += " — Sugerencia: Selecciona 'Gemini 2.0 Flash Lite' o presiona 🔄 para actualizar los modelos activos de tu cuenta.";
        }
        throw new Error(errMsg);
      }

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

  if (btnRefreshModels) {
    btnRefreshModels.addEventListener("click", async () => {
      btnRefreshModels.classList.add("rotating");
      const list = await fetchAvailableModels();
      btnRefreshModels.classList.remove("rotating");
      if (list && list.length > 0) {
        showToast(`✅ ${list.length} modelos de Gemini detectados correctamente.`);
      } else {
        showToast("No se pudieron detectar modelos de la API.");
      }
    });
  }

  if (btnConfigRefreshModels) {
    btnConfigRefreshModels.addEventListener("click", async () => {
      const keyToTest = inputApiKey.value.trim();
      const statusEl = document.getElementById("modelsDetectStatus");
      if (statusEl) statusEl.textContent = "Consultando Google API...";
      btnConfigRefreshModels.disabled = true;
      const list = await fetchAvailableModels(keyToTest || null);
      btnConfigRefreshModels.disabled = false;
      if (list && list.length > 0) {
        if (statusEl) statusEl.textContent = `✅ ${list.length} modelos disponibles`;
        showToast(`Modelos actualizados: ${list.length} disponibles`);
      } else {
        if (statusEl) statusEl.textContent = "⚠️ No se detectaron modelos";
        showToast("No se detectaron modelos con esa clave.");
      }
    });
  }

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

  // Segment Modal Trigger Listeners
  if (btnOpenSegmentModal) {
    btnOpenSegmentModal.addEventListener("click", () => openSegmentModal());
  }
  if (btnAudioCardSegment) {
    btnAudioCardSegment.addEventListener("click", () => openSegmentModal());
  }
  if (btnTranscriptHeaderSegment) {
    btnTranscriptHeaderSegment.addEventListener("click", () => openSegmentModal());
  }

  // Segment Modal Controls
  if (btnCloseSegmentModal) {
    btnCloseSegmentModal.addEventListener("click", closeSegmentModal);
  }
  if (btnCancelSegmentModal) {
    btnCancelSegmentModal.addEventListener("click", closeSegmentModal);
  }

  if (btnSetStartToCurrent) {
    btnSetStartToCurrent.addEventListener("click", () => {
      const cur = audioPlayer ? Math.floor(audioPlayer.currentTime) : 0;
      inputSegmentStart.value = formatDuration(cur);
      updateSegmentDurationCalc();
    });
  }

  if (btnSetEndToCurrent) {
    btnSetEndToCurrent.addEventListener("click", () => {
      const cur = audioPlayer ? Math.floor(audioPlayer.currentTime) : 0;
      inputSegmentEnd.value = formatDuration(cur);
      updateSegmentDurationCalc();
    });
  }

  if (btnSetEndToTotal) {
    btnSetEndToTotal.addEventListener("click", () => {
      const total = selectedMeeting?.duration_seconds || (audioPlayer ? audioPlayer.duration : 0) || 0;
      inputSegmentEnd.value = formatDuration(total);
      updateSegmentDurationCalc();
    });
  }

  if (inputSegmentStart) {
    inputSegmentStart.addEventListener("input", updateSegmentDurationCalc);
  }
  if (inputSegmentEnd) {
    inputSegmentEnd.addEventListener("input", updateSegmentDurationCalc);
  }

  // Quick adjust buttons (+5s, -5s, +1m, etc.)
  document.querySelectorAll(".btn-quick-adjust").forEach(btn => {
    btn.addEventListener("click", () => {
      const target = btn.dataset.target;
      const input = target === "start" ? inputSegmentStart : inputSegmentEnd;
      const totalDuration = selectedMeeting?.duration_seconds || (audioPlayer ? audioPlayer.duration : 0) || 0;

      if (btn.dataset.set !== undefined) {
        input.value = formatDuration(parseFloat(btn.dataset.set));
      } else if (btn.dataset.delta !== undefined) {
        const delta = parseFloat(btn.dataset.delta);
        let cur = parseTimeString(input.value);
        cur = Math.max(0, Math.min(totalDuration, cur + delta));
        input.value = formatDuration(cur);
      }
      updateSegmentDurationCalc();
    });
  });

  if (btnPreviewSegmentAudio) {
    btnPreviewSegmentAudio.addEventListener("click", startSegmentPreview);
  }
  if (btnStopPreviewSegmentAudio) {
    btnStopPreviewSegmentAudio.addEventListener("click", stopSegmentPreview);
  }

  if (btnExecuteSegmentTranscribe) {
    btnExecuteSegmentTranscribe.addEventListener("click", executeSegmentTranscription);
  }
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
      if (isSegmentPreviewActive) stopSegmentPreview();
      audioCard.classList.remove("is-playing");
      if (audioStatusBadge) {
        audioStatusBadge.textContent = "⏸️ PAUSADO";
        audioStatusBadge.className = "audio-floating-indicator paused";
      }
    });

    audioPlayer.addEventListener("ended", () => {
      if (isSegmentPreviewActive) stopSegmentPreview();
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

      // Stop audio if segment preview reached its end
      if (isSegmentPreviewActive && segmentPreviewEndSec !== null) {
        if (audioPlayer.currentTime >= segmentPreviewEndSec) {
          stopSegmentPreview();
        }
      }

      // Update position badges in segment modal if open
      if (segmentModal && segmentModal.style.display === "flex") {
        updateLiveAudioBadges();
      }
    });
  }

  // Global keyboard shortcuts to pause/resume playback and close modals
  document.addEventListener("keydown", (e) => {
    // Escape key closes modals and search bar
    if (e.key === "Escape") {
      if (replacementsModal && replacementsModal.style.display === "flex") {
        closeReplacementsModal();
        return;
      }
      if (segmentModal && segmentModal.style.display === "flex") {
        closeSegmentModal();
        return;
      }
      if (configModal && configModal.style.display === "flex") {
        configModal.style.display = "none";
        return;
      }
      const logsModal = document.getElementById("logsModal");
      if (logsModal && logsModal.style.display === "flex") {
        logsModal.style.display = "none";
        return;
      }
      if (isSearchReplaceOpen) {
        toggleSearchReplace(false);
        return;
      }
    }

    // Cmd+F or Ctrl+F: Open search and replace in transcript
    if ((e.metaKey || e.ctrlKey) && (e.key === "f" || e.key === "F")) {
      if (currentTranscript && currentTranscript.segments && currentTranscript.segments.length > 0) {
        e.preventDefault();
        toggleSearchReplace(true);
        return;
      }
    }

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

// --- Segment Transcription Functions ---
function parseTimeString(timeStr) {
  if (typeof timeStr === "number") return Math.max(0, timeStr);
  if (!timeStr || typeof timeStr !== "string") return 0;
  const parts = timeStr.trim().split(":");
  try {
    if (parts.length === 3) {
      return Math.max(0, parseFloat(parts[0]) * 3600 + parseFloat(parts[1]) * 60 + parseFloat(parts[2]));
    } else if (parts.length === 2) {
      return Math.max(0, parseFloat(parts[0]) * 60 + parseFloat(parts[1]));
    } else if (parts.length === 1) {
      const val = parseFloat(parts[0]);
      return isNaN(val) ? 0 : Math.max(0, val);
    }
  } catch (e) {
    return 0;
  }
  return 0;
}

function openSegmentModal(initialStartSec = null, initialEndSec = null) {
  if (!selectedMeeting) {
    showToast("Selecciona una llamada primero");
    return;
  }
  if (!selectedMeeting.has_audio) {
    showToast("Esta grabación no tiene archivo de audio");
    return;
  }

  const totalDuration = selectedMeeting.duration_seconds || (audioPlayer && audioPlayer.duration) || 0;

  // Set Meeting Name and Total Duration Badge
  if (segmentCallName) {
    segmentCallName.textContent = selectedMeeting.name || selectedMeeting.folder_name || selectedMeeting.id;
  }
  if (segmentCallTotalDuration) {
    segmentCallTotalDuration.textContent = `⏱️ Duración: ${formatDuration(totalDuration)}`;
  }

  // Compute default start/end times
  let startSec = 0;
  if (initialStartSec !== null && !isNaN(initialStartSec)) {
    startSec = Math.max(0, Math.min(totalDuration, initialStartSec));
  } else if (audioPlayer && audioPlayer.currentTime > 0) {
    startSec = Math.floor(audioPlayer.currentTime);
  }

  let endSec = totalDuration;
  if (initialEndSec !== null && !isNaN(initialEndSec)) {
    endSec = Math.max(startSec + 1, Math.min(totalDuration, initialEndSec));
  } else {
    // 1-minute default window or total duration
    endSec = totalDuration > 0 ? Math.min(totalDuration, startSec + 60) : 60;
    if (endSec <= startSec) endSec = totalDuration;
  }

  if (inputSegmentStart) inputSegmentStart.value = formatDuration(startSec);
  if (inputSegmentEnd) inputSegmentEnd.value = formatDuration(endSec);

  // Sync selected model
  if (segmentModelSelect && selectModel) {
    segmentModelSelect.value = selectModel.value;
  }

  // Sync participants context
  if (segmentParticipantsContext) {
    if (inputParticipantsContext && inputParticipantsContext.value.trim()) {
      segmentParticipantsContext.value = inputParticipantsContext.value.trim();
    } else if (currentTranscript && currentTranscript.speakers) {
      const mapping = currentTranscript.speaker_mapping || {};
      const names = currentTranscript.speakers.map(s => mapping[s] || s);
      segmentParticipantsContext.value = names.join(", ");
    } else {
      segmentParticipantsContext.value = "";
    }
  }

  // Ensure default merge mode is checked
  const mergeRadio = document.querySelector('input[name="segmentMergeMode"][value="merge"]');
  if (mergeRadio) mergeRadio.checked = true;

  updateSegmentDurationCalc();
  updateLiveAudioBadges();

  if (segmentModal) segmentModal.style.display = "flex";
}

function closeSegmentModal() {
  stopSegmentPreview();
  if (segmentModal) segmentModal.style.display = "none";
}

function updateLiveAudioBadges() {
  const currentPos = audioPlayer ? Math.floor(audioPlayer.currentTime) : 0;
  const formatted = formatDuration(currentPos);
  if (startCurrentPosBadge) startCurrentPosBadge.textContent = formatted;
  if (endCurrentPosBadge) endCurrentPosBadge.textContent = formatted;
}

function updateSegmentDurationCalc() {
  if (!inputSegmentStart || !inputSegmentEnd) return false;
  const totalDuration = selectedMeeting?.duration_seconds || (audioPlayer && audioPlayer.duration) || 0;
  const startSec = parseTimeString(inputSegmentStart.value);
  const endSec = parseTimeString(inputSegmentEnd.value);

  if (isNaN(startSec) || isNaN(endSec) || endSec <= startSec) {
    if (segmentCalculatedDuration) {
      segmentCalculatedDuration.textContent = "Intervalo no válido";
      segmentCalculatedDuration.className = "preview-val invalid";
    }
    if (segmentRangeSummary) {
      segmentRangeSummary.textContent = "El tiempo de fin debe ser posterior al inicio";
    }
    if (btnExecuteSegmentTranscribe) btnExecuteSegmentTranscribe.disabled = true;
    if (btnPreviewSegmentAudio) btnPreviewSegmentAudio.disabled = true;
    return false;
  }

  const duration = endSec - startSec;
  if (duration < 0.5) {
    if (segmentCalculatedDuration) {
      segmentCalculatedDuration.textContent = "Muy breve (< 1s)";
      segmentCalculatedDuration.className = "preview-val invalid";
    }
    if (segmentRangeSummary) {
      segmentRangeSummary.textContent = "El intervalo debe durar al menos 1 segundo";
    }
    if (btnExecuteSegmentTranscribe) btnExecuteSegmentTranscribe.disabled = true;
    if (btnPreviewSegmentAudio) btnPreviewSegmentAudio.disabled = true;
    return false;
  }

  if (segmentCalculatedDuration) {
    segmentCalculatedDuration.textContent = formatDuration(duration);
    segmentCalculatedDuration.className = "preview-val";
  }
  if (segmentRangeSummary) {
    segmentRangeSummary.textContent = `(${formatDuration(startSec)} ➔ ${formatDuration(endSec)})`;
  }
  if (btnExecuteSegmentTranscribe) btnExecuteSegmentTranscribe.disabled = false;
  if (btnPreviewSegmentAudio) btnPreviewSegmentAudio.disabled = false;
  return true;
}

function startSegmentPreview() {
  if (!updateSegmentDurationCalc()) return;
  const startSec = parseTimeString(inputSegmentStart.value);
  const endSec = parseTimeString(inputSegmentEnd.value);

  if (!audioPlayer || !audioPlayer.src) return;

  isSegmentPreviewActive = true;
  segmentPreviewEndSec = endSec;

  audioPlayer.currentTime = startSec;
  audioPlayer.play();

  if (btnPreviewSegmentAudio) btnPreviewSegmentAudio.style.display = "none";
  if (btnStopPreviewSegmentAudio) btnStopPreviewSegmentAudio.style.display = "inline-flex";
}

function stopSegmentPreview() {
  isSegmentPreviewActive = false;
  segmentPreviewEndSec = null;
  if (audioPlayer && !audioPlayer.paused) {
    audioPlayer.pause();
  }
  if (btnPreviewSegmentAudio) btnPreviewSegmentAudio.style.display = "inline-flex";
  if (btnStopPreviewSegmentAudio) btnStopPreviewSegmentAudio.style.display = "none";
}

async function executeSegmentTranscription() {
  if (!selectedMeeting) return;
  if (!updateSegmentDurationCalc()) return;

  const startSec = parseTimeString(inputSegmentStart.value);
  const endSec = parseTimeString(inputSegmentEnd.value);
  const model = segmentModelSelect ? segmentModelSelect.value : selectModel.value;

  const mergeRadio = document.querySelector('input[name="segmentMergeMode"]:checked');
  const mergeMode = mergeRadio ? mergeRadio.value : "merge";

  stopSegmentPreview();
  closeSegmentModal();

  const formattedRange = `${formatDuration(startSec)} - ${formatDuration(endSec)}`;
  showStatusBanner(`✨ Transcribiendo segmento (${formattedRange}) con Gemini... Por favor espera.`, "info");
  btnTranscribe.disabled = true;
  if (btnOpenSegmentModal) btnOpenSegmentModal.disabled = true;
  if (btnAudioCardSegment) btnAudioCardSegment.disabled = true;

  try {
    const context = segmentParticipantsContext && segmentParticipantsContext.value.trim()
      ? segmentParticipantsContext.value.trim()
      : (inputParticipantsContext ? inputParticipantsContext.value.trim() : "");

    const res = await fetch(`/api/meetings/${selectedMeeting.id}/transcribe-segment`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        start_seconds: startSec,
        end_seconds: endSec,
        gemini_model: model,
        merge_mode: mergeMode,
        speakers_context: context
      })
    });

    const data = await res.json();
    if (!res.ok) {
      let errMsg = data.error || "Error al transcribir segmento";
      if (errMsg.includes("not found") || errMsg.includes("not supported") || errMsg.includes("404")) {
        errMsg += " — Sugerencia: Selecciona 'Gemini 2.0 Flash Lite' o presiona 🔄 para actualizar los modelos activos de tu cuenta.";
      }
      throw new Error(errMsg);
    }

    selectedMeeting = data.meeting;
    currentTranscript = selectedMeeting.transcript;

    if (data.warning) {
      showToast(`⚠️ ${data.warning}`, 6000);
    } else {
      showToast(`¡Transcripción del tramo (${formattedRange}) completada con éxito!`);
    }

    hideStatusBanner();
    renderMeetingDetail();
    loadMeetings(selectedMeeting.id);

    // Seek player to start of segment for instant playback review
    seekAudioTo(startSec);

  } catch (err) {
    showStatusBanner(`⚠️ Error en transcripción de segmento: ${err.message}`, "error");
    showToast(`Error: ${err.message}`);
  } finally {
    btnTranscribe.disabled = false;
    if (btnOpenSegmentModal) btnOpenSegmentModal.disabled = false;
    if (btnAudioCardSegment) btnAudioCardSegment.disabled = false;
  }
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

// ==========================================================================
// Search & Replace and Centralized Replacements Logic
// ==========================================================================

let debounceTimer = null;
function debounceUiRefresh() {
  clearTimeout(debounceTimer);
  debounceTimer = setTimeout(() => {
    if (isSearchReplaceOpen) performSearch(false);
    checkDetectedReplacements();
  }, 350);
}

function buildSearchRegex(term, caseSensitive, wholeWord, global = true) {
  if (!term) return null;
  const escaped = term.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
  let flags = global ? "gu" : "u";
  if (!caseSensitive) flags += "i";
  if (!wholeWord) {
    return new RegExp(escaped, flags);
  }
  const startsWithWord = /^[\p{L}\p{N}_]/u.test(term);
  const endsWithWord = /[\p{L}\p{N}_]$/u.test(term);
  const prefix = startsWithWord ? "(?<![\\p{L}\\p{N}_])" : "(?<!\\S)";
  const suffix = endsWithWord ? "(?![\\p{L}\\p{N}_])" : "(?!\\S)";
  return new RegExp(`${prefix}${escaped}${suffix}`, flags);
}

async function loadCentralizedReplacements() {
  try {
    const res = await fetch("/api/replacements");
    const data = await res.json();
    centralizedReplacements = data.replacements || [];
    renderReplacementsModalList();
    checkDetectedReplacements();
  } catch (err) {
    console.error("Error loading centralized replacements:", err);
  }
}

function toggleSearchReplace(forceState) {
  if (!currentTranscript || !currentTranscript.segments || currentTranscript.segments.length === 0) {
    showToast("La llamada no tiene transcripción activa para buscar");
    return;
  }
  isSearchReplaceOpen = forceState !== undefined ? forceState : !isSearchReplaceOpen;
  if (searchReplaceBar) {
    searchReplaceBar.style.display = isSearchReplaceOpen ? "flex" : "none";
  }
  if (btnToggleSearchReplace) {
    btnToggleSearchReplace.classList.toggle("active", isSearchReplaceOpen);
  }
  if (isSearchReplaceOpen) {
    const activeEl = document.activeElement;
    if (activeEl && activeEl.classList.contains("segment-text")) {
      const selText = activeEl.value.substring(activeEl.selectionStart, activeEl.selectionEnd);
      if (selText && selText.trim()) {
        srSearchInput.value = selText.trim();
      }
    }
    if (srSearchInput) {
      srSearchInput.focus();
      srSearchInput.select();
    }
    performSearch(true);
  } else {
    clearSearchHighlights();
    searchMatches = [];
    currentMatchIndex = -1;
  }
}

function clearSearchHighlights() {
  const segmentItems = segmentsListEl.querySelectorAll(".segment-item");
  segmentItems.forEach(el => {
    el.classList.remove("sr-has-match", "sr-active-match");
  });
}

function performSearch(resetActiveIndex = false) {
  const term = srSearchInput ? srSearchInput.value.trim() : "";
  if (!term || !currentTranscript || !currentTranscript.segments) {
    searchMatches = [];
    currentMatchIndex = -1;
    if (srMatchCounter) {
      srMatchCounter.textContent = "0 coincidencias";
      srMatchCounter.className = "sr-badge-counter";
    }
    if (btnSrPrev) btnSrPrev.disabled = true;
    if (btnSrNext) btnSrNext.disabled = true;
    if (srStatusText) srStatusText.textContent = "";
    clearSearchHighlights();
    return;
  }

  const caseSensitive = srCaseSensitive ? srCaseSensitive.checked : false;
  const wholeWord = srWholeWord ? srWholeWord.checked : true;
  let regex = null;
  try {
    regex = buildSearchRegex(term, caseSensitive, wholeWord, true);
  } catch (e) {
    console.error("Regex build error:", e);
    return;
  }

  if (!regex) return;

  searchMatches = [];
  const segmentItems = segmentsListEl.querySelectorAll(".segment-item");

  segmentItems.forEach((item, idx) => {
    const textarea = item.querySelector(".segment-text");
    const text = textarea ? textarea.value : (currentTranscript.segments[idx]?.text || "");
    regex.lastIndex = 0;
    let m;
    let hasMatch = false;
    while ((m = regex.exec(text)) !== null) {
      hasMatch = true;
      searchMatches.push({
        segmentIndex: idx,
        startIndex: m.index,
        endIndex: m.index + m[0].length,
        matchText: m[0]
      });
      if (m.index === regex.lastIndex) regex.lastIndex++;
    }
    if (hasMatch) {
      item.classList.add("sr-has-match");
    } else {
      item.classList.remove("sr-has-match", "sr-active-match");
    }
  });

  if (searchMatches.length === 0) {
    if (srMatchCounter) {
      srMatchCounter.textContent = "0 coincidencias";
      srMatchCounter.className = "sr-badge-counter no-matches";
    }
    if (btnSrPrev) btnSrPrev.disabled = true;
    if (btnSrNext) btnSrNext.disabled = true;
    if (srStatusText) srStatusText.textContent = "No se encontraron coincidencias.";
    currentMatchIndex = -1;
    clearSearchHighlights();
  } else {
    if (btnSrPrev) btnSrPrev.disabled = false;
    if (btnSrNext) btnSrNext.disabled = false;
    if (srMatchCounter) {
      srMatchCounter.className = "sr-badge-counter has-matches";
    }
    if (resetActiveIndex || currentMatchIndex < 0 || currentMatchIndex >= searchMatches.length) {
      currentMatchIndex = 0;
    }
    goToMatch(currentMatchIndex);
  }
}

function goToMatch(index) {
  if (searchMatches.length === 0) return;
  currentMatchIndex = index;
  const match = searchMatches[currentMatchIndex];

  if (srMatchCounter) {
    srMatchCounter.textContent = `${currentMatchIndex + 1} de ${searchMatches.length}`;
  }
  if (srStatusText) {
    srStatusText.textContent = `Coincidencia ${currentMatchIndex + 1} de ${searchMatches.length}`;
  }

  const segmentItems = segmentsListEl.querySelectorAll(".segment-item");
  segmentItems.forEach((item, idx) => {
    if (idx === match.segmentIndex) {
      item.classList.add("sr-active-match");
      item.scrollIntoView({ behavior: "smooth", block: "nearest" });
      const textarea = item.querySelector(".segment-text");
      if (textarea) {
        textarea.focus();
        textarea.setSelectionRange(match.startIndex, match.endIndex);
      }
    } else {
      item.classList.remove("sr-active-match");
    }
  });
}

function replaceOneMatch() {
  if (searchMatches.length === 0 || currentMatchIndex < 0) {
    showToast("No hay ninguna coincidencia activa para reemplazar");
    return;
  }
  const match = searchMatches[currentMatchIndex];
  const replacement = srReplaceInput ? srReplaceInput.value : "";
  const segmentItems = segmentsListEl.querySelectorAll(".segment-item");
  const targetItem = segmentItems[match.segmentIndex];
  if (!targetItem) return;

  const textarea = targetItem.querySelector(".segment-text");
  if (!textarea) return;

  const oldVal = textarea.value;
  const newVal = oldVal.substring(0, match.startIndex) + replacement + oldVal.substring(match.endIndex);
  textarea.value = newVal;

  if (currentTranscript && currentTranscript.segments && currentTranscript.segments[match.segmentIndex]) {
    currentTranscript.segments[match.segmentIndex].text = newVal;
  }

  showToast("Coincidencia reemplazada");
  const nextTarget = currentMatchIndex;
  performSearch(false);
  if (searchMatches.length > 0) {
    goToMatch(Math.min(nextTarget, searchMatches.length - 1));
  }
  checkDetectedReplacements();
  rawJsonTextarea.value = JSON.stringify(collectTranscriptFromUI(), null, 2);
}

function replaceAllMatches() {
  const term = srSearchInput ? srSearchInput.value.trim() : "";
  if (!term) {
    showToast("Escribe un término a buscar");
    return;
  }
  const replacement = srReplaceInput ? srReplaceInput.value : "";
  const caseSensitive = srCaseSensitive ? srCaseSensitive.checked : false;
  const wholeWord = srWholeWord ? srWholeWord.checked : true;
  let regex = null;
  try {
    regex = buildSearchRegex(term, caseSensitive, wholeWord, true);
  } catch (e) {
    console.error("Regex build error:", e);
    return;
  }

  if (!regex) return;

  let totalReplaced = 0;
  let segmentsCount = 0;
  const segmentItems = segmentsListEl.querySelectorAll(".segment-item");

  segmentItems.forEach((item, idx) => {
    const textarea = item.querySelector(".segment-text");
    if (!textarea) return;
    const text = textarea.value;
    regex.lastIndex = 0;
    const m = text.match(regex);
    if (m && m.length > 0) {
      totalReplaced += m.length;
      segmentsCount++;
      const updated = text.replace(regex, replacement);
      textarea.value = updated;
      if (currentTranscript && currentTranscript.segments && currentTranscript.segments[idx]) {
        currentTranscript.segments[idx].text = updated;
      }
    }
  });

  if (totalReplaced === 0) {
    showToast("No se encontraron coincidencias para reemplazar");
  } else {
    showToast(`Se reemplazaron ${totalReplaced} apariciones en ${segmentsCount} segmento(s). Recuerda guardar cambios.`);
    if (srStatusText) srStatusText.textContent = `Se reemplazaron ${totalReplaced} apariciones.`;
    performSearch(true);
    checkDetectedReplacements();
    rawJsonTextarea.value = JSON.stringify(collectTranscriptFromUI(), null, 2);
  }
}

async function saveCurrentSearchToCentral() {
  const findTerm = srSearchInput ? srSearchInput.value.trim() : "";
  const replaceTerm = srReplaceInput ? srReplaceInput.value.trim() : "";
  if (!findTerm) {
    showToast("Escribe la palabra que deseas agregar a la lista centralizada");
    return;
  }
  const caseSensitive = srCaseSensitive ? srCaseSensitive.checked : false;
  const wholeWord = srWholeWord ? srWholeWord.checked : true;

  try {
    const res = await fetch("/api/replacements", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        find: findTerm,
        replace: replaceTerm,
        case_sensitive: caseSensitive,
        whole_word: wholeWord
      })
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.error || "Error al guardar regla");
    centralizedReplacements = data.replacements || [];
    showToast(`"${findTerm}" ➔ "${replaceTerm}" guardado en la lista centralizada`);
    checkDetectedReplacements();
    renderReplacementsModalList();
  } catch (err) {
    showToast(`Error: ${err.message}`);
  }
}

function checkDetectedReplacements() {
  if (!selectedMeeting || !currentTranscript || !currentTranscript.segments || currentTranscript.segments.length === 0) {
    if (replacementsAlertBanner) replacementsAlertBanner.style.display = "none";
    activeDetectedMatches = [];
    return;
  }

  if (centralizedReplacements.length === 0) {
    if (replacementsAlertBanner) replacementsAlertBanner.style.display = "none";
    activeDetectedMatches = [];
    return;
  }

  const matches = [];
  let totalCount = 0;

  centralizedReplacements.forEach(rule => {
    const findTerm = (rule.find || "").trim();
    if (!findTerm) return;
    let reg = null;
    try {
      reg = buildSearchRegex(findTerm, rule.case_sensitive, rule.whole_word, true);
    } catch (e) {
      return;
    }
    if (!reg) return;

    let ruleMatches = 0;
    const segmentItems = segmentsListEl.querySelectorAll(".segment-item");
    segmentItems.forEach((item, idx) => {
      const textarea = item.querySelector(".segment-text");
      const text = textarea ? textarea.value : (currentTranscript.segments[idx]?.text || "");
      reg.lastIndex = 0;
      const found = text.match(reg);
      if (found) ruleMatches += found.length;
    });

    if (ruleMatches > 0) {
      totalCount += ruleMatches;
      matches.push({
        ...rule,
        count: ruleMatches
      });
    }
  });

  activeDetectedMatches = matches;

  if (matches.length > 0 && !dismissedMeetingAlerts.has(selectedMeeting.id)) {
    if (replacementsAlertBanner) {
      replacementsAlertBanner.classList.remove("success-mode");
      replacementsAlertBanner.style.display = "flex";
    }
    if (repAlertTotalCount) repAlertTotalCount.textContent = totalCount;
    if (repAlertSubtitle) {
      repAlertSubtitle.textContent = `Se encontraron ${totalCount} apariciones de ${matches.length} término(s) de tu lista de reemplazos frecuentes.`;
    }
    if (repAlertChips) {
      repAlertChips.innerHTML = "";
      matches.forEach(item => {
        const chip = document.createElement("div");
        chip.className = "rep-chip";
        chip.innerHTML = `
          <span class="rep-chip-wrong">${escapeHtml(item.find)}</span>
          <span class="rep-chip-arrow">➔</span>
          <span class="rep-chip-right">${escapeHtml(item.replace)}</span>
          <span class="rep-chip-count" title="${item.count} apariciones">${item.count}</span>
          <button type="button" class="btn-chip-apply" title="Reemplazar solo '${escapeHtml(item.find)}'">Reemplazar</button>
        `;
        const applyBtn = chip.querySelector(".btn-chip-apply");
        if (applyBtn) {
          applyBtn.addEventListener("click", () => applySingleDetectedReplacement(item.id));
        }
        repAlertChips.appendChild(chip);
      });
    }
  } else {
    if (replacementsAlertBanner && !replacementsAlertBanner.classList.contains("success-mode")) {
      replacementsAlertBanner.style.display = "none";
    }
  }

  // Update modal apply button
  if (btnModalApplyAllToMeeting && modalMatchesCount) {
    if (matches.length > 0) {
      btnModalApplyAllToMeeting.style.display = "inline-flex";
      modalMatchesCount.textContent = totalCount;
    } else {
      btnModalApplyAllToMeeting.style.display = "none";
    }
  }

  renderReplacementsModalList();
}

async function applyAllDetectedReplacements() {
  if (!selectedMeeting || !currentTranscript) return;
  if (activeDetectedMatches.length === 0) {
    showToast("No hay términos frecuentes detectados en esta llamada");
    return;
  }
  const ruleIds = activeDetectedMatches.map(m => m.id);
  try {
    const res = await fetch(`/api/meetings/${selectedMeeting.id}/apply-replacements`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ rule_ids: ruleIds })
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.error || "Error al aplicar reemplazos");
    selectedMeeting = data.meeting;
    currentTranscript = selectedMeeting.transcript;
    renderTranscriptUI();
    showToast(`¡Se reemplazaron ${data.replacements_count} términos frecuentes con éxito!`);

    if (replacementsAlertBanner) {
      replacementsAlertBanner.classList.add("success-mode");
      if (repAlertSubtitle) repAlertSubtitle.textContent = "Todos los términos frecuentes fueron corregidos.";
      if (repAlertChips) repAlertChips.innerHTML = "";
      setTimeout(() => {
        if (replacementsAlertBanner) replacementsAlertBanner.style.display = "none";
      }, 3500);
    }
    loadMeetings(selectedMeeting.id);
  } catch (err) {
    showToast(`Error al aplicar reemplazos: ${err.message}`);
  }
}

async function applySingleDetectedReplacement(ruleId) {
  if (!selectedMeeting || !currentTranscript) return;
  try {
    const res = await fetch(`/api/meetings/${selectedMeeting.id}/apply-replacements`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ rule_ids: [ruleId] })
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.error || "Error al aplicar reemplazo");
    selectedMeeting = data.meeting;
    currentTranscript = selectedMeeting.transcript;
    renderTranscriptUI();
    showToast(`Término reemplazado (${data.replacements_count} cambios)`);
    loadMeetings(selectedMeeting.id);
  } catch (err) {
    showToast(`Error: ${err.message}`);
  }
}

function openReplacementsModal() {
  if (replacementsModal) replacementsModal.style.display = "flex";
  resetReplacementForm();
  renderReplacementsModalList();
}

function closeReplacementsModal() {
  if (replacementsModal) replacementsModal.style.display = "none";
  resetReplacementForm();
}

function resetReplacementForm() {
  if (inputEditRepId) inputEditRepId.value = "";
  if (inputNewRepFind) inputNewRepFind.value = "";
  if (inputNewRepReplace) inputNewRepReplace.value = "";
  if (checkNewRepWholeWord) checkNewRepWholeWord.checked = true;
  if (checkNewRepCase) checkNewRepCase.checked = false;
  if (repFormTitle) repFormTitle.textContent = "➕ Agregar Nuevo Término de Reemplazo";
  if (btnAddNewReplacement) btnAddNewReplacement.textContent = "+ Guardar Término";
  if (btnCancelEditRep) btnCancelEditRep.style.display = "none";
}

function editReplacementRule(ruleId) {
  const rule = centralizedReplacements.find(r => r.id === ruleId);
  if (!rule) return;
  if (inputEditRepId) inputEditRepId.value = rule.id;
  if (inputNewRepFind) inputNewRepFind.value = rule.find;
  if (inputNewRepReplace) inputNewRepReplace.value = rule.replace;
  if (checkNewRepWholeWord) checkNewRepWholeWord.checked = Boolean(rule.whole_word);
  if (checkNewRepCase) checkNewRepCase.checked = Boolean(rule.case_sensitive);
  if (repFormTitle) repFormTitle.textContent = "✏️ Editar Término de Reemplazo";
  if (btnAddNewReplacement) btnAddNewReplacement.textContent = "Actualizar Término";
  if (btnCancelEditRep) btnCancelEditRep.style.display = "inline-block";
  if (inputNewRepFind) {
    inputNewRepFind.focus();
    inputNewRepFind.select();
  }
}

async function saveReplacementRuleFromForm() {
  const findTerm = inputNewRepFind ? inputNewRepFind.value.trim() : "";
  const replaceTerm = inputNewRepReplace ? inputNewRepReplace.value.trim() : "";
  if (!findTerm) {
    showToast("El término a buscar no puede estar vacío");
    return;
  }
  const wholeWord = checkNewRepWholeWord ? checkNewRepWholeWord.checked : true;
  const caseSensitive = checkNewRepCase ? checkNewRepCase.checked : false;
  const editId = inputEditRepId ? inputEditRepId.value : "";

  const url = editId ? `/api/replacements/${editId}` : "/api/replacements";
  try {
    const res = await fetch(url, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        find: findTerm,
        replace: replaceTerm,
        whole_word: wholeWord,
        case_sensitive: caseSensitive
      })
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.error || "Error al guardar regla");
    centralizedReplacements = data.replacements || [];
    showToast(editId ? "Regla actualizada" : "Regla agregada a la lista centralizada");
    resetReplacementForm();
    renderReplacementsModalList();
    checkDetectedReplacements();
  } catch (err) {
    showToast(`Error: ${err.message}`);
  }
}

async function deleteReplacementRule(ruleId) {
  const rule = centralizedReplacements.find(r => r.id === ruleId);
  const name = rule ? rule.find : "esta regla";
  if (!confirm(`¿Eliminar el reemplazo de "${name}" de la lista centralizada?`)) {
    return;
  }
  try {
    const res = await fetch(`/api/replacements/${ruleId}`, { method: "DELETE" });
    const data = await res.json();
    if (!res.ok) throw new Error(data.error || "Error al eliminar");
    centralizedReplacements = data.replacements || [];
    showToast("Regla eliminada");
    renderReplacementsModalList();
    checkDetectedReplacements();
  } catch (err) {
    showToast(`Error al eliminar regla: ${err.message}`);
  }
}

function renderReplacementsModalList() {
  if (!repItemsList) return;
  const filterQuery = repFilterInput ? repFilterInput.value.trim().toLowerCase() : "";
  let filtered = centralizedReplacements;
  if (filterQuery) {
    filtered = filtered.filter(r =>
      (r.find || "").toLowerCase().includes(filterQuery) ||
      (r.replace || "").toLowerCase().includes(filterQuery)
    );
  }

  if (repTotalRulesBadge) {
    repTotalRulesBadge.textContent = `${centralizedReplacements.length} regla${centralizedReplacements.length === 1 ? "" : "s"}`;
  }

  if (filtered.length === 0) {
    repItemsList.innerHTML = `<div class="rep-empty-state">${centralizedReplacements.length === 0 ? "No hay reglas de reemplazo guardadas todavía. Agrega tus tecnicismos arriba." : "No hay reglas que coincidan con la búsqueda."}</div>`;
    return;
  }

  repItemsList.innerHTML = "";
  filtered.forEach(rule => {
    const detected = activeDetectedMatches.find(m => m.id === rule.id);
    const matchCount = detected ? detected.count : 0;

    const card = document.createElement("div");
    card.className = "rep-item-card";
    card.innerHTML = `
      <div class="rep-item-info">
        <div class="rep-item-pair">
          <span class="rep-item-wrong">${escapeHtml(rule.find)}</span>
          <span class="rep-item-arrow">➔</span>
          <span class="rep-item-right">${escapeHtml(rule.replace)}</span>
        </div>
        <div class="rep-item-meta">
          ${rule.whole_word ? '<span class="rep-tag-badge">Palabra completa</span>' : '<span class="rep-tag-badge">Subcadena</span>'}
          ${rule.case_sensitive ? '<span class="rep-tag-badge">Sensible a mayúsculas</span>' : ''}
          ${matchCount > 0 ? `<span class="rep-match-badge">⚠️ ${matchCount} en llamada actual</span>` : ""}
        </div>
      </div>
      <div class="rep-item-actions">
        ${matchCount > 0 ? `<button type="button" class="btn btn-sm btn-warning btn-apply-here" title="Reemplazar en esta llamada">⚡ Reemplazar (${matchCount})</button>` : ""}
        <button type="button" class="btn-icon btn-edit-rep" title="Editar regla">✏️</button>
        <button type="button" class="btn-icon btn-del-rep" title="Eliminar regla">🗑️</button>
      </div>
    `;

    const applyBtn = card.querySelector(".btn-apply-here");
    if (applyBtn) {
      applyBtn.addEventListener("click", () => applySingleDetectedReplacement(rule.id));
    }
    const editBtn = card.querySelector(".btn-edit-rep");
    if (editBtn) {
      editBtn.addEventListener("click", () => editReplacementRule(rule.id));
    }
    const delBtn = card.querySelector(".btn-del-rep");
    if (delBtn) {
      delBtn.addEventListener("click", () => deleteReplacementRule(rule.id));
    }

    repItemsList.appendChild(card);
  });
}

function setupSearchReplaceAndReplacements() {
  if (btnToggleSearchReplace) {
    btnToggleSearchReplace.addEventListener("click", () => toggleSearchReplace());
  }
  if (btnSrClose) {
    btnSrClose.addEventListener("click", () => toggleSearchReplace(false));
  }
  if (srSearchInput) {
    srSearchInput.addEventListener("input", () => performSearch(true));
    srSearchInput.addEventListener("keydown", (e) => {
      if (e.key === "Enter") {
        e.preventDefault();
        if (e.shiftKey) {
          if (btnSrPrev) btnSrPrev.click();
        } else {
          if (btnSrNext) btnSrNext.click();
        }
      }
    });
  }
  if (srReplaceInput) {
    srReplaceInput.addEventListener("keydown", (e) => {
      if (e.key === "Enter") {
        e.preventDefault();
        if (e.metaKey || e.ctrlKey) {
          if (btnSrReplaceAll) btnSrReplaceAll.click();
        } else {
          if (btnSrReplaceOne) btnSrReplaceOne.click();
        }
      }
    });
  }
  if (btnSrPrev) {
    btnSrPrev.addEventListener("click", () => {
      if (searchMatches.length > 0) {
        goToMatch((currentMatchIndex - 1 + searchMatches.length) % searchMatches.length);
      }
    });
  }
  if (btnSrNext) {
    btnSrNext.addEventListener("click", () => {
      if (searchMatches.length > 0) {
        goToMatch((currentMatchIndex + 1) % searchMatches.length);
      }
    });
  }
  if (srCaseSensitive) {
    srCaseSensitive.addEventListener("change", () => performSearch(true));
  }
  if (srWholeWord) {
    srWholeWord.addEventListener("change", () => performSearch(true));
  }
  if (btnSrReplaceOne) {
    btnSrReplaceOne.addEventListener("click", replaceOneMatch);
  }
  if (btnSrReplaceAll) {
    btnSrReplaceAll.addEventListener("click", replaceAllMatches);
  }
  if (btnSrSaveToCentral) {
    btnSrSaveToCentral.addEventListener("click", saveCurrentSearchToCentral);
  }

  // Replacements Alert Banner
  if (btnApplyAllDetectedRep) {
    btnApplyAllDetectedRep.addEventListener("click", applyAllDetectedReplacements);
  }
  if (btnOpenRepFromBanner) {
    btnOpenRepFromBanner.addEventListener("click", openReplacementsModal);
  }
  if (btnDismissRepAlert) {
    btnDismissRepAlert.addEventListener("click", () => {
      if (selectedMeeting) dismissedMeetingAlerts.add(selectedMeeting.id);
      if (replacementsAlertBanner) replacementsAlertBanner.style.display = "none";
    });
  }

  // Centralized Replacements Modal
  if (btnReplacementsModal) {
    btnReplacementsModal.addEventListener("click", openReplacementsModal);
  }
  if (btnCloseReplacementsModal) {
    btnCloseReplacementsModal.addEventListener("click", closeReplacementsModal);
  }
  if (btnExitReplacementsModal) {
    btnExitReplacementsModal.addEventListener("click", closeReplacementsModal);
  }
  if (btnAddNewReplacement) {
    btnAddNewReplacement.addEventListener("click", saveReplacementRuleFromForm);
  }
  if (btnCancelEditRep) {
    btnCancelEditRep.addEventListener("click", resetReplacementForm);
  }
  if (repFilterInput) {
    repFilterInput.addEventListener("input", renderReplacementsModalList);
  }
  if (btnModalApplyAllToMeeting) {
    btnModalApplyAllToMeeting.addEventListener("click", () => {
      applyAllDetectedReplacements();
      closeReplacementsModal();
    });
  }
}

