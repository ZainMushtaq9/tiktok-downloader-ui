import streamlit as st
import requests

# =========================
# CONFIG
# =========================

BACKEND = "https://tiktok-downloader-backend-production-ce2b.up.railway.app"
CHUNK_SIZE = 20  # how many videos per request

st.set_page_config(
    page_title="TikTok Profile Downloader",
    layout="centered"
)

st.title("TikTok Profile Downloader")
st.caption("Fetch all videos from a TikTok profile (chunked, no timeouts)")

# =========================
# SESSION STATE
# =========================

def init_state():
    defaults = {
        "videos": [],
        "offset": 0,
        "done": False,
        "selected": set(),
        "profile_url": "",
        "error": None
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_state()

# =========================
# INPUT
# =========================

profile_url = st.text_input(
    "TikTok Profile URL",
    value=st.session_state.profile_url,
    placeholder="https://www.tiktok.com/@username"
)

quality = st.selectbox(
    "Video Quality",
    ["best", "720p", "480p"]
)

# =========================
# RESET ON PROFILE CHANGE
# =========================

if profile_url != st.session_state.profile_url:
    st.session_state.profile_url = profile_url
    st.session_state.videos = []
    st.session_state.offset = 0
    st.session_state.done = False
    st.session_state.selected.clear()
    st.session_state.error = None

# =========================
# FETCH NEXT CHUNK
# =========================

def fetch_next_chunk():
    try:
        r = requests.post(
            f"{BACKEND}/profile/chunk",
            json={
                "profile_url": st.session_state.profile_url,
                "offset": st.session_state.offset,
                "limit": CHUNK_SIZE
            },
            timeout=60
        )

        if r.status_code != 200:
            st.session_state.error = "Backend error while scraping"
            return

        data = r.json()
        st.session_state.videos.extend(data["videos"])
        st.session_state.offset = data["offset"]

        if data["count"] == 0:
            st.session_state.done = True

    except requests.exceptions.Timeout:
        st.session_state.error = "Request timed out. Try again."
    except requests.exceptions.ConnectionError:
        st.session_state.error = "Connection lost. Backend may be sleeping."

# =========================
# CONTROLS
# =========================

col1, col2 = st.columns(2)

with col1:
    if st.button("Fetch Next Videos", disabled=st.session_state.done):
        if not st.session_state.profile_url:
            st.warning("Please enter a profile URL")
        else:
            fetch_next_chunk()

with col2:
    if st.button("Fetch ALL Automatically", disabled=st.session_state.done):
        if not st.session_state.profile_url:
            st.warning("Please enter a profile URL")
        else:
            with st.spinner("Fetching all videos in chunks…"):
                while not st.session_state.done:
                    fetch_next_chunk()

# =========================
# STATUS
# =========================

st.divider()
st.write(f"Loaded videos: **{len(st.session_state.videos)}**")

if st.session_state.done:
    st.success("All videos loaded")

if st.session_state.error:
    st.error(st.session_state.error)

# =========================
# SELECT CONTROLS
# =========================

if st.session_state.videos:
    c1, c2 = st.columns(2)
    with c1:
        if st.button("Select ALL"):
            st.session_state.selected = set(range(len(st.session_state.videos)))
    with c2:
        if st.button("Unselect ALL"):
            st.session_state.selected.clear()

# =========================
# VIDEO LIST (NO PAGINATION)
# =========================

for idx, url in enumerate(st.session_state.videos):
    st.divider()

    checked = idx in st.session_state.selected
    if st.checkbox(f"Video {idx + 1}", checked, key=f"chk_{idx}"):
        st.session_state.selected.add(idx)
    else:
        st.session_state.selected.discard(idx)

    st.caption(url)

    col1, col2 = st.columns(2)

    # -------- PREVIEW --------
    with col1:
        if st.button("Play", key=f"play_{idx}"):
            r = requests.post(
                f"{BACKEND}/video",
                json={"url": url, "quality": quality},
                timeout=300
            )
            if r.status_code == 200:
                st.video(r.content)
            else:
                st.error("Preview failed")

    # -------- DOWNLOAD --------
    with col2:
        if st.button("Download", key=f"dl_{idx}"):
            r = requests.post(
                f"{BACKEND}/video",
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
# ZIP DOWNLOAD
# =========================

if st.session_state.selected:
    st.divider()
    st.subheader(f"Download {len(st.session_state.selected)} selected videos")

    if st.button("Download selected as ZIP"):
        urls = [st.session_state.videos[i] for i in sorted(st.session_state.selected)]

        with st.spinner("Preparing ZIP…"):
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
