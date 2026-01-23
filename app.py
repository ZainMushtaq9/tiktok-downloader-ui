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
# FETCH PROFILE
# =========================

if st.button("Fetch profile"):
    if not profile_url:
        st.warning("Please enter a TikTok profile URL")
    else:
        with st.spinner("Fetching profile…"):
            try:
                r = requests.get(
                    f"{BACKEND}/profile",
                    params={"profile_url": profile_url},
                    timeout=300
                )
            except Exception:
                st.error("Backend not reachable")
                r = None

        if r and r.status_code == 200:
            st.session_state.profile_data = r.json()
            st.success(f"{r.json()['total']} videos found")
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

    # -------------------------
    # DOWNLOAD ALL (SEQUENTIAL)
    # -------------------------

    st.info(
        "Tap **Download all videos**.\n"
        "Your browser may ask permission once for multiple downloads."
    )

    if st.button("⬇ Download all videos"):
        for v in videos:
            url = (
                f"{BACKEND}/download?"
                f"url={urllib.parse.quote(v['url'])}"
                f"&index={v['index']}"
                f"&profile={profile}"
                f"&quality={quality}"
            )

            # Invisible link – user-initiated via button
            st.markdown(
                f'<a href="{url}" download></a>',
                unsafe_allow_html=True
            )

    # -------------------------
    # VIDEO LIST (VIDMATE STYLE)
    # -------------------------

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
