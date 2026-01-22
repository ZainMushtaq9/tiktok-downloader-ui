import streamlit as st
import requests
import re

st.set_page_config(page_title="TikTok Downloader", layout="centered")

st.title("TikTok Video Downloader")
st.caption("Preview, select, and download videos like VidMate")

BACKEND_URL = "https://tiktok-downloader-backend-production-ce2b.up.railway.app/resolve"

# ------------------ INPUT MODE ------------------

mode = st.radio(
    "Choose input type",
    ["Video Links", "Profile Link"],
    horizontal=True
)

input_text = st.text_area(
    "Paste links",
    height=200,
    placeholder=(
        "Video links:\n"
        "https://www.tiktok.com/@user/video/123\n\n"
        "OR profile link:\n"
        "https://www.tiktok.com/@username"
    )
)

# ------------------ SESSION STATE ------------------

if "videos" not in st.session_state:
    st.session_state.videos = []

if "selected" not in st.session_state:
    st.session_state.selected = set()

# ------------------ HELPERS ------------------

def normalize_lines(text):
    return [l.strip() for l in text.splitlines() if l.strip().startswith("http")]

def is_profile(url):
    return "/@" in url and "/video/" not in url

def extract_video_id(url):
    m = re.search(r"/video/(\d+)", url)
    return m.group(1) if m else None

# ------------------ FETCH ------------------

if st.button("Fetch"):
    st.session_state.videos.clear()
    st.session_state.selected.clear()

    links = normalize_lines(input_text)

    if not links:
        st.warning("No valid links found")
        st.stop()

    st.info("Fetching videos…")

    # ⚠️ Profile handling (limited, safe)
    if mode == "Profile Link" and is_profile(links[0]):
        st.warning(
            "Profile download is limited on free hosting. "
            "Only latest videos may appear."
        )
        links = links[:5]  # safety limit

    for link in links:
        try:
            with st.spinner("Resolving video…"):
                res = requests.post(
                    BACKEND_URL,
                    json={"url": link},
                    stream=True,
                    timeout=120
                )

            if res.status_code != 200:
                continue

            video_bytes = res.content

            st.session_state.videos.append({
                "url": link,
                "bytes": video_bytes
            })

        except Exception:
            continue

# ------------------ UI CONTROLS ------------------

if st.session_state.videos:
    col1, col2 = st.columns(2)

    with col1:
        if st.button("Select All"):
            st.session_state.selected = set(range(len(st.session_state.videos)))

    with col2:
        if st.button("Unselect All"):
            st.session_state.selected.clear()

# ------------------ VIDEO LIST ------------------

for idx, vid in enumerate(st.session_state.videos):
    st.divider()

    checked = idx in st.session_state.selected
    check = st.checkbox(
        f"Select Video {idx + 1}",
        value=checked,
        key=f"chk_{idx}"
    )

    if check:
        st.session_state.selected.add(idx)
    else:
        st.session_state.selected.discard(idx)

    # 🎬 LIVE PREVIEW
    st.video(vid["bytes"])

    # ⬇️ SINGLE DOWNLOAD
    st.download_button(
        label="Download This Video",
        data=vid["bytes"],
        file_name=f"video_{idx+1}.mp4",
        mime="video/mp4"
    )

# ------------------ DOWNLOAD SELECTED ------------------

if st.session_state.selected:
    st.divider()
    st.subheader("Download Selected")

    for idx in sorted(st.session_state.selected):
        vid = st.session_state.videos[idx]

        st.download_button(
            label=f"Download Selected Video {idx+1}",
            data=vid["bytes"],
            file_name=f"selected_{idx+1}.mp4",
            mime="video/mp4"
        )
