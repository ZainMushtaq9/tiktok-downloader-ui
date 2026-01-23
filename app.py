import streamlit as st
import requests

BACKEND = "https://tiktok-downloader-backend-production-ce2b.up.railway.app"

st.set_page_config(page_title="TikTok Profile Downloader", layout="centered")
st.title("TikTok Profile Downloader")

# =========================
# SESSION STATE INIT
# =========================

if "videos" not in st.session_state:
    st.session_state.videos = []

if "checkbox" not in st.session_state:
    st.session_state.checkbox = {}   # index -> bool

if "selected" not in st.session_state:
    st.session_state.selected = set()

# =========================
# INPUT
# =========================

profile_url = st.text_input(
    "TikTok Profile URL",
    placeholder="https://www.tiktok.com/@username"
)

quality = st.selectbox("Video Quality", ["best", "720p", "480p"])

# =========================
# FETCH PROFILE VIDEOS
# =========================

if st.button("Fetch all videos from profile"):
    if not profile_url:
        st.warning("Enter profile URL")
    else:
        with st.spinner("Fetching videos…"):
            r = requests.post(
                f"{BACKEND}/profile/all",
                json={"profile_url": profile_url},
                timeout=600
            )

        if r.status_code == 200:
            st.session_state.videos = r.json()["videos"]

            # 🔥 AUTO-SELECT ALL AFTER SCRAPE
            st.session_state.checkbox = {
                i: True for i in range(len(st.session_state.videos))
            }
            st.session_state.selected = set(range(len(st.session_state.videos)))

            st.success(f"Fetched {len(st.session_state.videos)} videos (auto-selected)")
        else:
            st.error("Failed to fetch profile videos")

# =========================
# SELECT / UNSELECT BUTTONS
# =========================

if st.session_state.videos:
    c1, c2 = st.columns(2)

    with c1:
        if st.button("Select All"):
            for i in range(len(st.session_state.videos)):
                st.session_state.checkbox[i] = True
            st.session_state.selected = set(range(len(st.session_state.videos)))

    with c2:
        if st.button("Unselect All"):
            for i in range(len(st.session_state.videos)):
                st.session_state.checkbox[i] = False
            st.session_state.selected.clear()

# =========================
# VIDEO LIST
# =========================

for idx, url in enumerate(st.session_state.videos):
    st.divider()

    checked = st.checkbox(
        f"Video {idx + 1}",
        key=f"cb_{idx}",
        value=st.session_state.checkbox.get(idx, False)
    )

    # Sync state
    st.session_state.checkbox[idx] = checked
    if checked:
        st.session_state.selected.add(idx)
    else:
        st.session_state.selected.discard(idx)

    st.caption(url)

# =========================
# =========================
# DOWNLOAD SELECTED (AUTO-SEQUENCE)
# =========================

if st.session_state.selected:
    st.divider()
    st.subheader(f"{len(st.session_state.selected)} videos ready for download")

    if st.button("Download Selected Videos"):
        st.warning(
            "Your browser may ask permission for multiple downloads. Allow it once."
        )

        for count, i in enumerate(sorted(st.session_state.selected), start=1):
            url = st.session_state.videos[i]

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
                # Auto-trigger download without visible button spam
                st.download_button(
                    label=f"Downloading {count}.mp4",
                    data=r.content,
                    file_name=f"{count}.mp4",
                    mime="video/mp4",
                    key=f"auto_{count}"
                )
            else:
                st.error(f"Failed video {count}")
