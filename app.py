import streamlit as st
import requests

# =========================
# CONFIG
# =========================

BACKEND = "https://tiktok-downloader-backend-production-ce2b.up.railway.app"
VIDEOS_PER_PAGE = {st.session_state.total_videos}

st.set_page_config(page_title="TikTok Downloader", layout="centered")
st.title("TikTok Profile & Video Downloader")

# =========================
# SESSION STATE
# =========================

if "videos" not in st.session_state:
    st.session_state.videos = []

if "selected" not in st.session_state:
    st.session_state.selected = set()

if "offset" not in st.session_state:
    st.session_state.offset = 0

if "page" not in st.session_state:
    st.session_state.page = 0

if "total_videos" not in st.session_state:
    st.session_state.total_videos = None

if "profile_url" not in st.session_state:
    st.session_state.profile_url = ""

# =========================
# INPUT
# =========================

profile_url = st.text_input(
    "TikTok Profile URL",
    placeholder="https://www.tiktok.com/@username"
)

quality = st.selectbox(
    "Video Quality",
    ["best", "720p", "480p"]
)

# =========================
# PROFILE COUNT
# =========================

if profile_url and st.button("Check total videos on profile"):
    with st.spinner("Checking profile…"):
        r = requests.post(
            f"{BACKEND}/profile_count",
            json={"profile_url": profile_url},
            timeout=120
        )

    if r.status_code == 200:
        st.session_state.total_videos = r.json()["total_videos"]
        st.session_state.profile_url = profile_url
        st.success(f"Total videos on this profile: {st.session_state.total_videos}")
    else:
        st.error("Failed to fetch profile video count")

# =========================
# SCRAPE / RESUME
# =========================

if st.button("Load / Resume Scraping"):
    if not profile_url:
        st.warning("Please enter a profile URL")
    else:
        with st.spinner("Scraping videos…"):
            r = requests.post(
                f"{BACKEND}/profile",
                json={
                    "profile_url": profile_url,
                    "offset": st.session_state.offset,
                    "limit": 10,
                    "sleep_seconds": 3
                },
                timeout=120
            )

        if r.status_code == 200:
            data = r.json()
            st.session_state.videos.extend(data["videos"])
            st.session_state.offset = data["offset"]
        else:
            st.error("Profile scraping failed")

# =========================
# PROGRESS
# =========================

if st.session_state.total_videos:
    progress = min(
        len(st.session_state.videos) / st.session_state.total_videos,
        1.0
    )
    st.progress(progress)
    st.caption(
        f"Scraped {len(st.session_state.videos)} / {st.session_state.total_videos} videos"
    )
else:
    st.caption(f"Scraped videos: {len(st.session_state.videos)}")

# =========================
# SELECT CONTROLS
# =========================

if st.session_state.videos:
    c1, c2 = st.columns(2)
    with c1:
        if st.button("Select All"):
            st.session_state.selected = set(range(len(st.session_state.videos)))
    with c2:
        if st.button("Unselect All"):
            st.session_state.selected.clear()

# =========================
# PAGINATION VIEW (5 ONLY)
# =========================

start = st.session_state.page * VIDEOS_PER_PAGE
end = start + VIDEOS_PER_PAGE
visible = st.session_state.videos[start:end]

st.divider()
st.subheader(
    f"Showing videos {start + 1} – {min(end, len(st.session_state.videos))}"
)

# =========================
# VIDEO LIST
# =========================

for idx, url in enumerate(visible, start=start):
    st.divider()

    checked = idx in st.session_state.selected
    if st.checkbox(f"Video {idx + 1}", checked, key=f"chk_{idx}"):
        st.session_state.selected.add(idx)
    else:
        st.session_state.selected.discard(idx)

    st.caption(url)

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Play", key=f"play_{idx}"):
            r = requests.post(
                f"{BACKEND}/resolve",
                json={"url": url, "quality": quality},
                timeout=300
            )
            if r.status_code == 200:
                st.video(r.content)
            else:
                st.error("Preview failed")

    with col2:
        if st.button("Download", key=f"dl_{idx}"):
            r = requests.post(
                f"{BACKEND}/resolve",
                json={"url": url, "quality": quality},
                timeout=300
            )
            if r.status_code == 200:
                st.download_button(
                    "Save file",
                    r.content,
                    file_name=f"video_{idx + 1}.mp4",
                    mime="video/mp4",
                    key=f"save_{idx}"
                )

# =========================
# PAGE CONTROLS
# =========================

p1, p2 = st.columns(2)

with p1:
    if st.button("⬅ Previous") and st.session_state.page > 0:
        st.session_state.page -= 1

with p2:
    if st.button("Next ➡") and end < len(st.session_state.videos):
        st.session_state.page += 1

# =========================
# ZIP DOWNLOAD
# =========================

if st.session_state.selected:
    st.divider()
    st.subheader(f"Download {len(st.session_state.selected)} selected videos")

    if st.button("Download Selected as ZIP"):
        urls = [st.session_state.videos[i] for i in sorted(st.session_state.selected)]

        r = requests.post(
            f"{BACKEND}/zip",
            json={"urls": urls, "quality": quality},
            timeout=600
        )

        if r.status_code == 200:
            st.download_button(
                "Save ZIP",
                r.content,
                file_name="videos.zip",
                mime="application/zip"
            )
        else:
            st.error("ZIP download failed")
