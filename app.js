const BACKEND_URL =
  "https://tiktok-downloader-backend-production-ce2b.up.railway.app";

/* =========================
   ELEMENTS
========================= */

const fetchBtn = document.getElementById("fetchBtn");
const downloadAllBtn = document.getElementById("downloadAllBtn");
const singleDownloadBtn = document.getElementById("singleDownloadBtn");

const statusDiv = document.getElementById("status");
const videoList = document.getElementById("videoList");

const progressWrapper = document.getElementById("progressWrapper");
const progressFill = document.getElementById("progressFill");

const profileMode = document.getElementById("profileMode");
const singleMode = document.getElementById("singleMode");

/* =========================
   MODE SWITCH (RADIO)
========================= */

document.querySelectorAll('input[name="mode"]').forEach((radio) => {
  radio.addEventListener("change", () => {
    if (radio.value === "profile") {
      profileMode.classList.remove("hidden");
      singleMode.classList.add("hidden");
    } else {
      singleMode.classList.remove("hidden");
      profileMode.classList.add("hidden");
    }
  });
});

/* =========================
   GLOBAL STATE
========================= */

let currentProfile = null;

/* =========================
   SINGLE VIDEO DOWNLOAD
========================= */

singleDownloadBtn.onclick = () => {
  const url = document.getElementById("singleVideoUrl").value.trim();
  if (!url) {
    alert("Please paste a TikTok video link");
    return;
  }

  const a = document.createElement("a");
  a.href =
    `${BACKEND_URL}/download` +
    `?url=${encodeURIComponent(url)}` +
    `&index=1&profile=single&quality=best`;
  a.click();
};

/* =========================
   FETCH PROFILE
========================= */

fetchBtn.onclick = async () => {
  const profileUrl = document.getElementById("profileUrl").value.trim();
  if (!profileUrl) {
    statusDiv.innerText = "Please enter a profile URL";
    return;
  }

  statusDiv.innerText = "Fetching profile…";
  videoList.innerHTML = "";

  progressWrapper.style.display = "block";
  progressFill.style.width = "0%";
  progressFill.innerText = "0%";

  try {
    const res = await fetch(
      `${BACKEND_URL}/profile?profile_url=${encodeURIComponent(profileUrl)}`
    );

    if (!res.ok) throw new Error("Request failed");

    const data = await res.json();
    currentProfile = data;

    let videos = data.videos || [];

    // Apply limit selector
    const limitValue = document.getElementById("limitSelect").value;
    if (limitValue !== "all") {
      videos = videos.slice(0, parseInt(limitValue));
    }

    const total = videos.length;
    statusDiv.innerText = `${total} videos found`;

    let loaded = 0;

    for (const v of videos) {
      const card = document.createElement("div");
      card.className = "video-card";

      card.innerHTML = `
        ${v.thumbnail ? `<img src="${v.thumbnail}" />` : ""}
        <div>
          <p><strong>Video ${v.index}</strong></p>
          <button onclick="downloadOne('${encodeURIComponent(v.url)}', ${v.index}, '${data.profile}')">
            Download ${v.index}.mp4
          </button>
        </div>
      `;

      videoList.appendChild(card);

      loaded++;
      const percent = Math.round((loaded / total) * 100);
      progressFill.style.width = percent + "%";
      progressFill.innerText = percent + "%";

      // small UI delay (not backend)
      await new Promise((r) => setTimeout(r, 10));
    }

    statusDiv.innerText = "Videos ready";

  } catch (e) {
    console.error(e);
    statusDiv.innerText = "Failed to fetch profile";
    progressWrapper.style.display = "none";
  }
};

/* =========================
   DOWNLOAD ONE VIDEO
========================= */

function downloadOne(url, index, profile) {
  const a = document.createElement("a");
  a.href =
    `${BACKEND_URL}/download` +
    `?url=${url}` +
    `&index=${index}` +
    `&profile=${profile}` +
    `&quality=best`;
  a.click();
}

/* =========================
   DOWNLOAD ALL (SEQUENTIAL)
========================= */

downloadAllBtn.onclick = async () => {
  if (!currentProfile) {
    alert("Fetch profile first");
    return;
  }

  let videos = currentProfile.videos || [];

  // Respect limit selector
  const limitValue = document.getElementById("limitSelect").value;
  if (limitValue !== "all") {
    videos = videos.slice(0, parseInt(limitValue));
  }

  statusDiv.innerText = "Starting download queue…";

  for (let i = 0; i < videos.length; i++) {
    const v = videos[i];

    statusDiv.innerText = `Downloading ${i + 1} / ${videos.length}`;

    const a = document.createElement("a");
    a.href =
      `${BACKEND_URL}/download` +
      `?url=${encodeURIComponent(v.url)}` +
      `&index=${v.index}` +
      `&profile=${currentProfile.profile}` +
      `&quality=best`;
    a.click();

    // 1 SECOND DELAY (anti-block)
    await new Promise((r) => setTimeout(r, 1000));
  }

  statusDiv.innerText = "All downloads triggered";
};
