/* ======================================================
   CONFIG
====================================================== */

const BACKEND_URL =
  "https://tiktok-downloader-backend-production-ce2b.up.railway.app";

const DOWNLOAD_DELAY = 5000; // 5 seconds (anti-block, safe)

/* ======================================================
   DOM ELEMENTS (SAFE QUERY)
====================================================== */

const statusDiv = document.getElementById("status");
const videoList = document.getElementById("videoList");
const progressWrapper = document.getElementById("progressWrapper");
const progressFill = document.getElementById("progressFill");

const fetchBtn = document.getElementById("fetchBtn");
const analyzeBtn = document.getElementById("analyzeBtn");
const downloadAllBtn = document.getElementById("downloadAllBtn");

const profileUrlInput = document.getElementById("profileUrl");
const youtubeUrlInput = document.getElementById("youtubeUrl");
const singleVideoInput = document.getElementById("singleVideoUrl");

const limitSelect = document.getElementById("limitSelect");

/* ======================================================
   STATE
====================================================== */

let currentItems = []; // videos to download
let currentTitle = "video";

/* ======================================================
   HELPERS
====================================================== */

function setStatus(text) {
  if (statusDiv) statusDiv.textContent = text;
}

function showProgress() {
  if (progressWrapper) progressWrapper.classList.remove("hidden");
}

function hideProgress() {
  if (progressWrapper) progressWrapper.classList.add("hidden");
}

function updateProgress(percent) {
  if (!progressFill) return;
  progressFill.style.width = percent + "%";
  progressFill.textContent = percent + "%";
}

function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

function clearUI() {
  if (videoList) videoList.innerHTML = "";
  currentItems = [];
  hideProgress();
  updateProgress(0);
}

/* ======================================================
   COOKIE CONSENT (FIXED)
====================================================== */

const cookieBanner = document.getElementById("cookieBanner");
const acceptCookies = document.getElementById("acceptCookies");

if (cookieBanner && acceptCookies) {
  if (localStorage.getItem("cookiesAccepted") === "yes") {
    cookieBanner.style.display = "none";
  }

  acceptCookies.addEventListener("click", () => {
    localStorage.setItem("cookiesAccepted", "yes");
    cookieBanner.style.display = "none";
  });
}

/* ======================================================
   UNIVERSAL INFO FETCH
====================================================== */

async function fetchInfo(url) {
  setStatus("Analyzing link...");
  showProgress();
  updateProgress(20);

  const res = await fetch(
    `${BACKEND_URL}/info?url=${encodeURIComponent(url)}`
  );

  if (!res.ok) {
    throw new Error("INFO_FAILED");
  }

  const data = await res.json();
  updateProgress(100);
  return data;
}

/* ======================================================
   RENDER LIST (PLAYLIST)
====================================================== */

function renderList(items) {
  if (!videoList) return;

  videoList.innerHTML = "";

  items.forEach(item => {
    const card = document.createElement("div");
    card.className = "video-card";

    card.innerHTML = `
      ${item.thumbnail ? `<img src="${item.thumbnail}" loading="lazy" />` : ""}
      <div>
        <p>${item.title || "Video " + item.index}</p>
        <button>Download</button>
      </div>
    `;

    card.querySelector("button").addEventListener("click", () => {
      triggerDownload(item.url, item.title || "video_" + item.index);
    });

    videoList.appendChild(card);
  });
}

/* ======================================================
   DOWNLOAD TRIGGER (REAL)
====================================================== */

function triggerDownload(url, filename) {
  const link =
    `${BACKEND_URL}/download` +
    `?url=${encodeURIComponent(url)}` +
    `&filename=${encodeURIComponent(filename)}` +
    `&quality=best`;

  const a = document.createElement("a");
  a.href = link;
  a.download = "";
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
}

/* ======================================================
   DOWNLOAD QUEUE (PLAYLIST)
====================================================== */

async function startQueue() {
  if (!currentItems.length) return;

  setStatus("Starting downloads. Allow multiple downloads.");
  showProgress();

  for (let i = 0; i < currentItems.length; i++) {
    const percent = Math.round(((i + 1) / currentItems.length) * 100);
    updateProgress(percent);

    const item = currentItems[i];
    setStatus(`Downloading ${i + 1} of ${currentItems.length}`);

    triggerDownload(item.url, item.title || "video_" + item.index);
    await sleep(DOWNLOAD_DELAY);
  }

  setStatus("All downloads triggered.");
}

/* ======================================================
   TIKTOK / PROFILE PAGE
====================================================== */

if (fetchBtn && profileUrlInput) {
  fetchBtn.addEventListener("click", async () => {
    const url = profileUrlInput.value.trim();
    if (!url) {
      setStatus("Paste a TikTok profile link.");
      return;
    }

    clearUI();

    try {
      const data = await fetchInfo(url);

      if (data.type !== "playlist") {
        setStatus("This link does not contain multiple videos.");
        return;
      }

      currentItems = data.videos;
      renderList(currentItems);
      setStatus(`${currentItems.length} videos ready.`);
      if (downloadAllBtn) downloadAllBtn.classList.remove("hidden");

    } catch {
      setStatus("Failed to fetch profile. It may be private or blocked.");
      hideProgress();
    }
  });
}

/* ======================================================
   YOUTUBE PAGE (SINGLE + PLAYLIST)
====================================================== */

if (analyzeBtn && youtubeUrlInput) {
  analyzeBtn.addEventListener("click", async () => {
    const url = youtubeUrlInput.value.trim();
    if (!url) {
      setStatus("Paste a YouTube link.");
      return;
    }

    clearUI();

    try {
      const data = await fetchInfo(url);

      // SINGLE VIDEO
      if (data.type === "single") {
        setStatus("Single video detected.");
        triggerDownload(data.url, data.title || "youtube_video");
        return;
      }

      // PLAYLIST
      currentTitle = data.title || "playlist";
      currentItems = data.videos;

      const limit = limitSelect ? limitSelect.value : "all";
      if (limit !== "all") {
        currentItems = currentItems.slice(0, parseInt(limit));
      }

      renderList(currentItems);
      setStatus(`${currentItems.length} videos ready from playlist.`);
      if (downloadAllBtn) downloadAllBtn.classList.remove("hidden");

    } catch {
      setStatus("Failed to analyze YouTube link.");
      hideProgress();
    }
  });
}

/* ======================================================
   SINGLE VIDEO MODE (ALL PLATFORMS)
====================================================== */

if (singleVideoInput) {
  const singleBtn = document.getElementById("singleDownloadBtn");
  if (singleBtn) {
    singleBtn.addEventListener("click", () => {
      const url = singleVideoInput.value.trim();
      if (!url) {
        setStatus("Paste a video link.");
        return;
      }

      setStatus("Your download will start.");
      triggerDownload(url, "single_video");
    });
  }
}

/* ======================================================
   DOWNLOAD ALL BUTTON
====================================================== */

if (downloadAllBtn) {
  downloadAllBtn.addEventListener("click", startQueue);
}
