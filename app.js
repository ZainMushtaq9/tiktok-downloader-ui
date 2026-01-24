/* ======================================================
   CONFIG
====================================================== */

const BACKEND =
  "https://tiktok-downloader-backend-production-ce2b.up.railway.app";

const DOWNLOAD_DELAY_MS = 5000; // 5 seconds (safe, anti-block)

/* ======================================================
   DOM ELEMENTS
====================================================== */

const youtubeUrlInput = document.getElementById("youtubeUrl");
const analyzeBtn = document.getElementById("analyzeBtn");

const statusDiv = document.getElementById("status");
const videoList = document.getElementById("videoList");

const downloadControls = document.getElementById("downloadControls");
const downloadAllBtn = document.getElementById("downloadAllBtn");

const progressWrapper = document.getElementById("progressWrapper");
const progressFill = document.getElementById("progressFill");

const limitSelect = document.getElementById("limitSelect");

/* ======================================================
   STATE
====================================================== */

let videos = [];
let currentMode = "single"; // single | playlist

/* ======================================================
   HELPERS
====================================================== */

function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

function resetUI() {
  statusDiv.textContent = "";
  videoList.innerHTML = "";
  downloadControls.classList.add("hidden");
  progressWrapper.classList.add("hidden");
  updateProgress(0);
  videos = [];
}

function updateProgress(percent) {
  progressFill.style.width = percent + "%";
  progressFill.textContent = percent + "%";
}

function showProgress() {
  progressWrapper.classList.remove("hidden");
}

/* ======================================================
   ANALYZE YOUTUBE LINK
====================================================== */

analyzeBtn.addEventListener("click", async () => {
  const url = youtubeUrlInput.value.trim();
  if (!url) {
    statusDiv.textContent = "Please paste a YouTube video or playlist link.";
    return;
  }

  resetUI();
  statusDiv.textContent = "Analyzing link...";

  try {
    const infoRes = await fetch(
      `${BACKEND}/youtube/info?url=${encodeURIComponent(url)}`
    );

    if (!infoRes.ok) {
      throw new Error("ANALYZE_FAILED");
    }

    const info = await infoRes.json();

    // ---------------- SINGLE VIDEO ----------------
    if (info.type === "single") {
      currentMode = "single";

      videos = [
        {
          index: 1,
          url: url,
          title: info.title,
          thumbnail: info.thumbnail
        }
      ];

      renderVideos(videos);
      statusDiv.textContent = "1 video ready for download.";
      downloadControls.classList.remove("hidden");
    }

    // ---------------- PLAYLIST ----------------
    if (info.type === "playlist") {
      currentMode = "playlist";
      statusDiv.textContent = "Fetching playlist videos...";

      const listRes = await fetch(
        `${BACKEND}/youtube/playlist?url=${encodeURIComponent(url)}`
      );

      if (!listRes.ok) {
        throw new Error("PLAYLIST_FAILED");
      }

      const listData = await listRes.json();

      videos = listData.videos;

      // Apply limit (first N)
      const limit = limitSelect.value;
      if (limit !== "all") {
        videos = videos.slice(0, parseInt(limit));
      }

      renderVideos(videos);
      statusDiv.textContent =
        `${videos.length} videos ready. Click “Download All” to start.`;

      downloadControls.classList.remove("hidden");
    }

  } catch (err) {
    console.error(err);
    statusDiv.textContent =
      "Failed to analyze link. Please check the URL or try again later.";
  }
});

/* ======================================================
   RENDER VIDEO LIST (THUMBNAIL PREVIEW ONLY)
====================================================== */

function renderVideos(list) {
  videoList.innerHTML = "";

  list.forEach(video => {
    const card = document.createElement("div");
    card.className = "video-card";

    card.innerHTML = `
      ${video.thumbnail ? `<img src="${video.thumbnail}" loading="lazy" />` : ""}
      <div>
        <p>${video.title || "YouTube Video"}</p>
        <button>Download</button>
      </div>
    `;

    card.querySelector("button").addEventListener("click", () => {
      triggerDownload(video, video.index);
    });

    videoList.appendChild(card);
  });
}

/* ======================================================
   DOWNLOAD ALL (SEQUENTIAL QUEUE WITH DELAY)
====================================================== */

downloadAllBtn.addEventListener("click", async () => {
  if (!videos.length) return;

  statusDiv.textContent =
    "Starting downloads. Please allow multiple downloads when prompted.";
  showProgress();

  for (let i = 0; i < videos.length; i++) {
    const percent = Math.round(((i + 1) / videos.length) * 100);
    updateProgress(percent);

    statusDiv.textContent =
      `Downloading ${i + 1} of ${videos.length}...`;

    triggerDownload(videos[i], i + 1);

    // Delay between downloads (important)
    await sleep(DOWNLOAD_DELAY_MS);
  }

  statusDiv.textContent = "All downloads have been triggered.";
});

/* ======================================================
   DOWNLOAD SINGLE VIDEO
====================================================== */

function triggerDownload(video, index) {
  const a = document.createElement("a");
  a.href =
    `${BACKEND}/download` +
    `?url=${encodeURIComponent(video.url)}` +
    `&index=${index}` +
    `&profile=youtube` +
    `&quality=best`;

  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
}moveChild(a);
}
