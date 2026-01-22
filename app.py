import streamlit as st
import requests

st.set_page_config(page_title="TikTok Video Downloader", layout="centered")

st.title("TikTok Video Downloader")
st.caption("Download public TikTok videos. One click per video.")

links_text = st.text_area(
    "Paste TikTok links (one per line)",
    height=200,
    placeholder="https://www.tiktok.com/@username/video/1234567890"
)

process_btn = st.button("Process Links")

def normalize_links(text):
    return [l.strip() for l in text.splitlines() if l.strip().startswith("http")]

# ✅ YOUR WORKING RAILWAY BACKEND
BACKEND_URL = "https://tiktok-downloader-backend-production-ce2b.up.railway.app/resolve"

if process_btn:
    links = normalize_links(links_text)

    if not links:
        st.warning("No valid TikTok links found.")
        st.stop()

    st.info(f"Processing {len(links)} links...")

    for idx, link in enumerate(links, 1):
        st.divider()

        try:
            with st.spinner("Downloading video (first request may be slow)…"):
                res = requests.post(
                    BACKEND_URL,
                    json={"url": link},
                    stream=True,
                    timeout=300
                )

            if res.status_code != 200:
                st.error("Backend error or video blocked")
                continue

            st.download_button(
                label=f"Download Video {idx}",
                data=res.content,
                file_name=f"video_{idx}.mp4",
                mime="video/mp4"
            )

        except requests.exceptions.Timeout:
            st.error("Timeout (Railway waking up, try again)")
        except Exception as e:
            st.error(str(e))
