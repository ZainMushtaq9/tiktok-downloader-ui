import streamlit as st
import requests

BACKEND = "https://tiktok-downloader-backend-production-ce2b.up.railway.app"

st.set_page_config("TikTok Profile Downloader", layout="wide")
st.title("📥 TikTok Profile Downloader")

profile_url = st.text_input("TikTok Profile URL")
quality = st.selectbox("Quality", ["best", "720p", "480p"])
sleep_time = st.slider("Delay between videos (seconds)", 1, 10, 3)

if "data" not in st.session_state:
    st.session_state.data = None

if st.button("Fetch profile"):
    r = requests.get(f"{BACKEND}/profile", params={"profile_url": profile_url})
    if r.status_code == 200:
        st.session_state.data = r.json()
        st.success(f"{r.json()['total']} videos found")
    else:
        st.error("Failed to fetch profile")

if st.session_state.data:
    data = st.session_state.data

    st.subheader(f"Profile: {data['profile']}")
    st.caption("All videos will be downloaded with one click")

    if st.button("⬇ Download ALL videos (ONE CLICK)"):
        r = requests.post(
            f"{BACKEND}/download-all",
            json={
                "profile": data["profile"],
                "urls": data["videos"],
                "quality": quality,
                "sleep_seconds": sleep_time
            },
            timeout=3600
        )

        if r.status_code == 200:
            st.download_button(
                "Save ZIP",
                r.content,
                file_name=f"{data['profile']}.zip",
                mime="application/zip"
            )
        else:
            st.error("Download failed")
