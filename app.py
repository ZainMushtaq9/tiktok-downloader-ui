import streamlit as st
import requests
from urllib.parse import urlencode

BACKEND = "https://tiktok-downloader-backend-production-ce2b.up.railway.app"

st.set_page_config(page_title="TikTok Profile Downloader", layout="wide")
st.title("TikTok Profile Downloader")

profile_url = st.text_input("TikTok Profile URL")
quality = st.selectbox("Quality", ["best", "720p", "480p"])

if "videos" not in st.session_state:
    st.session_state.videos = []

if st.button("Fetch all videos"):
    with st.spinner("Scraping profile…"):
        r = requests.get(
            f"{BACKEND}/profile/all",
            params={"profile_url": profile_url},
            timeout=300
        )
    if r.status_code == 200:
        data = r.json()
        st.session_state.videos = data["videos"]
        st.success(f"{data['total']} videos found")
    else:
        st.error("Failed to fetch profile")

if st.session_state.videos:
    for idx, url in enumerate(st.session_state.videos, start=1):
        st.divider()
        st.markdown(f"### Video {idx}")
        st.code(url)

        download_url = (
            f"{BACKEND}/download?"
            + urlencode({"url": url, "quality": quality})
        )

        st.download_button(
            label=f"Download {idx}.mp4 (B&W)",
            data=requests.get(download_url, stream=True).raw,
            file_name=f"{idx}.mp4",
            mime="video/mp4",
            key=f"dl_{idx}"
        )
