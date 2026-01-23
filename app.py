import streamlit as st
import requests

BACKEND = "https://tiktok-downloader-backend-production-ce2b.up.railway.app"

st.set_page_config(page_title="TikTok Profile Downloader", layout="centered")
st.title("TikTok Profile Downloader")

profile_url = st.text_input(
    "TikTok Profile URL",
    placeholder="https://www.tiktok.com/@username"
)

quality = st.selectbox("Video Quality", ["best", "720p", "480p"])

# ======================
# SESSION STATE
# ======================

if "videos" not in st.session_state:
    st.session_state.videos = []

if "start_download" not in st.session_state:
    st.session_state.start_download = False


# ======================
# FETCH VIDEOS
# ======================

if st.button("Fetch all videos from profile"):
    with st.spinner("Fetching videos…"):
        r = requests.post(
            f"{BACKEND}/profile/all",
            json={"profile_url": profile_url},
            timeout=300
        )

    if r.status_code == 200:
        data = r.json()
        st.session_state.videos = data["videos"]
        st.success(f"{data['count']} videos ready")
    else:
        st.error("Failed to fetch videos")


# ======================
# DOWNLOAD SECTION
# ======================

if st.session_state.videos:
    st.warning(
        "⚠️ Your browser will ask permission to download multiple files.\n\n"
        "Please tap **Allow** once. All videos will then download automatically."
    )

    if st.button("Download all videos"):
        st.session_state.start_download = True

# ======================
# AUTO DOWNLOAD (ONE BY ONE)
# ======================

if st.session_state.start_download:
    for i, url in enumerate(st.session_state.videos, start=1):
        with st.spinner(f"Downloading {i}.mp4"):
            r = requests.post(
                f"{BACKEND}/download",
                json={"url": url, "quality": quality},
                timeout=300
            )

        if r.status_code == 200:
            st.download_button(
                label=f"Downloading {i}.mp4",
                data=r.content,
                file_name=f"{i}.mp4",
                mime="video/mp4",
                key=f"dl_{i}"
            )
        else:
            st.error(f"Failed video {i}")

    st.success("All downloads triggered")
    st.session_state.start_download = False
