import streamlit as st
import requests

BACKEND = "https://tiktok-downloader-backend-production-ce2b.up.railway.app"

st.set_page_config(page_title="TikTok Downloader", layout="centered")
st.title("TikTok Video Downloader")

mode = st.radio(
    "Input type",
    ["Multiple Video Links", "Profile Link"],
    horizontal=True
)

input_text = st.text_area(
    "Paste links",
    height=200,
    placeholder="https://www.tiktok.com/@user/video/...\nOR\nhttps://www.tiktok.com/@username"
)

if "videos" not in st.session_state:
    st.session_state.videos = []

if "selected" not in st.session_state:
    st.session_state.selected = set()

# ---------- LOAD ----------

if st.button("Load"):
    st.session_state.videos.clear()
    st.session_state.selected.clear()

    lines = [l.strip() for l in input_text.splitlines() if l.startswith("http")]

    if not lines:
        st.warning("No valid links")
        st.stop()

    if mode == "Profile Link":
        with st.spinner("Scraping profile (limited)…"):
            r = requests.post(
                f"{BACKEND}/profile",
                json={"profile_url": lines[0], "limit": 5},
                timeout=120
            )

        if r.status_code != 200:
            st.error("Profile scrape failed")
            st.stop()

        st.session_state.videos = r.json()["videos"]

    else:
        st.session_state.videos = lines

# ---------- CONTROLS ----------

if st.session_state.videos:
    c1, c2 = st.columns(2)
    with c1:
        if st.button("Select All"):
            st.session_state.selected = set(range(len(st.session_state.videos)))
    with c2:
        if st.button("Unselect All"):
            st.session_state.selected.clear()

# ---------- VIDEO LIST ----------

for i, url in enumerate(st.session_state.videos):
    st.divider()

    checked = i in st.session_state.selected
    if st.checkbox(f"Video {i+1}", checked, key=f"chk_{i}"):
        st.session_state.selected.add(i)
    else:
        st.session_state.selected.discard(i)

    st.caption(url)

    # PREVIEW
    if st.button("Play", key=f"play_{i}"):
        with st.spinner("Loading preview…"):
            r = requests.post(
                f"{BACKEND}/resolve",
                json={"url": url},
                timeout=300
            )
            if r.status_code == 200:
                st.video(r.content)
            else:
                st.error("Preview failed")

    # SINGLE DOWNLOAD
    if st.button("Download", key=f"dl_{i}"):
        with st.spinner("Downloading…"):
            r = requests.post(
                f"{BACKEND}/resolve",
                json={"url": url},
                timeout=300
            )
            if r.status_code == 200:
                st.download_button(
                    "Save file",
                    r.content,
                    file_name=f"video_{i+1}.mp4",
                    mime="video/mp4",
                    key=f"save_{i}"
                )

# ---------- DOWNLOAD SELECTED ----------

if st.session_state.selected:
    st.subheader("Download Selected")
    for i in sorted(st.session_state.selected):
        url = st.session_state.videos[i]
        if st.button(f"Download Selected {i+1}", key=f"bulk_{i}"):
            r = requests.post(
                f"{BACKEND}/resolve",
                json={"url": url},
                timeout=300
            )
            if r.status_code == 200:
                st.download_button(
                    f"Save Selected {i+1}",
                    r.content,
                    file_name=f"selected_{i+1}.mp4",
                    mime="video/mp4",
                    key=f"save_bulk_{i}"
                )
