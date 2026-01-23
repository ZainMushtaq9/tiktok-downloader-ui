import streamlit as st
import requests
import urllib.parse

# =========================
# CONFIG
# =========================

BACKEND = "https://tiktok-downloader-backend-production-ce2b.up.railway.app"

st.set_page_config(
    page_title="TikTok Profile Downloader",
    layout="wide"
)

st.title("📥 TikTok Profile Downloader")
st.caption("Mobile-friendly • Select & download • Auto-named files")

# =========================
# SESSION STATE
# =========================

if "profile_data" not in st.session_state:
    st.session_state.profile_data = None

if "selected" not in st.session_state:
    st.session_state.selected = set()

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
# FETCH PROFILE
# =========================

if st.button("Fetch profile"):
    if not profile_url:
        st.warning("Please enter a TikTok profile URL")
    else:
        with st.spinner("Fetching profile…"):
            r = requests.get(
                f"{BACKEND}/profile",
                params={"profile_url": profile_url},
                timeout=300
            )

        if r.status_code == 200:
            data = r.json()
            st.session_state.profile_data = data

            # AUTO-SELECT ALL VIDEOS
            st.session_state.selected = {
                v["index"] for v in data["videos"]
            }

            st.success(f"{data['total']} videos found")
        else:
            st.error("Failed to fetch profile (TikTok rate limit or invalid URL)")

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
    # SELECT + DOWNLOAD CONTROLS
    # =========================

    c1, c2 = st.columns([1, 2])

    with c1:
        select_all = st.checkbox(
            "Select all videos",
            value=len(st.session_state.selected) == len(videos)
        )

    with c2:
        if st.button("⬇ Download selected videos"):
            for v in videos:
                if v["index"] in st.session_state.selected:
                    download_url = (
                        f"{BACKEND}/download?"
                        f"url={urllib.parse.quote(v['url'])}"
                        f"&index={v['index']}"
                        f"&profile={profile}"
                        f"&quality={quality}"
                    )

                    st.markdown(
                        f'<a href="{download_url}" download></a>',
                        unsafe_allow_html=True
                    )

    # Handle Select All / Unselect All
    if select_all:
        st.session_state.selected = {v["index"] for v in videos}
    else:
        st.session_state.selected.clear()

    st.info(
        "All videos are selected by default.\n"
        "Your browser may ask permission once for multiple downloads."
    )

    # =========================
    # VIDEO LIST
    # =========================

    st.divider()
    st.subheader("Videos")

    for v in videos:
        col1, col2 = st.columns([1, 3], vertical_alignment="top")

        with col1:
            checked = v["index"] in st.session_state.selected
            if st.checkbox(
                f"Video {v['index']}",
                value=checked,
                key=f"chk_{v['index']}"
            ):
                st.session_state.selected.add(v["index"])
            else:
                st.session_state.selected.discard(v["index"])

            if v.get("thumbnail"):
                st.image(v["thumbnail"], use_column_width=True)

        with col2:
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
