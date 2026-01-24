/* ======================================================
   CONFIG
====================================================== */

const BACKEND_URL =
  "https://tiktok-downloader-backend-production-ce2b.up.railway.app";

const DOWNLOAD_DELAY_MS = 1000; // safe delay between downloads

/* ======================================================
   DOM ELEMENTS (DEFENSIVE)
====================================================== */

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

/* ======================================================
   STATE
====================================================== */

let currentProfile = "";
let videos = [];

/* ======================================================
   UTILITIES
====================================================== */

// Strip tracking params from TikTok URLs
function normalizeUrl(raw) {
  try {
    const u = new URL(raw.trim());
    return `${u.origin}${u.pathname}`;
  } catch {
    return raw.trim();
  }
}

function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

/* ======================================================
   UI HELPERS
====================================================== */

function resetUI() {
  if (statusDiv) statusDiv.textContent = "";
  if (videoList) videoList.innerHTML = "";
  if (progressWrapper) progressWrapper.classList.add("hidden");
  updateProgress(0);
  if (downloadAllBtn) downloadAllBtn.classList.add("hidden");
  videos = [];
}

function updateProgress(percent) {
  if (!progressFill) return;
  progressFill.style.width = percent + "%";
  progressFill.textContent = percent + "%";
}

function showProgress() {
  if (progressWrapper) progressWrapper.classList.remove("hidden");
}

/* ======================================================
   MODE SWITCHING
====================================================== */

if (modeRadios.length) {
  modeRadios.forEach(radio => {
    radio.addEventListener("change", () => {
      if (radio.value === "single") {
        profileMode?.classList.add("hidden");
        singleMode?.classList.remove("hidden");
      } else {
        singleMode?.classList.add("hidden");
        profileMode?.classList.remove("hidden");
      }
      resetUI();
    });
  });
}

/* ======================================================
   SKELETON LOADER
====================================================== */

function showSkeletons(count = 5) {
  if (!videoList) return;
  videoList.innerHTML = "";
  for (let i = 0; i < count; i++) {
    const sk = document.createElement("div");
    sk.className = "video-card";
    sk.innerHTML = `
      <div class="skeleton" style="width:88px;height:88px;border-radius:8px;"></div>
      <div style="flex:1">
        <div class="skeleton" style="height:12px;width:70%;margin-bottom:8px;"></div>
        <div class="skeleton" style="height:10px;width:40%;"></div>
      </div>
    `;
    videoList.appendChild(sk);
  }
}

/* ======================================================
   FETCH PROFILE VIDEOS
====================================================== */

fetchBtn?.addEventListener("click", async () => {
  if (!profileUrlInput || !statusDiv) return;

  const rawUrl = profileUrlInput.value;
  if (!rawUrl) {
    statusDiv.textContent = "Please enter a TikTok profile URL.";
    return;
  }

  const profileUrl = normalizeUrl(rawUrl);

  resetUI();
  statusDiv.textContent = "Fetching profile videos…";
  showProgress();
  updateProgress(10);
  showSkeletons(6);

  try {
    const res = await fetch(
      `${BACKEND_URL}/profile?profile_url=${encodeURIComponent(profileUrl)}`
    );

    const data = await res.json();

    if (!res.ok || data.detail) {
      throw new Error(data.detail || "Profile fetch failed");
    }

    currentProfile = data.profile || "tiktok_profile";

    const limit = limitSelect?.value || "all";
    videos =
      limit === "all"
        ? data.videos
        : data.videos.slice(0, parseInt(limit, 10));

    updateProgress(100);
    statusDiv.textContent = `${videos.length} videos found on this profile.`;

    renderVideoList(videos);
    downloadAllBtn?.classList.remove("hidden");

  } catch (err) {
    console.error(err);
    updateProgress(0);
    statusDiv.textContent =
      err.message ||
      "Failed to fetch profile. The profile may be private or temporarily unavailable.";
  }
});

/* ======================================================
   RENDER VIDEO LIST
====================================================== */

function renderVideoList(list) {
  if (!videoList) return;
  videoList.innerHTML = "";

  list.forEach(video => {
    const card = document.createElement("div");
    card.className = "video-card";

    card.innerHTML = `
      ${video.thumbnail ? `<img src="${video.thumbnail}" alt="Video thumbnail" loading="lazy" />` : ""}
      <div>
        <p>Video ${video.index}</p>
        <button>Download</button>
      </div>
    `;

    const btn = card.querySelector("button");
    btn.addEventListener("click", () => downloadSingle(video));

    videoList.appendChild(card);
  });
}

/* ======================================================
   SINGLE VIDEO DOWNLOAD (FROM LIST)
====================================================== */

function downloadSingle(video) {
  if (!statusDiv) return;

  statusDiv.textContent =
    "Your browser may ask permission to download the file.";

  const url =
    `${BACKEND_URL}/download` +
    `?url=${encodeURIComponent(video.url)}` +
    `&index=${video.index}` +
    `&profile=${encodeURIComponent(currentProfile)}` +
    `&quality=best`;

  triggerDownload(url);
}

/* ======================================================
   DOWNLOAD ALL (SEQUENTIAL QUEUE)
====================================================== */

downloadAllBtn?.addEventListener("click", async () => {
  if (!videos.length || !statusDiv) return;

  statusDiv.textContent =
    "Starting downloads… Please allow multiple downloads when prompted.";
  showProgress();

  for (let i = 0; i < videos.length; i++) {
    const percent = Math.round(((i + 1) / videos.length) * 100);
    updateProgress(percent);

    const video = videos[i];
    statusDiv.textContent =
      `Downloading ${i + 1} of ${videos.length}`;

    const url =
      `${BACKEND_URL}/download` +
      `?url=${encodeURIComponent(video.url)}` +
      `&index=${video.index}` +
      `&profile=${encodeURIComponent(currentProfile)}` +
      `&quality=best`;

    triggerDownload(url);
    await sleep(DOWNLOAD_DELAY_MS);
  }

  statusDiv.textContent =
    "All downloads have been triggered successfully.";
});

/* ======================================================
   SINGLE VIDEO MODE
====================================================== */

singleDownloadBtn?.addEventListener("click", () => {
  if (!singleVideoInput || !statusDiv) return;

  const raw = singleVideoInput.value;
  if (!raw) {
    statusDiv.textContent = "Please paste a TikTok video link.";
    return;
  }

  const cleanUrl = normalizeUrl(raw);

  statusDiv.textContent =
    "Your browser may ask permission to download the file.";

  const downloadUrl =
    `${BACKEND_URL}/download` +
    `?url=${encodeURIComponent(cleanUrl)}` +
    `&index=1` +
    `&profile=single_video` +
    `&quality=best`;

  triggerDownload(downloadUrl);
});

/* ======================================================
   SAFE DOWNLOAD TRIGGER
====================================================== */

function triggerDownload(url) {
  const a = document.createElement("a");
  a.href = url;
  a.download = "";
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
}

/* ======================================================
   COOKIE CONSENT
====================================================== */

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
