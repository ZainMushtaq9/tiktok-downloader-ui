/* ======================================================
   GLOBAL CONFIG
====================================================== */

const BACKEND_URL =
  "https://tiktok-downloader-backend-production-ce2b.up.railway.app";

const DOWNLOAD_DELAY_MS = 1000; // 1s delay between downloads

/* ======================================================
   DOM READY (CRITICAL FIX)
====================================================== */

document.addEventListener("DOMContentLoaded", () => {

  /* ======================================================
     DOM ELEMENTS (SAFE SELECT)
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
     MODE SWITCHING (PROFILE / SINGLE)
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
     UI HELPERS
  ====================================================== */

  function resetUI() {
    if (statusDiv) statusDiv.textContent = "";
    if (videoList) videoList.innerHTML = "";
    if (progressWrapper) progressWrapper.classList.add("hidden");
    updateProgress(0);
    downloadAllBtn?.classList.add("hidden");
    videos = [];
  }

  function updateProgress(percent) {
    if (!progressFill) return;
    progressFill.style.width = percent + "%";
    progressFill.textContent = percent + "%";
  }

  function showProgress() {
    progressWrapper?.classList.remove("hidden");
  }

  function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
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
     FETCH PROFILE (TIKTOK)
  ====================================================== */

  fetchBtn?.addEventListener("click", async () => {
    const profileUrl = profileUrlInput?.value.trim();
    if (!profileUrl) {
      statusDiv.textContent = "Please enter a profile URL.";
      return;
    }

    resetUI();
    statusDiv.textContent = "Fetching videos…";
    showProgress();
    updateProgress(10);
    showSkeletons(6);

    try {
      const res = await fetch(
        `${BACKEND_URL}/profile?profile_url=${encodeURIComponent(profileUrl)}`
      );

      if (!res.ok) throw new Error("FETCH_FAILED");

      const data = await res.json();
      currentProfile = data.profile || "profile";

      const limit = limitSelect?.value || "all";
      videos =
        limit === "all"
          ? data.videos
          : data.videos.slice(0, parseInt(limit));

      updateProgress(100);
      statusDiv.textContent = `${videos.length} videos found.`;
      renderVideoList(videos);
      downloadAllBtn?.classList.remove("hidden");

    } catch (err) {
      console.error(err);
      statusDiv.textContent =
        "Failed to fetch profile. It may be private or blocked.";
      updateProgress(0);
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
        ${video.thumbnail ? `<img src="${video.thumbnail}" loading="lazy" />` : ""}
        <div>
          <p>Video ${video.index}</p>
          <button>Download</button>
        </div>
      `;

      card.querySelector("button").addEventListener("click", () => {
        downloadSingle(video);
      });

      videoList.appendChild(card);
    });
  }

  /* ======================================================
     SINGLE VIDEO DOWNLOAD
  ====================================================== */

  function downloadSingle(video) {
    statusDiv.textContent =
      "Your browser may ask permission to download the file.";

    const url =
      `${BACKEND_URL}/download` +
      `?url=${encodeURIComponent(video.url)}` +
      `&index=${video.index}` +
      `&profile=${currentProfile}` +
      `&quality=best`;

    triggerDownload(url);
  }

  /* ======================================================
     DOWNLOAD ALL (SEQUENTIAL QUEUE)
  ====================================================== */

  downloadAllBtn?.addEventListener("click", async () => {
    if (!videos.length) return;

    statusDiv.textContent =
      "Starting downloads… Please allow multiple downloads.";
    showProgress();

    for (let i = 0; i < videos.length; i++) {
      updateProgress(Math.round(((i + 1) / videos.length) * 100));

      const video = videos[i];
      const url =
        `${BACKEND_URL}/download` +
        `?url=${encodeURIComponent(video.url)}` +
        `&index=${video.index}` +
        `&profile=${currentProfile}` +
        `&quality=best`;

      triggerDownload(url);
      await sleep(DOWNLOAD_DELAY_MS);
    }

    statusDiv.textContent = "All downloads started.";
  });

  /* ======================================================
     SINGLE VIDEO MODE
  ====================================================== */

  singleDownloadBtn?.addEventListener("click", () => {
    const url = singleVideoInput?.value.trim();
    if (!url) {
      statusDiv.textContent = "Please paste a video link.";
      return;
    }

    const downloadUrl =
      `${BACKEND_URL}/download` +
      `?url=${encodeURIComponent(url)}` +
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

    acceptCookies.addEventListener("click", () => {
      localStorage.setItem("cookiesAccepted", "yes");
      cookieBanner.style.display = "none";
    });
  }

});
