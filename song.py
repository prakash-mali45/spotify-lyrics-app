import streamlit as st
from spotipy import Spotify
from spotipy.oauth2 import SpotifyClientCredentials
from youtubesearchpython import VideosSearch

# -----------------------------
# Config / Credentials
# -----------------------------
SPOTIFY_CLIENT_ID = st.secrets.get("SPOTIFY_CLIENT_ID", "b6ccc00d266b4c28b249d3d3e5d9949f")
SPOTIFY_CLIENT_SECRET = st.secrets.get("SPOTIFY_CLIENT_SECRET", "9cf6ca53668d4e64a5eed6f799dbfa08")

sp = Spotify(client_credentials_manager=SpotifyClientCredentials(
    client_id=SPOTIFY_CLIENT_ID, client_secret=SPOTIFY_CLIENT_SECRET))

# -----------------------------
# Page Config
# -----------------------------
st.set_page_config(page_title="🎧 Spotify + YouTube Explorer", layout="wide")

st.markdown("""
    <style>
        .song-card {
            border-radius: 14px;
            padding: 20px;
            box-shadow: 0 6px 20px rgba(0,0,0,0.08);
            background: linear-gradient(180deg, #ffffff, #f7f9ff);
            margin-bottom: 25px;
            transition: transform 0.2s ease;
        }
        .song-card:hover { transform: scale(1.01); }
        .meta {font-size: 14px; color:#333; margin-bottom: 6px;}
        .small {font-size: 13px; color:#555;}
        .stAudio, iframe {border-radius: 10px; margin-top: 10px;}
        h3 {color: #1DB954; margin-bottom: 8px;}
        .section-title {margin-top: 30px; font-size: 22px; color:#1DB954;}
        .yt-section {margin-top: 10px;}
    </style>
""", unsafe_allow_html=True)

st.title("🎧 Spotify + YouTube Explorer")
st.caption("Find Spotify tracks, play previews, and watch the best YouTube videos. Recommendations included!")

# -----------------------------
# YouTube search
# -----------------------------
@st.cache_data(show_spinner=False)
def youtube_search(query, limit=1):
    try:
        vs = VideosSearch(query, limit=limit)
        res = vs.result().get("result", [])
        if not res:
            return None
        top = res[0]
        return {
            "title": top.get("title"),
            "id": top.get("id"),
            "link": top.get("link"),
            "duration": top.get("duration"),
            "channel": top.get("channel", {}).get("name")
        }
    except Exception:
        return None

# -----------------------------
# Search input
# -----------------------------
query = st.text_input("🎵 Search a song or artist", placeholder="e.g., Shape of You, Blinding Lights")

if st.button("Search") and query.strip():
    with st.spinner("Searching Spotify..."):
        try:
            results = sp.search(q=query, limit=6, type="track")
            tracks = results.get("tracks", {}).get("items", [])
        except Exception as e:
            st.error(f"Spotify error: {e}")
            tracks = []

    if not tracks:
        st.warning("No songs found. Try another keyword.")
    else:
        cols = st.columns(2)
        for idx, track in enumerate(tracks):
            with cols[idx % 2]:
                st.markdown('<div class="song-card">', unsafe_allow_html=True)

                title = track["name"]
                artists = ", ".join([a["name"] for a in track["artists"]])
                album = track["album"]["name"]
                release = track["album"]["release_date"]
                img_url = track["album"]["images"][0]["url"] if track["album"]["images"] else ""
                spotify_link = track["external_urls"]["spotify"]
                preview_url = track.get("preview_url")

                st.markdown(f"### {title}")
                st.markdown(f"**Artist:** {artists}")
                st.image(img_url, use_container_width=True)
                st.markdown(f"<div class='meta'><b>Album:</b> {album}</div>", unsafe_allow_html=True)
                st.markdown(f"<div class='meta'><b>Release:</b> {release}</div>", unsafe_allow_html=True)
                st.markdown(f"[🎧 Open in Spotify]({spotify_link})")

                if preview_url:
                    st.audio(preview_url, format="audio/mp3")
                else:
                    st.info("Preview not available.")

                yt_query = f"{title} {artists} official music video"
                yt = youtube_search(yt_query)
                if yt:
                    st.markdown('<div class="yt-section">', unsafe_allow_html=True)
                    st.markdown(f"**YouTube:** {yt['title']} — {yt['channel']}")
                    embed_url = f"https://www.youtube.com/embed/{yt['id']}"
                    st.components.v1.iframe(embed_url, width=560, height=315)
                    st.markdown(f"[▶️ Open on YouTube]({yt['link']})")
                    st.markdown('</div>', unsafe_allow_html=True)
                else:
                    st.info("No YouTube video found.")

                st.markdown('</div>', unsafe_allow_html=True)

        # -----------------------------
        # Recommendations Section
        # -----------------------------
        st.markdown("<div class='section-title'>🎶 Recommended Songs</div>", unsafe_allow_html=True)
        try:
            seed_id = tracks[0]["id"]
            recs = sp.recommendations(seed_tracks=[seed_id], limit=6)
            rec_tracks = recs.get("tracks", [])
            for rec in rec_tracks:
                name = rec["name"]
                artists = ", ".join([a["name"] for a in rec["artists"]])
                link = rec["external_urls"]["spotify"]
                st.write(f"• **{name}** — {artists} — [Open in Spotify]({link})")
        except Exception as e:
            st.warning(f"Could not fetch recommendations: {e}")
