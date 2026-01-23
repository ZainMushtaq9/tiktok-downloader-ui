import streamlit as st
import requests

BACKEND = "https://tiktok-downloader-backend-production-ce2b.up.railway.app"

st.set_page_config("TikTok Profile Downloader", layout="wide")
st.title("📥 TikTok Profile Downloader")

profile_url = st.text_input("TikTok Profile URL")
quality = st.selectbox("Quality", ["best", "720p", "480p"])

# Delay ONLY affects downloading
sleep_time = st.slider(
    "Delay between downloads (anti-block)",
    min_value=1,
    max_value=10,
    value=3
)

if "data" not in st.session_state:
    st.session_state.data = None

# -------------------------
# Fetch profile (NO delay)
# -------------------------

if st.button("Fetch profile"):
    with st.spinner("Fetching profile…"):
        r = requests.get(
            f"{BACKEND}/profile",
            params={"profile_url": profile_url},
            timeout=300
        )

    if r.status_code == 200:
        st.session_state.data = r.json()
        st.success(f"{r.json()['total']} videos found")
    else:
        st.error("Failed to fetch profile")

# -------------------------
# Download section
# -------------------------

if st.session_state.data:
    data = st.session_state.data

    st.subheader(f"Profile: {data['profile']}")
    st.caption("Delay applies only while downloading, not scraping")

    if st.button("⬇ Download ALL videos (one click)"):
        with st.spinner("Preparing download…"):
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
