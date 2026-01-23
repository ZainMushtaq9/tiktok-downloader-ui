/* =========================
   CONFIG
========================= */

const BACKEND_URL =
  "https://tiktok-downloader-backend-production-ce2b.up.railway.app";

const DOWNLOAD_DELAY_MS = 1000; // 1 second anti-block delay

/* =========================
   DOM ELEMENTS
========================= */

const profileUrlInput = document.getElementById("profileUrl");
const singleVideoInput = document.getElementById("singleVideoUrl");

const fetchBtn = document.getElementById("fetchBtn");
const singleDownloadBtn = document.getElementById("singleDownloadBtn");

const statusDiv = document.getElementById("status");
const videoList = document.getElementById("videoList");

const progressWrapper = document.getElementById("progressWrapper");
const progressFill = document.getElementById("progressFill");

const downloadAllBtn = document.getElementById("downloadAllBtn");
const limitSelect = document.getElementById("limitSelect");

const modeRadios = document.querySelectorAll("input[name='mode']");
const profileMode = document.getElementById("profileMode");
const singleMode = document.getElementById("singleMode");

/* =========================
   STATE
========================= */

let currentProfile = null;
let videos = [];
let selectedIndexes = new Set();

/* =========================
   MODE SWITCH
========================= */

modeRadios.forEach(radio => {
  radio.addEventListener("change", () => {
    if (radio.value === "single") {
      profileMode.classList.add("hidden");
      singleMode.classList.remove("hidden");
    } else {
      singleMode.classList.add("hidden");
      profileMode.classList.remove("hidden");
    }

    resetUI();
  });
});

/* =========================
   HELPERS
========================= */

function resetUI() {
  statusDiv.textContent = "";
  videoList.innerHTML = "";
  progressWrapper.classList.add("hidden");
  progressFill.style.width = "0%";
  progressFill.textContent = "0%";
  downloadAllBtn.classList.add("hidden");
  videos = [];
  selectedIndexes.clear();
}

function updateProgress(percent) {
  progressWrapper.classList.remove("hidden");
  progressFill.style.width = percent + "%";
  progressFill.textContent = percent + "%";
}

function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

/* =========================
   FETCH PROFILE
========================= */

fetchBtn?.addEventListener("click", async () => {
  const profileUrl = profileUrlInput.value.trim();
  if (!profileUrl) {
    statusDiv.textContent = "Please enter a TikTok profile URL.";
    return;
  }

  resetUI();
  statusDiv.textContent = "Fetching profile…";
  updateProgress(5);

  try {
    const res = await fetch(
      `${BACKEND_URL}/profile?profile_url=${encodeURIComponent(profileUrl)}`
    );

    if (!res.ok) throw new Error("Profile fetch failed");

    const data = await res.json();
    currentProfile = data.profile;

    let limit = limitSelect.value;
    videos =
      limit === "all"
        ? data.videos
        : data.videos.slice(0, parseInt(limit));

    statusDiv.textContent = `${videos.length} videos found`;
    updateProgress(100);

    renderVideoList(videos);
    downloadAllBtn.classList.remove("hidden");

  } catch (err) {
    statusDiv.textContent = "Failed to fetch profile";
    console.error(err);
  }
});

/* =========================
   RENDER VIDEO LIST
========================= */

function renderVideoList(videos) {
  videoList.innerHTML = "";

  videos.forEach(v => {
    selectedIndexes.add(v.index); // auto-select all

    const card = document.createElement("div");
    card.className = "video-card";

    card.innerHTML = `
      ${v.thumbnail ? `<img src="${v.thumbnail}" alt="Thumbnail" />` : ""}
      <div>
        <p>Video ${v.index}</p>
        <button data-index="${v.index}">Download</button>
      </div>
    `;

    const btn = card.querySelector("button");
    btn.addEventListener("click", () => {
      downloadSingle(v);
    });

    videoList.appendChild(card);
  });
}

/* =========================
   SINGLE VIDEO DOWNLOAD
========================= */

async function downloadSingle(video) {
  const url =
    `${BACKEND_URL}/download` +
    `?url=${encodeURIComponent(video.url)}` +
    `&index=${video.index}` +
    `&profile=${currentProfile}` +
    `&quality=best`;

  const a = document.createElement("a");
  a.href = url;
  a.download = "";
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
}

/* =========================
   DOWNLOAD ALL (SEQUENTIAL)
========================= */

downloadAllBtn?.addEventListener("click", async () => {
  if (!videos.length) return;

  statusDiv.textContent =
    "Downloading videos… Your browser may ask permission once.";

  for (let i = 0; i < videos.length; i++) {
    const v = videos[i];
    const percent = Math.round(((i + 1) / videos.length) * 100);
    updateProgress(percent);

    statusDiv.textContent = `Downloading ${i + 1} / ${videos.length}`;

    const url =
      `${BACKEND_URL}/download` +
      `?url=${encodeURIComponent(v.url)}` +
      `&index=${v.index}` +
      `&profile=${currentProfile}` +
      `&quality=best`;

    const a = document.createElement("a");
    a.href = url;
    a.download = "";
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);

    await sleep(DOWNLOAD_DELAY_MS);
  }

  statusDiv.textContent = "All downloads triggered.";
});

/* =========================
   SINGLE VIDEO MODE
========================= */

singleDownloadBtn?.addEventListener("click", () => {
  const url = singleVideoInput.value.trim();
  if (!url) {
    statusDiv.textContent = "Please paste a TikTok video link.";
    return;
  }

  const a = document.createElement("a");
  a.href =
    `${BACKEND_URL}/download` +
    `?url=${encodeURIComponent(url)}` +
    `&index=1` +
    `&profile=single_video` +
    `&quality=best`;
  a.download = "";
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
});

/* =========================
   COOKIE CONSENT
========================= */

const cookieBanner = document.getElementById("cookieBanner");
const acceptCookies = document.getElementById("acceptCookies");

if (cookieBanner && acceptCookies) {
  if (localStorage.getItem("cookiesAccepted")) {
    cookieBanner.style.display = "none";
  }

  acceptCookies.onclick = () => {
    localStorage.setItem("cookiesAccepted", "yes");
    cookieBanner.style.display = "none";
  };
}
