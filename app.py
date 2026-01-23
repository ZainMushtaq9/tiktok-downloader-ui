import streamlit as st
import requests
import time

BACKEND = "https://tiktok-downloader-backend-production-ce2b.up.railway.app"

st.set_page_config("TikTok Downloader", layout="wide")
st.title("📥 TikTok Profile Downloader")

profile_url = st.text_input("TikTok Profile URL")
quality = st.selectbox("Quality", ["best", "720p", "480p"])
delay = st.slider("Delay between downloads (seconds)", 1, 10, 3)

if "data" not in st.session_state:
    st.session_state.data = None

if st.button("Fetch profile"):
    r = requests.get(f"{BACKEND}/profile", params={"profile_url": profile_url})
    if r.status_code == 200:
        st.session_state.data = r.json()
        st.success(f"{r.json()['total']} videos found")
    else:
        st.error("Failed")

if st.session_state.data:
    data = st.session_state.data
    profile = data["profile"]
    videos = data["videos"]

    st.subheader(f"Profile: {profile}")

    if st.button("⬇ Download ALL videos"):
        for i, url in enumerate(videos, start=1):
            st.info(f"Downloading {i}/{len(videos)}")

            download_url = (
                f"{BACKEND}/download"
                f"?url={url}&index={i}&profile={profile}&quality={quality}"
            )

            st.markdown(
                f'<a href="{download_url}" download>Click to download {i}.mp4</a>',
                unsafe_allow_html=True
            )

            time.sleep(delay)
