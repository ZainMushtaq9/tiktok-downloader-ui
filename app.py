import streamlit as st
import requests

# =========================
# CONFIG
# =========================

BACKEND = "https://tiktok-downloader-backend-production-ce2b.up.railway.app"
CHUNK_SIZE = 20

st.set_page_config(page_title="TikTok Profile Downloader", layout="centered")
st.title("TikTok Profile Downloader")
st.caption("Scrape videos incrementally, select & download")

# =========================
# SESSION STATE
# =========================

def init_state():
    defaults = {
        "profile_url": "",
        "videos": [],
        "offset": 0,
        "done": False,
        "selected": set(),
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
    placeholder="https://www.tiktok.com/@username"
)

quality = st.selectbox("Video Quality", ["best", "720p", "480p"])

# =========================
# RESET IF PROFILE CHANGED
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

def fetch_next():
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
        new_videos = data["videos"]

        if not new_videos:
            st.session_state.done = True
            return

        start_index = len(st.session_state.videos)
        st.session_state.videos.extend(new_videos)
        st.session_state.offset = data["offset"]

        # auto-select newly added videos if Select All was active
        if len(st.session_state.selected) == start_index:
            for i in range(start_index, len(st.session_state.videos)):
                st.session_state.selected.add(i)

    except Exception:
        st.session_state.error = "Connection error"

# =========================
# CONTROLS
# =========================

c1, c2 = st.columns(2)

with c1:
    if st.button("Fetch Next Videos", disabled=st.session_state.done):
        if not st.session_state.profile_url:
            st.warning("Enter profile URL")
        else:
            fetch_next()

with c2:
    if st.button("Fetch All Automatically", disabled=st.session_state.done):
        if not st.session_state.profile_url:
            st.warning("Enter profile URL")
        else:
            with st.spinner("Fetching all videos incrementally…"):
                while not st.session_state.done:
                    fetch_next()

# =========================
# STATUS
# =========================

st.divider()
st.write(f"Videos loaded: **{len(st.session_state.videos)}**")

if st.session_state.done:
    st.success("All videos scraped")

if st.session_state.error:
    st.error(st.session_state.error)

# =========================
# SELECT CONTROLS
# =========================

if st.session_state.videos:
    sc1, sc2 = st.columns(2)

    with sc1:
        if st.button("Select All"):
            st.session_state.selected = set(range(len(st.session_state.videos)))

    with sc2:
        if st.button("Unselect All"):
            st.session_state.selected.clear()

# =========================
# VIDEO LIST (SHOW AS THEY COME)
# =========================

for idx, url in enumerate(st.session_state.videos):
    st.divider()

    checked = idx in st.session_state.selected
    if st.checkbox(f"Video {idx + 1}", value=checked, key=f"chk_{idx}"):
        st.session_state.selected.add(idx)
    else:
        st.session_state.selected.discard(idx)

    st.caption(url)

# =========================
# DOWNLOAD SELECTED (ONCE)
# =========================

if st.session_state.selected:
    st.divider()
    st.subheader(f"Download {len(st.session_state.selected)} selected videos")

    if st.button("Download Selected Videos"):
        urls = [st.session_state.videos[i] for i in sorted(st.session_state.selected)]

        with st.spinner("Preparing download…"):
            r = requests.post(
                f"{BACKEND}/zip",
                json={"urls": urls, "quality": quality},
                timeout=900
            )

        if r.status_code == 200:
            st.download_button(
                "Save ZIP file",
                r.content,
                file_name="selected_videos.zip",
                mime="application/zip"
            )
        else:
            st.error("Download failed")
