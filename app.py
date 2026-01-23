import streamlit as st
import requests

# =========================
# CONFIG
# =========================

BACKEND = "https://tiktok-downloader-backend-production-ce2b.up.railway.app"

st.set_page_config(
    page_title="TikTok Profile Downloader",
    layout="centered"
)

st.title("TikTok Profile Downloader")
st.caption("Fetch all videos from a TikTok profile (no limits)")

# =========================
# SESSION STATE
# =========================

if "videos" not in st.session_state:
    st.session_state.videos = []

if "selected" not in st.session_state:
    st.session_state.selected = set()

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

sleep_seconds = st.number_input(
    "Delay between videos (seconds, anti-blocking)",
    min_value=0,
    max_value=10,
    value=2
)

# =========================
# FETCH ALL VIDEOS
# =========================

if st.button("Fetch ALL videos from profile"):
    if not profile_url:
        st.warning("Please enter a profile URL")
    else:
        with st.spinner("Scraping profile… this may take time for large accounts"):
            r = requests.post(
                f"{BACKEND}/profile/all",
                json={
                    "profile_url": profile_url,
                    "sleep_seconds": sleep_seconds
                },
                timeout=900
            )

        if r.status_code == 200:
            data = r.json()
            st.session_state.videos = data["videos"]
            st.session_state.selected.clear()

            st.success(
                f"Found {data['total_videos']} videos on this profile"
            )
        else:
            st.error("Failed to scrape profile")

# =========================
# SHOW ALL VIDEOS
# =========================

if st.session_state.videos:
    st.divider()
    st.subheader(f"All videos ({len(st.session_state.videos)})")

    # -------------------------
    # SELECT CONTROLS
    # -------------------------

    c1, c2 = st.columns(2)

    with c1:
        if st.button("Select ALL videos"):
            st.session_state.selected = set(range(len(st.session_state.videos)))

    with c2:
        if st.button("Unselect ALL videos"):
            st.session_state.selected.clear()

    # -------------------------
    # VIDEO LIST (NO PAGINATION)
    # -------------------------

    for idx, url in enumerate(st.session_state.videos):
        st.divider()

        checked = idx in st.session_state.selected
        if st.checkbox(f"Video {idx + 1}", checked, key=f"chk_{idx}"):
            st.session_state.selected.add(idx)
        else:
            st.session_state.selected.discard(idx)

        st.caption(url)

        col1, col2 = st.columns(2)

        # -------- PREVIEW --------
        with col1:
            if st.button("Play", key=f"play_{idx}"):
                r = requests.post(
                    f"{BACKEND}/video",
                    json={"url": url, "quality": quality},
                    timeout=300
                )
                if r.status_code == 200:
                    st.video(r.content)
                else:
                    st.error("Preview failed")

        # -------- DOWNLOAD --------
        with col2:
            if st.button("Download", key=f"dl_{idx}"):
                r = requests.post(
                    f"{BACKEND}/video",
                    json={"url": url, "quality": quality},
                    timeout=300
                )
                if r.status_code == 200:
                    st.download_button(
                        "Save file",
                        r.content,
                        file_name=f"video_{idx + 1}.mp4",
                        mime="video/mp4",
                        key=f"save_{idx}"
                    )

# =========================
# ZIP DOWNLOAD
# =========================

if st.session_state.selected:
    st.divider()
    st.subheader(
        f"Download {len(st.session_state.selected)} selected videos as ZIP"
    )

    if st.button("Download selected as ZIP"):
        urls = [
            st.session_state.videos[i]
            for i in sorted(st.session_state.selected)
        ]

        with st.spinner("Preparing ZIP… this may take time"):
            r = requests.post(
                f"{BACKEND}/zip",
                json={"urls": urls, "quality": quality},
                timeout=3600
            )

        if r.status_code == 200:
            st.download_button(
                "Save ZIP",
                r.content,
                file_name="tiktok_videos.zip",
                mime="application/zip"
            )
        else:
            st.error("ZIP download failed")
