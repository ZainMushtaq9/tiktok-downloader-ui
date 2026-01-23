import streamlit as st
import requests

BACKEND = "https://tiktok-downloader-backend-production-ce2b.up.railway.app"

st.set_page_config("TikTok Profile Downloader", layout="wide")
st.title("📥 TikTok Profile Downloader")
st.caption("Mobile-friendly • Sequential downloads • Auto-named")

profile_url = st.text_input(
    "TikTok Profile URL",
    placeholder="https://www.tiktok.com/@username"
)

quality = st.selectbox("Quality", ["best", "720p", "480p"])

if "data" not in st.session_state:
    st.session_state.data = None

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

if st.session_state.data:
    data = st.session_state.data
    profile = data["profile"]
    videos = data["videos"]

    st.divider()
    st.subheader(f"Profile: {profile}")

    st.info(
        "Tap **Download All Videos**.\n"
        "Your browser may ask permission once."
    )

    # AUTO DOWNLOAD ALL (SEQUENTIAL)
    if st.button("⬇ Download all videos"):
        for v in videos:
            url = (
                f"{BACKEND}/download"
                f"?url={v['url']}"
                f"&index={v['index']}"
                f"&profile={profile}"
                f"&quality={quality}"
            )
            st.markdown(
                f'<a href="{url}" download></a>',
                unsafe_allow_html=True
            )

    st.divider()
    st.subheader("Videos")

    # VIDMATE-STYLE LIST
    for v in videos:
        col1, col2 = st.columns([1, 3])

        with col1:
            if v.get("thumbnail"):
                st.image(v["thumbnail"], use_column_width=True)

        with col2:
            st.markdown(f"**Video {v['index']}**")
            st.caption(v["url"])

            download_url = (
                f"{BACKEND}/download"
                f"?url={v['url']}"
                f"&index={v['index']}"
                f"&profile={profile}"
                f"&quality={quality}"
            )

            st.markdown(
                f"[⬇ Download {v['index']}.mp4]({download_url})",
                unsafe_allow_html=True
            )
