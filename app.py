import streamlit as st
import requests
import urllib.parse
import time

# =========================
# CONFIG
# =========================

BACKEND = "https://tiktok-downloader-backend-production-ce2b.up.railway.app"

st.set_page_config(
    page_title="TikTok Profile Downloader",
    layout="wide"
)

st.title("📥 TikTok Profile Downloader")
st.caption("Mobile-friendly • Sequential downloads • Auto-named files")

# =========================
# SESSION STATE
# =========================

if "profile_data" not in st.session_state:
    st.session_state.profile_data = None

# =========================
# INPUTS
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
# FETCH PROFILE (WITH PROGRESS)
# =========================

if st.button("Fetch profile"):
    if not profile_url:
        st.warning("Please enter a TikTok profile URL")
    else:
        progress = st.progress(0)
        status = st.empty()

        status.info("Connecting to TikTok profile…")
        time.sleep(0.3)
        progress.progress(10)

        try:
            status.info("Scraping video list…")
            r = requests.get(
                f"{BACKEND}/profile",
                params={"profile_url": profile_url},
                timeout=300
            )
            progress.progress(70)
        except Exception:
            progress.empty()
            status.empty()
            st.error("Backend not reachable")
            r = None

        if r and r.status_code == 200:
            status.info("Finalizing results…")
            time.sleep(0.3)
            progress.progress(100)

            st.session_state.profile_data = r.json()
            total = r.json()["total"]

            progress.empty()
            status.empty()

            st.success(f"{total} videos found")
        else:
            progress.empty()
            status.empty()
            st.error("Failed to fetch profile (invalid URL or TikTok rate limit)")

# =========================
# DISPLAY RESULTS
# =========================

if st.session_state.profile_data:
    data = st.session_state.profile_data
    profile = data["profile"]
    videos = data["videos"]

    st.divider()
    st.subheader(f"Profile: {profile}")
    st.caption("Files will download as: profile_001.mp4, profile_002.mp4, …")

    # =========================
    # DOWNLOAD ALL (ONE CLICK)
    # =========================

    st.info(
        "Tap **Download all videos**.\n"
        "Your browser may ask permission once for multiple downloads."
    )

    if st.button("⬇ Download all videos at once"):
        for v in videos:
            url = (
                f"{BACKEND}/download?"
                f"url={urllib.parse.quote(v['url'])}"
                f"&index={v['index']}"
                f"&profile={profile}"
                f"&quality={quality}"
            )

            # Browser-handled download (lightweight)
            st.markdown(
                f'<a href="{url}" download></a>',
                unsafe_allow_html=True
            )

    # =========================
    # VIDEO LIST (VIDMATE STYLE)
    # =========================

    st.divider()
    st.subheader("Videos")

    for v in videos:
        col1, col2 = st.columns([1, 3], vertical_alignment="top")

        with col1:
            if v.get("thumbnail"):
                st.image(v["thumbnail"], use_column_width=True)

        with col2:
            st.markdown(f"**Video {v['index']}**")
            st.caption(v["url"])

            download_url = (
                f"{BACKEND}/download?"
                f"url={urllib.parse.quote(v['url'])}"
                f"&index={v['index']}"
                f"&profile={profile}"
                f"&quality={quality}"
            )

            st.markdown(
                f"[⬇ Download {v['index']}.mp4]({download_url})",
                unsafe_allow_html=True
            )
