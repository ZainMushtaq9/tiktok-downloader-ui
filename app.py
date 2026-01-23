import streamlit as st
import requests

# =========================
# CONFIG
# =========================

BACKEND = "https://tiktok-downloader-backend-production-ce2b.up.railway.app"

st.set_page_config(page_title="TikTok Profile Downloader", layout="wide")
st.title("TikTok Profile Downloader")

# =========================
# SESSION STATE
# =========================

if "videos" not in st.session_state:
    st.session_state.videos = []

# =========================
# INPUT
# =========================

profile_url = st.text_input(
    "TikTok Profile URL",
    placeholder="https://www.tiktok.com/@username"
)

quality = st.selectbox(
    "Video Quality",
    ["best", "720p", "480p"]
)

# =========================
# FETCH PROFILE
# =========================

if st.button("Fetch all videos from profile"):
    if not profile_url:
        st.warning("Enter a profile URL")
    else:
        with st.spinner("Scraping profile…"):
            r = requests.post(
                f"{BACKEND}/profile/all",
                json={"profile_url": profile_url},
                timeout=300
            )

        if r.status_code == 200:
            data = r.json()
            st.session_state.videos = data["videos"]
            st.success(f"Found {data['total']} videos")
        else:
            st.error("Failed to fetch profile videos")

# =========================
# VIDEO LIST
# =========================

if st.session_state.videos:
    st.divider()
    st.subheader(f"All videos ({len(st.session_state.videos)})")

    for idx, url in enumerate(st.session_state.videos, start=1):
        st.divider()

        st.markdown(f"### Video {idx}")
        st.caption(url)

        # Preview
        try:
            st.video(url)
        except:
            st.info("Preview not available")

        # Download button
        r = requests.post(
            f"{BACKEND}/download",
            json={"url": url, "quality": quality},
            stream=True,
            timeout=300
        )

        if r.status_code == 200:
            st.download_button(
                label=f"Download {idx}.mp4",
                data=r.content,
                file_name=f"{idx}.mp4",
                mime="video/mp4",
                key=f"dl_{idx}"
            )
        else:
            st.error("Download unavailable")
