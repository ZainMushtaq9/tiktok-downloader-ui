const BACKEND_URL =
  "https://tiktok-downloader-backend-production-ce2b.up.railway.app";

const fetchBtn = document.getElementById("fetchBtn");
const statusDiv = document.getElementById("status");
const videoList = document.getElementById("videoList");

const progressWrapper = document.getElementById("progressWrapper");
const progressFill = document.getElementById("progressFill");

fetchBtn.onclick = async () => {
  const profileUrl = document.getElementById("profileUrl").value.trim();

  if (!profileUrl) {
    statusDiv.innerText = "Please enter a TikTok profile URL";
    return;
  }

  // Reset UI
  statusDiv.innerText = "Fetching profile…";
  videoList.innerHTML = "";
  progressWrapper.style.display = "block";
  progressFill.style.width = "0%";
  progressFill.innerText = "0%";

  try {
    const response = await fetch(
      `${BACKEND_URL}/profile?profile_url=${encodeURIComponent(profileUrl)}`
    );

    if (!response.ok) throw new Error("Request failed");

    const data = await response.json();

    const videos = data.videos || [];
    const total = videos.length;

    if (total === 0) {
      statusDiv.innerText = "No videos found";
      progressWrapper.style.display = "none";
      return;
    }

    statusDiv.innerText = `${total} videos found`;

    let loaded = 0;

    for (const video of videos) {
      const card = document.createElement("div");
      card.className = "video-card";

      card.innerHTML = `
        ${video.thumbnail ? `<img src="${video.thumbnail}" />` : ""}
        <p><strong>Video ${video.index}</strong></p>
        <button onclick="downloadVideo(
          '${encodeURIComponent(video.url)}',
          ${video.index},
          '${data.profile}'
        )">
          Download ${video.index}.mp4
        </button>
      `;

      videoList.appendChild(card);

      // Update progress bar
      loaded++;
      const percent = Math.round((loaded / total) * 100);
      progressFill.style.width = percent + "%";
      progressFill.innerText = percent + "%";

      // Tiny delay for smooth UI (NOT backend delay)
      await new Promise((r) => setTimeout(r, 12));
    }

    statusDiv.innerText = "All videos loaded";
  } catch (err) {
    console.error(err);
    statusDiv.innerText = "Failed to fetch profile";
    progressWrapper.style.display = "none";
  }
};

// =========================
// DOWNLOAD FUNCTION
// =========================

function downloadVideo(url, index, profile) {
  const quality = "best";

  const downloadUrl =
    `${BACKEND_URL}/download` +
    `?url=${url}` +
    `&index=${index}` +
    `&profile=${profile}` +
    `&quality=${quality}`;

  const a = document.createElement("a");
  a.href = downloadUrl;
  a.download = "";
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
}
