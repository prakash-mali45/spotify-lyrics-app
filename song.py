import streamlit as st
from spotipy import Spotify
from spotipy.oauth2 import SpotifyClientCredentials
from youtubesearchpython import VideosSearch

# -----------------------------
# Spotify API credentials
# -----------------------------
SPOTIFY_CLIENT_ID = "b6ccc00d266b4c28b249d3d3e5d9949f"
SPOTIFY_CLIENT_SECRET = "9cf6ca53668d4e64a5eed6f799dbfa08"

sp = Spotify(client_credentials_manager=SpotifyClientCredentials(
    client_id=SPOTIFY_CLIENT_ID, client_secret=SPOTIFY_CLIENT_SECRET))

# -----------------------------
# Streamlit Config
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
    iframe {
        border-radius:15px;
    }
    </style>
""", unsafe_allow_html=True)

# -----------------------------
# Helper: YouTube Search
# -----------------------------
@st.cache_data(show_spinner=False)
def youtube_search(query):
    search_terms = [f"{query} official video", f"{query} lyrics", f"{query} audio"]
    for term in search_terms:
        try:
            results = VideosSearch(term, limit=1).result()
            if results.get("result"):
                v = results["result"][0]
                vid_id = v.get("id") or v.get("link", "").split("v=")[-1]
                return {
                    "title": v.get("title"),
                    "id": vid_id,
                    "link": v.get("link"),
                    "channel": v.get("channel", {}).get("name")
                }
        except Exception:
            continue
    return None

# -----------------------------
# Header
# -----------------------------
st.markdown("<div class='main-title'>🎧 Spotify + YouTube Explorer</div>", unsafe_allow_html=True)
st.markdown("<div class='sub'>Search any song and instantly stream its YouTube video!</div>", unsafe_allow_html=True)

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

                yt = youtube_search(f"{title} {artists}")

                st.markdown("<div class='card'>", unsafe_allow_html=True)
                c1, c2 = st.columns([1.2, 2])  # Spotify info | YouTube video

                # --- Left: Spotify Info ---
                with c1:
                    st.image(img, use_container_width=True)
                    st.markdown(f"### 🎵 {title}")
                    st.markdown(f"**Artist:** {artists}")
                    st.markdown(f"**Album:** {album}")
                    st.markdown(f"**Release Date:** {release}")
                    st.markdown(f"[🎧 Listen on Spotify]({spotify_link})")

                # --- Right: YouTube Video ---
                with c2:
                    if yt:
                        st.markdown(f"**🎬 {yt['title']}** — {yt['channel']}")
                        embed_url = f"https://www.youtube.com/embed/{yt['id']}"
                        st.components.v1.iframe(embed_url, height=315)
                        st.markdown(f"[▶️ Watch on YouTube]({yt['link']})")
                    else:
                        st.info("No YouTube video found.")

                st.markdown("</div>", unsafe_allow_html=True)
