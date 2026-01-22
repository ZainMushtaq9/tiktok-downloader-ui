import streamlit as st
import requests

st.set_page_config(page_title="TikTok Downloader", layout="centered")

st.title("TikTok Video Downloader")
st.caption("Select, preview, and download like VidMate")

BACKEND_URL = "https://tiktok-downloader-backend-production-ce2b.up.railway.app/resolve"

links_text = st.text_area(
    "Paste TikTok video links (one per line)",
    height=200,
    placeholder="https://www.tiktok.com/@username/video/1234567890"
)

if "links" not in st.session_state:
    st.session_state.links = []

if "selected" not in st.session_state:
    st.session_state.selected = set()

# ------------------ LOAD LINKS ------------------

if st.button("Load Links"):
    st.session_state.links = [
        l.strip() for l in links_text.splitlines()
        if l.strip().startswith("http")
    ]
    st.session_state.selected.clear()

if not st.session_state.links:
    st.stop()

# ------------------ SELECT CONTROLS ------------------

col1, col2 = st.columns(2)

with col1:
    if st.button("Select All"):
        st.session_state.selected = set(range(len(st.session_state.links)))

with col2:
    if st.button("Unselect All"):
        st.session_state.selected.clear()

# ------------------ LIST VIDEOS ------------------

for idx, link in enumerate(st.session_state.links):
    st.divider()

    checked = idx in st.session_state.selected
    check = st.checkbox(
        f"Video {idx+1}",
        value=checked,
        key=f"chk_{idx}"
    )

    if check:
        st.session_state.selected.add(idx)
    else:
        st.session_state.selected.discard(idx)

    st.caption(link)

    # ▶️ PREVIEW BUTTON
    if st.button(f"Play Preview {idx+1}", key=f"play_{idx}"):
        with st.spinner("Loading preview…"):
            res = requests.post(
                BACKEND_URL,
                json={"url": link},
                timeout=300
            )
            if res.status_code == 200:
                st.video(res.content)
            else:
                st.error("Preview failed")

    # ⬇️ SINGLE DOWNLOAD
    if st.button(f"Download Video {idx+1}", key=f"dl_{idx}"):
        with st.spinner("Downloading…"):
            res = requests.post(
                BACKEND_URL,
                json={"url": link},
                timeout=300
            )
            if res.status_code == 200:
                st.download_button(
                    "Save File",
                    data=res.content,
                    file_name=f"video_{idx+1}.mp4",
                    mime="video/mp4",
                    key=f"save_{idx}"
                )
            else:
                st.error("Download failed")

# ------------------ DOWNLOAD SELECTED ------------------

if st.session_state.selected:
    st.divider()
    st.subheader("Download Selected Videos")

    for idx in sorted(st.session_state.selected):
        link = st.session_state.links[idx]

        if st.button(f"Download Selected {idx+1}", key=f"bulk_{idx}"):
            with st.spinner("Downloading…"):
                res = requests.post(
                    BACKEND_URL,
                    json={"url": link},
                    timeout=300
                )
                if res.status_code == 200:
                    st.download_button(
                        f"Save Selected {idx+1}",
                        data=res.content,
                        file_name=f"selected_{idx+1}.mp4",
                        mime="video/mp4",
                        key=f"save_bulk_{idx}"
                    )
                else:
                    st.error("Failed")
