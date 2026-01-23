import streamlit as st
import requests

BACKEND = "https://tiktok-downloader-backend-production-ce2b.up.railway.app"

st.set_page_config("TikTok Profile Downloader", layout="wide")
st.title("TikTok Profile Downloader")

profile_url = st.text_input("TikTok Profile URL")
quality = st.selectbox("Quality", ["best", "720p", "480p"])
mode = st.radio(
    "Download Mode",
    ["original", "black & white"],
    help="Black & white is label-only on free servers"
)

if "videos" not in st.session_state:
    st.session_state.videos = []

if st.button("Fetch all videos"):
    r = requests.get(
        f"{BACKEND}/profile/all",
        params={"profile_url": profile_url},
        timeout=300
    )
    if r.status_code == 200:
        st.session_state.videos = r.json()["videos"]
        st.success(f"{len(st.session_state.videos)} videos found")
    else:
        st.error("Failed to fetch profile")

for i, url in enumerate(st.session_state.videos, 1):
    st.divider()
    st.markdown(f"### Video {i}")
    st.code(url)

    download_url = (
        f"{BACKEND}/download"
        f"?url={url}&quality={quality}"
        f"&mode={'bw' if mode == 'black & white' else 'original'}"
    )

    st.markdown(
        f"[⬇ Download {i}.mp4]({download_url})",
        unsafe_allow_html=True
    )

if mode == "black & white":
    st.info(
        "Black & white is a labeled download only.\n"
        "True video filtering requires FFmpeg (not available on free tier)."
    )
