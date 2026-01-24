const BACKEND =
  "https://tiktok-downloader-backend-production-ce2b.up.railway.app";

const analyzeBtn = document.getElementById("analyzeBtn");
const youtubeUrlInput = document.getElementById("youtubeUrl");
const videoList = document.getElementById("videoList");
const statusDiv = document.getElementById("status");
const progressWrapper = document.getElementById("progressWrapper");
const progressFill = document.getElementById("progressFill");
const downloadAllBtn = document.getElementById("downloadAllBtn");
const downloadControls = document.getElementById("downloadControls");
const limitSelect = document.getElementById("limitSelect");

let videos = [];

/* =========================
   ANALYZE LINK
========================= */

analyzeBtn.addEventListener("click", async () => {
  const url = youtubeUrlInput.value.trim();
  if (!url) {
    statusDiv.textContent = "Please paste a YouTube video or playlist link.";
    return;
  }

  statusDiv.textContent = "Analyzing link...";
  videoList.innerHTML = "";
  videos = [];
  downloadControls.classList.add("hidden");
  progressWrapper.classList.add("hidden");

  try {
    const infoRes = await fetch(
      `${BACKEND}/youtube/info?url=${encodeURIComponent(url)}`
    );

    if (!infoRes.ok) throw new Error();

    const info = await infoRes.json();

    // SINGLE VIDEO
    if (info.type === "single") {
      videos = [{
        index: 1,
        url: url,
        title: info.title,
        thumbnail: info.thumbnail
      }];

      renderVideos();
      statusDiv.textContent = "1 video ready for download.";
      downloadControls.classList.remove("hidden");
    }

    // PLAYLIST
    if (info.type === "playlist") {
      statusDiv.textContent = "Fetching playlist videos...";

      const listRes = await fetch(
        `${BACKEND}/youtube/playlist?url=${encodeURIComponent(url)}`
      );

      if (!listRes.ok) throw new Error();

      const listData = await listRes.json();
      videos = listData.videos;

      const limit = limitSelect.value;
      if (limit !== "all") {
        videos = videos.slice(0, parseInt(limit));
      }

      renderVideos();
      statusDiv.textContent = `${videos.length} videos ready for download.`;
      downloadControls.classList.remove("hidden");
    }

  } catch (e) {
    statusDiv.textContent =
      "Failed to analyze link. The video or playlist may be private or unavailable.";
  }
});

/* =========================
   RENDER VIDEO LIST
========================= */

function renderVideos() {
  videoList.innerHTML = "";

  videos.forEach((video, idx) => {
    const card = document.createElement("div");
    card.className = "video-card";

    card.innerHTML = `
      ${video.thumbnail ? `<img src="${video.thumbnail}" loading="lazy" alt="Video thumbnail">` : ""}
      <div>
        <p>${video.title || "YouTube Video"}</p>
        <button>Download</button>
      </div>
    `;

    card.querySelector("button").addEventListener("click", () => {
      triggerDownload(video, idx + 1);
    });

    videoList.appendChild(card);
  });
}

/* =========================
   DOWNLOAD ALL (SEQUENTIAL)
========================= */

downloadAllBtn.addEventListener("click", async () => {
  if (!videos.length) return;

  progressWrapper.classList.remove("hidden");

  for (let i = 0; i < videos.length; i++) {
    const percent = Math.round(((i + 1) / videos.length) * 100);
    progressFill.style.width = percent + "%";
    progressFill.textContent = percent + "%";

    triggerDownload(videos[i], i + 1);

    // safe delay
    await new Promise(r => setTimeout(r, 1200));
  }

  statusDiv.textContent = "All downloads have been triggered.";
});

/* =========================
   TRIGGER DOWNLOAD
========================= */

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
}
