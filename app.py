import streamlit as st
import requests
import re

st.set_page_config(
    page_title="TikTok Video Downloader",
    layout="centered"
)

st.title("TikTok Video Downloader")
st.caption("Download public TikTok videos. One click per video.")

links_text = st.text_area(
    "Paste TikTok links (one per line)",
    height=200,
    placeholder=(
        "https://vt.tiktok.com/...\n"
        "https://www.tiktok.com/@username/video/1234567890"
    )
)

process_btn = st.button("Process Links")

def normalize_links(text):
    return [l.strip() for l in text.splitlines() if l.strip().startswith("http")]

def resolve_short_url(url):
    r = requests.get(url, allow_redirects=True, timeout=10)
    return r.url

def extract_video_id(url):
    m = re.search(r"/video/(\d+)", url)
    return m.group(1) if m else None

# 🔴 CHANGE THIS AFTER BACKEND DEPLOY
BACKEND_URL = "https://YOUR-BACKEND-NAME.onrender.com/resolve"

if process_btn:
    links = normalize_links(links_text)

    if not links:
        st.warning("No valid TikTok links found.")
        st.stop()

    st.info(f"Processing {len(links)} links...")

    for idx, link in enumerate(links, 1):
        st.divider()

        try:
            final_url = resolve_short_url(link)
            video_id = extract_video_id(final_url)

            if not video_id:
                st.error("Invalid TikTok URL")
                st.caption(final_url)
                continue

            st.success(f"Video {idx} ready")
            st.write(f"**Video ID:** `{video_id}`")
            st.caption(final_url)

            with st.spinner("Fetching video…"):
                res = requests.post(
                    BACKEND_URL,
                    json={"url": final_url},
                    timeout=180
                )

            if res.status_code != 200:
                st.error("Backend error")
                continue

            data = res.json()

            st.download_button(
                label=f"Download Video {idx}",
                data=bytes(data["file_bytes"]),
                file_name=data["filename"],
                mime="video/mp4"
            )

        except Exception as e:
            st.error(str(e))
