const BACKEND_URL =
  "https://tiktok-downloader-backend-production-ce2b.up.railway.app";

// =======================
// ELEMENTS
// =======================

const fetchBtn = document.getElementById("fetchBtn");
const downloadAllBtn = document.getElementById("downloadAllBtn");
const singleBtn = document.getElementById("singleDownloadBtn");
const themeToggle = document.getElementById("themeToggle");

const statusDiv = document.getElementById("status");
const videoList = document.getElementById("videoList");

const progressWrapper = document.getElementById("progressWrapper");
const progressFill = document.getElementById("progressFill");

// =======================
// THEME TOGGLE (DARK / LIGHT)
// =======================

const setTheme = (mode) => {
  document.body.classList.toggle("light", mode === "light");
  localStorage.setItem("theme", mode);
  themeToggle.innerText = mode === "light" ? "🌙" : "☀️";
};

themeToggle.onclick = () => {
  const isLight = document.body.classList.contains("light");
  setTheme(isLight ? "dark" : "light");
};

setTheme(localStorage.getItem("theme") || "dark");

// =======================
// SINGLE VIDEO MODE
// =======================

singleBtn.onclick = () => {
  const url = document.getElementById("singleVideoUrl").value.trim();
  if (!url) return alert("Paste a TikTok video link");

  const a = document.createElement("a");
  a.href =
    `${BACKEND_URL}/download` +
    `?url=${encodeURIComponent(url)}` +
    `&index=1&profile=single&quality=best`;
  a.click();
};

// =======================
// FETCH PROFILE
// =======================

let currentProfileData = null;

fetchBtn.onclick = async () => {
  const profileUrl = document.getElementById("profileUrl").value.trim();
  if (!profileUrl) return;

  statusDiv.innerText = "Fetching profile…";
  videoList.innerHTML = "";
  progressWrapper.style.display = "block";
  progressFill.style.width = "0%";
  progressFill.innerText = "0%";

  try {
    const res = await fetch(
      `${BACKEND_URL}/profile?profile_url=${encodeURIComponent(profileUrl)}`
    );
    if (!res.ok) throw new Error();

    const data = await res.json();
    currentProfileData = data;

    statusDiv.innerText = `${data.total} videos found`;

    let loaded = 0;

    for (const v of data.videos) {
      const card = document.createElement("div");
      card.className = "video-card";

      card.innerHTML = `
        ${v.thumbnail ? `<img src="${v.thumbnail}" />` : ""}
        <p>Video ${v.index}</p>
        <button onclick="downloadOne('${encodeURIComponent(v.url)}', ${v.index}, '${data.profile}')">
          Download ${v.index}.mp4
        </button>
      `;

      videoList.appendChild(card);

      loaded++;
      const percent = Math.round((loaded / data.total) * 100);
      progressFill.style.width = percent + "%";
      progressFill.innerText = percent + "%";

      await new Promise(r => setTimeout(r, 10));
    }

    statusDiv.innerText = "Videos ready";
  } catch {
    statusDiv.innerText = "Failed to fetch profile";
    progressWrapper.style.display = "none";
  }
};

// =======================
// DOWNLOAD ONE
// =======================

function downloadOne(url, index, profile) {
  const a = document.createElement("a");
  a.href =
    `${BACKEND_URL}/download` +
    `?url=${url}&index=${index}&profile=${profile}&quality=best`;
  a.click();
}

// =======================
// DOWNLOAD ALL (SEQUENTIAL QUEUE)
// =======================

downloadAllBtn.onclick = async () => {
  if (!currentProfileData) return alert("Fetch profile first");

  const { videos, profile } = currentProfileData;

  statusDiv.innerText = "Starting download queue…";

  for (let i = 0; i < videos.length; i++) {
    const v = videos[i];

    statusDiv.innerText = `Downloading ${i + 1} / ${videos.length}`;

    const a = document.createElement("a");
    a.href =
      `${BACKEND_URL}/download` +
      `?url=${encodeURIComponent(v.url)}` +
      `&index=${v.index}&profile=${profile}&quality=best`;
    a.click();

    // 1 SECOND DELAY (ANTI-BLOCK)
    await new Promise(r => setTimeout(r, 1000));
  }

  statusDiv.innerText = "All downloads triggered";
};
