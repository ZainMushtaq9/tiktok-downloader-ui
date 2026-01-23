import streamlit as st
import requests

BACKEND = "https://tiktok-downloader-backend-production-ce2b.up.railway.app"

st.set_page_config(page_title="TikTok Profile Downloader", layout="centered")
st.title("TikTok Profile Downloader")

# =========================
# SESSION STATE
# =========================

if "profile_url" not in st.session_state:
    st.session_state.profile_url = ""

if "videos" not in st.session_state:
    st.session_state.videos = []

if "selected" not in st.session_state:
    st.session_state.selected = set()

if "scraping" not in st.session_state:
    st.session_state.scraping = False

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
# RESET IF PROFILE CHANGES
# =========================

if profile_url != st.session_state.profile_url:
    st.session_state.profile_url = profile_url
    st.session_state.videos.clear()
    st.session_state.selected.clear()

# =========================
# SCRAPE ALL VIDEOS
# =========================

if st.button("Fetch all videos from profile"):
    if not profile_url:
        st.warning("Please enter a profile URL")
    else:
        st.session_state.scraping = True
        st.session_state.videos.clear()
        st.session_state.selected.clear()

        with st.spinner("Fetching videos… this may take time"):
            r = requests.post(
                f"{BACKEND}/profile/all",
                json={"profile_url": profile_url},
                timeout=900
            )

        if r.status_code == 200:
            st.session_state.videos = r.json()["videos"]
            st.success(f"Fetched {len(st.session_state.videos)} videos")
        else:
            st.error("Failed to fetch profile videos")

        st.session_state.scraping = False

# =========================
# VIDEO LIST
# =========================

if st.session_state.videos:
    st.divider()
    st.subheader(f"Videos found: {len(st.session_state.videos)}")

    c1, c2 = st.columns(2)
    with c1:
        if st.button("Select All"):
            st.session_state.selected = set(range(len(st.session_state.videos)))
    with c2:
        if st.button("Unselect All"):
            st.session_state.selected.clear()

    for idx, url in enumerate(st.session_state.videos):
        st.divider()

        checked = idx in st.session_state.selected
        if st.checkbox(f"Video {idx + 1}", value=checked, key=f"chk_{idx}"):
            st.session_state.selected.add(idx)
        else:
            st.session_state.selected.discard(idx)

        st.caption(url)

# =========================
# DOWNLOAD SELECTED
# =========================

if st.session_state.selected:
    st.divider()
    st.subheader(f"Download {len(st.session_state.selected)} selected videos")

    if st.button("Download Selected Videos"):
        st.info("Your browser will download videos one-by-one")

        for count, i in enumerate(sorted(st.session_state.selected), start=1):
            url = st.session_state.videos[i]

            with st.spinner(f"Downloading video {count}…"):
                r = requests.post(
                    f"{BACKEND}/download",
                    json={
                        "url": url,
                        "index": count,
                        "quality": quality
                    },
                    timeout=300
                )

            if r.status_code == 200:
                st.download_button(
                    label=f"Save {count}.mp4",
                    data=r.content,
                    file_name=f"{count}.mp4",
                    mime="video/mp4",
                    key=f"save_{count}"
                )
            else:
                st.error(f"Failed to download video {count}")
