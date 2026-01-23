const BACKEND_URL = "https://tiktok-downloader-backend-production-ce2b.up.railway.app";

const fetchBtn = document.getElementById("fetchBtn");
const statusDiv = document.getElementById("status");
const videoList = document.getElementById("videoList");

fetchBtn.onclick = async () => {
  const profileUrl = document.getElementById("profileUrl").value.trim();
  if (!profileUrl) return;

  statusDiv.innerText = "Fetching videos...";
  videoList.innerHTML = "";

  try {
    const res = await fetch(
      `${BACKEND_URL}/profile?profile_url=${encodeURIComponent(profileUrl)}`
    );
    const data = await res.json();

    statusDiv.innerText = `${data.total} videos found`;

    data.videos.forEach(v => {
      const card = document.createElement("div");
      card.className = "video-card";

      card.innerHTML = `
        ${v.thumbnail ? `<img src="${v.thumbnail}" />` : ""}
        <p>Video ${v.index}</p>
        <button onclick="downloadVideo('${v.url}', ${v.index}, '${data.profile}')">
          Download ${v.index}.mp4
        </button>
      `;

      videoList.appendChild(card);
    });

  } catch (err) {
    statusDiv.innerText = "Failed to fetch profile";
  }
};

function downloadVideo(url, index, profile) {
  const a = document.createElement("a");
  a.href =
    `${BACKEND_URL}/download` +
    `?url=${encodeURIComponent(url)}` +
    `&index=${index}` +
    `&profile=${profile}` +
    `&quality=best`;
  a.click();
}
