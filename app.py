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
st.caption("Select videos • Download individually or all at once")

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

            st.success(
                f"Profile: {data['profile']}  |  "
                f"Available videos: {data['total']}"
            )
        else:
            st.error("Failed to fetch profile (TikTok rate limit or invalid URL)")

# =========================
# MAIN UI
# =========================

if st.session_state.profile_data:
    data = st.session_state.profile_data
    profile = data["profile"]
    videos = data["videos"]

    st.divider()

    # =========================
    # TOP CONTROLS (ALIGNED)
    # =========================

    col1, col2, col3 = st.columns([1, 1, 2])

    with col1:
        select_all = st.checkbox(
            "Select all",
            value=len(st.session_state.selected) == len(videos)
        )

        if select_all:
            st.session_state.selected = {v["index"] for v in videos}
        else:
            st.session_state.selected.clear()

    with col2:
        st.markdown(
            f"**Selected:** {len(st.session_state.selected)} / {len(videos)}"
        )

    with col3:
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

                    # Browser-handled download
                    st.markdown(
                        f'<a href="{download_url}" download></a>',
                        unsafe_allow_html=True
                    )

    st.divider()
    st.subheader("Videos on profile")

    # =========================
    # VIDEO LIST
    # =========================

    for v in videos:
        col1, col2, col3 = st.columns([0.5, 1, 3], vertical_alignment="center")

        with col1:
            checked = v["index"] in st.session_state.selected
            if st.checkbox(
                "",
                value=checked,
                key=f"chk_{v['index']}"
            ):
                st.session_state.selected.add(v["index"])
            else:
                st.session_state.selected.discard(v["index"])

        with col2:
            if v.get("thumbnail"):
                st.image(v["thumbnail"], use_column_width=True)

        with col3:
            st.markdown(f"**Video {v['index']}**")
            st.caption(v["url"])

            single_download = (
                f"{BACKEND}/download?"
                f"url={urllib.parse.quote(v['url'])}"
                f"&index={v['index']}"
                f"&profile={profile}"
                f"&quality={quality}"
            )

            st.markdown(
                f"[⬇ Download {v['index']}.mp4]({single_download})",
                unsafe_allow_html=True
            )
