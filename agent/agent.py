import random

def process_prompt(prompt: str, sp):
    """
    Converts natural language prompts into Spotify API actions using the Spotipy client.
    Supports playback control, track/album search, volume control, and vibe-based playlists.
    """
    prompt = prompt.lower()
    response = []

    # Split multiple commands chained with "and"
    commands = [c.strip() for c in prompt.split("and")]

    for cmd in commands:

        # --- Play a specific album ---
        if cmd.startswith("play album"):
            album = cmd.replace("play album", "").strip()
            result = sp.search(q=album, type="album", limit=1)

            if result['albums']['items']:
                album_id = result['albums']['items'][0]['id']
                tracks = sp.album_tracks(album_id)['items']
                uris = [t['uri'] for t in tracks]
                sp.start_playback(uris=uris)
                response.append(f"🎶 Playing album: {result['albums']['items'][0]['name']}")
            else:
                response.append("🚫 Album not found.")

        # --- Play user's liked songs ---
        elif "liked songs" in cmd or "my likes" in cmd:
            liked = sp.current_user_saved_tracks(limit=50)
            uris = [item['track']['uri'] for item in liked['items']]
            random.shuffle(uris)
            sp.start_playback(uris=uris)
            response.append("💖 Playing your liked songs.")

        # --- Start a randomized vibe session ---
        elif "vibe session" in cmd:
            genres = ["pop", "hip-hop", "rock", "lo-fi", "edm", "indie"]
            genre = random.choice(genres)
            recs = sp.recommendations(seed_genres=[genre], limit=20)
            uris = [track['uri'] for track in recs['tracks']]
            sp.start_playback(uris=uris)
            response.append(f"🌈 Starting a '{genre}' vibe session.")

        # --- Play a specific song ---
        elif cmd.startswith("play "):
            song = cmd.replace("play", "").strip()
            result = sp.search(q=song, type="track", limit=1)

            if result['tracks']['items']:
                uri = result['tracks']['items'][0]['uri']
                sp.start_playback(uris=[uri])
                response.append(f"🎵 Playing: {result['tracks']['items'][0]['name']}")
            else:
                response.append("🚫 Song not found.")

        # --- Pause playback ---
        elif "pause" in cmd:
            sp.pause_playback()
            response.append("⏸️ Music paused.")

        # --- Skip to next track ---
        elif "next" in cmd:
            sp.next_track()
            response.append("⏭️ Skipped to next track.")

        # --- Volume control (up/down) ---
        elif "volume up" in cmd or "volume down" in cmd:
            current = sp.current_playback()
            if current and current['device']:
                vol = current['device']['volume_percent']
                if "up" in cmd:
                    new_vol = min(vol + 10, 100)
                else:
                    new_vol = max(vol - 10, 0)
                sp.volume(new_vol)
                response.append(f"🔊 Volume set to {new_vol}%")
            else:
                response.append("⚠️ Can't fetch current volume.")

        # --- Fallback for unrecognized commands ---
        else:
            response.append(f"🤔 Didn't understand: '{cmd}'")

    return "\n".join(response)
