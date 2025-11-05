import streamlit as st
from spotipy import Spotify
from spotipy.oauth2 import SpotifyClientCredentials
import lyricsgenius

# -----------------------------
# Spotify Credentials
# -----------------------------
CLIENT_ID = 'b6ccc00d266b4c28b249d3d3e5d9949f'
CLIENT_SECRET = '9cf6ca53668d4e64a5eed6f799dbfa08'

# -----------------------------
# Genius API Token
# -----------------------------
GENIUS_TOKEN = 'FQ7nR9AU4o2KduQP54vxNR4gKK7HzSMwxF_vMOmO0WlGF9THKm3Q12T99-edP_BY'

# -----------------------------
# Spotify and Genius setup
# -----------------------------
sp = Spotify(client_credentials_manager=SpotifyClientCredentials(client_id=CLIENT_ID, client_secret=CLIENT_SECRET))
genius = lyricsgenius.Genius(GENIUS_TOKEN, skip_non_songs=True, verbose=False)

st.set_page_config(page_title="🎵 Spotify Song Finder", layout="wide")
st.title("🎵 Spotify Song Info Finder with Lyrics & Suggestions")

# -----------------------------
# User input
# -----------------------------
song_name = st.text_input("Enter Song Name or Artist Name:")

if st.button("Search"):
    if song_name.strip() == "":
        st.error("Please enter a valid song or artist name!")
    else:
        results = sp.search(q=song_name, limit=5, type='track')
        tracks = results['tracks']['items']

        if not tracks:
            st.warning("No results found. Try a different song or artist.")
        else:
            # Main results
            for idx, track in enumerate(tracks):
                with st.container():
                    st.markdown(f"### {track['name']}")
                    col1, col2 = st.columns([1, 3])
                    
                    # Album Art
                    with col1:
                        st.image(track['album']['images'][0]['url'], use_container_width=True)
                    
                    # Song info and preview
                    with col2:
                        st.write(f"**Artist:** {', '.join(a['name'] for a in track['artists'])}")
                        st.write(f"**Album:** {track['album']['name']}")
                        st.write(f"**Release Date:** {track['album']['release_date']}")
                        st.write(f"[Listen on Spotify]({track['external_urls']['spotify']})")

                        # Play/Pause Preview
                        preview_url = track['preview_url']
                        if preview_url:
                            play_preview = st.checkbox(f"▶️ Play Preview ({track['name']})", key=f"preview_{idx}")
                            if play_preview:
                                st.audio(preview_url, format='audio/mp3', start_time=0)
                        else:
                            st.write("Preview not available for this track.")

                    # Lyrics in scrollable box
                    try:
                        genius_song = genius.search_song(track['name'], track['artists'][0]['name'], get_full_info=False)
                        if not genius_song:
                            genius_song = genius.search_song(track['name'], None, get_full_info=False)
                        if genius_song and genius_song.lyrics:
                            st.write("**Lyrics:**")
                            st.markdown(
                                f"<div style='height:300px; overflow-y:auto; border:1px solid #ccc; padding:10px'>{genius_song.lyrics}</div>",
                                unsafe_allow_html=True
                            )
                        else:
                            st.write("Lyrics not found.")
                    except Exception as e:
                        st.write(f"Lyrics fetch error: {e}")

                    st.markdown("---")

            # -----------------------------
            # Suggested Songs
            # -----------------------------
            st.subheader("🎧 Suggested Songs Based on First Result")
            first_track_id = tracks[0]['id']
            try:
                recommendations = sp.recommendations(seed_tracks=[first_track_id], limit=5)
                for rec in recommendations['tracks']:
                    st.write(f"**{rec['name']}** by {', '.join(a['name'] for a in rec['artists'])}")
                    st.write(f"[Listen on Spotify]({rec['external_urls']['spotify']})")
                    st.markdown("---")
            except Exception as e:
                st.write(f"Could not fetch suggestions: {e}")
