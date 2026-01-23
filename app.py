import streamlit as st
import requests

# =========================
# CONFIG
# =========================

BACKEND = "https://tiktok-downloader-backend-production-ce2b.up.railway.app"

st.set_page_config(
    page_title="TikTok Profile Downloader",
    layout="wide"
)

st.title("TikTok Profile Downloader")
st.caption("Scrape all videos from a TikTok profile and download individually")

# =========================
# SESSION STATE
# =========================

if "videos" not in st.session_state:
    st.session_state.videos = []

if "profile_loaded" not in st.session_state:
    st.session_state.profile_loaded = False

# =========================
# INPUT CONTROLS
# =========================

profile_url = st.text_input(
    "TikTok Profile URL",
    placeholder="https://www.tiktok.com/@username"
)

quality = st.selectbox(
    "Video Quality",
    ["best", "720p", "480p"]
)

filter_type = st.selectbox(
    "Video Filter",
    ["original", "bw"]
)

urdu_caption = st.text_input(
    "Urdu Caption (optional)",
    placeholder="یہ ویڈیو بہترین ہے"
)

# =========================
# FETCH PROFILE
# =========================

if st.button("Fetch all videos from profile"):
    if not profile_url:
        st.warning("Please enter a TikTok profile URL")
    else:
        with st.spinner("Scraping profile, please wait..."):
            r = requests.post(
                f"{BACKEND}/profile/all",
                json={"profile_url": profile_url},
                timeout=300
            )

        if r.status_code == 200:
            data = r.json()
            st.session_state.videos = data["videos"]
            st.session_state.profile_loaded = True
            st.success(f"Found {data['total']} videos on this profile")
        else:
            st.error("Failed to scrape profile videos")

# =========================
# VIDEO LIST
# =========================

if st.session_state.profile_loaded and st.session_state.videos:
    st.divider()
    st.subheader(f"All Videos ({len(st.session_state.videos)})")

    st.info(
        "Tap any Download button to save that video. "
        "Your browser may ask permission for multiple downloads."
    )

    for idx, url in enumerate(st.session_state.videos, start=1):
        st.divider()

        st.markdown(f"### Video {idx}")
        st.code(url, language="text")

        # Download button
        try:
            response = requests.post(
                f"{BACKEND}/download",
                json={
                    "url": url,
                    "quality": quality,
                    "filter": filter_type,
                    "urdu_caption": urdu_caption if urdu_caption else None
                },
                stream=True,
                timeout=600
            )

            if response.status_code == 200:
                st.download_button(
                    label=f"Download {idx}.mp4",
                    data=response.content,
                    file_name=f"{idx}.mp4",
                    mime="video/mp4",
                    key=f"dl_{idx}"
                )
            else:
                st.error("Download not available")

        except requests.exceptions.Timeout:
            st.error("Download timeout (video too large or network slow)")
        except Exception as e:
            st.error(str(e))
