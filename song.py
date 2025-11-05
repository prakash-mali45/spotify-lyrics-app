import streamlit as st
from spotipy import Spotify
from spotipy.oauth2 import SpotifyClientCredentials
import requests
from urllib.parse import quote_plus

# -----------------------------
# Spotify Credentials
# -----------------------------
SPOTIFY_CLIENT_ID = "b6ccc00d266b4c28b249d3d3e5d9949f"
SPOTIFY_CLIENT_SECRET = "9cf6ca53668d4e64a5eed6f799dbfa08"

sp = Spotify(client_credentials_manager=SpotifyClientCredentials(
    client_id=SPOTIFY_CLIENT_ID, client_secret=SPOTIFY_CLIENT_SECRET))

# -----------------------------
# Streamlit UI Setup
# -----------------------------
st.set_page_config(page_title="🎵 Spotify + YouTube Finder", layout="wide")

st.markdown("""
    <style>
    body { background-color: #f7f9fc; }
    .main-title { text-align:center; font-size:38px; font-weight:700; color:#1DB954; margin-bottom:10px; }
    .sub { text-align:center; color:#555; font-size:16px; margin-bottom:40px; }
    .card {
        background:white;
        padding:25px;
        border-radius:20px;
        box-shadow:0 6px 18px rgba(0,0,0,0.08);
        margin-bottom:40px;
        transition:0.3s;
    }
    .card:hover {
        box-shadow:0 10px 25px rgba(0,0,0,0.15);
        transform: translateY(-2px);
    }
    </style>
""", unsafe_allow_html=True)

# -----------------------------
# YouTube Search (Custom)
# -----------------------------
def youtube_search_fallback(query):
    """Search YouTube video by scraping — works even when API fails."""
    try:
        search_query = quote_plus(query + " official video")
        url = f"https://www.youtube.com/results?search_query={search_query}"
        html = requests.get(url).text
        start = html.find("/watch?v=")
        if start != -1:
            video_id = html[start+9:start+20]
            return {
                "id": video_id,
                "link": f"https://www.youtube.com/watch?v={video_id}"
            }
    except:
        pass
    return None

# -----------------------------
# Header
# -----------------------------
st.markdown("<div class='main-title'>🎧 Spotify + YouTube Explorer</div>", unsafe_allow_html=True)
st.markdown("<div class='sub'>Find Spotify songs with direct YouTube links!</div>", unsafe_allow_html=True)

# -----------------------------
# Input
# -----------------------------
query = st.text_input("🎵 Enter Song or Artist Name:")

if st.button("Search"):
    if not query.strip():
        st.warning("Please enter a valid song or artist.")
    else:
        with st.spinner("Fetching songs..."):
            results = sp.search(q=query, limit=5, type="track")
            tracks = results.get("tracks", {}).get("items", [])

        if not tracks:
            st.warning("No songs found.")
        else:
            for track in tracks:
                title = track["name"]
                artists = ", ".join([a["name"] for a in track["artists"]])
                album = track["album"]["name"]
                release = track["album"]["release_date"]
                img = track["album"]["images"][0]["url"]
                spotify_link = track["external_urls"]["spotify"]

                yt = youtube_search_fallback(f"{title} {artists}")

                st.markdown("<div class='card'>", unsafe_allow_html=True)
                col1, col2 = st.columns([1.2, 2])

                with col1:
                    st.image(img, use_container_width=True)
                    st.markdown(f"### 🎵 {title}")
                    st.markdown(f"**Artist:** {artists}")
                    st.markdown(f"**Album:** {album}")
                    st.markdown(f"**Release Date:** {release}")
                    st.markdown(f"[🎧 Listen on Spotify]({spotify_link})")

                with col2:
                    if yt:
                        thumbnail = f"https://img.youtube.com/vi/{yt['id']}/hqdefault.jpg"
                        st.markdown(
                            f"""
                            <a href="{yt['link']}" target="_blank">
                                <img src="{thumbnail}" width="100%" 
                                style="border-radius:12px; box-shadow:0 4px 12px rgba(0,0,0,0.2);">
                            </a>
                            <br>
                            <a href="{yt['link']}" target="_blank" style="text-decoration:none;">
                                ▶️ Watch on YouTube
                            </a>
                            """,
                            unsafe_allow_html=True
                        )
                    else:
                        st.info("No YouTube video found.")

                st.markdown("</div>", unsafe_allow_html=True)
