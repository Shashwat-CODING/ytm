from flask import Blueprint, current_app, jsonify, request

bp_entities = Blueprint("entities", __name__)


def _client():
	return current_app.config["YTMUSIC_CLIENT"]


@bp_entities.get("/songs/<video_id>")
def get_song(video_id: str):
	"""Get song details
	---
	parameters:
	  - name: video_id
	    in: path
	    type: string
	    required: true
	responses:
	  200:
	    description: Song metadata
	  500:
	    description: Song data unavailable
	"""
	try:
		data = _client().get_song(video_id)
		return jsonify(data)
	except Exception as e:
		return jsonify({"error": f"Song data unavailable: {str(e)}"}), 500


@bp_entities.get("/albums/<browse_id>")
def get_album(browse_id: str):
	"""Get album details
	---
	parameters:
	  - name: browse_id
	    in: path
	    type: string
	    required: true
	responses:
	  200:
	    description: Album metadata and tracks
	  500:
	    description: Album data unavailable
	"""
	try:
		data = _client().get_album(browse_id)
		return jsonify(data)
	except Exception as e:
		return jsonify({"error": f"Album data unavailable: {str(e)}"}), 500


@bp_entities.get("/artists/<browse_id>")
def get_artist(browse_id: str):
	"""Get artist details
	---
	parameters:
	  - name: browse_id
	    in: path
	    type: string
	    required: true
	responses:
	  200:
	    description: Artist info and releases
	  500:
	    description: Artist data unavailable
	"""
	try:
		data = _client().get_artist(browse_id)
		return jsonify(data)
	except Exception as e:
		return jsonify({"error": f"Artist data unavailable: {str(e)}"}), 500


@bp_entities.get("/playlists/<playlist_id>")
def get_playlist(playlist_id: str):
	"""Get playlist details
	---
	parameters:
	  - name: playlist_id
	    in: path
	    type: string
	    required: true
	  - name: limit
	    in: query
	    type: integer
	    required: false
	    default: 100
	responses:
	  200:
	    description: Playlist metadata and items
	  500:
	    description: Playlist data unavailable
	"""
	limit = request.args.get("limit", default=100, type=int)
	try:
		data = _client().get_playlist(playlist_id, limit=limit)
		return jsonify(data)
	except Exception as e:
		return jsonify({"error": f"Playlist data unavailable: {str(e)}"}), 500


@bp_entities.get("/artist/<browse_id>")
def get_artist_summary(browse_id: str):
	"""Get concise artist summary (name, top songs playlist, recommendations, featured-on)
	---
	parameters:
	  - name: browse_id
	    in: path
	    type: string
	    required: true
	responses:
	  200:
	    description: Artist summary payload
	  500:
	    description: Artist data unavailable
	"""
	try:
		artist = _client().get_artist(browse_id)

		if not isinstance(artist, dict):
			return jsonify({"error": "Unexpected artist payload format"}), 500

		artist_name = artist.get("name")

		# Attempt to extract a playlistId for Top songs
		songs_section = artist.get("songs")
		playlist_id = None
		if isinstance(songs_section, dict):
			playlist_id = songs_section.get("playlistId")
			if not playlist_id:
				results = songs_section.get("results")
				if isinstance(results, list) and results:
					first = results[0]
					if isinstance(first, dict):
						playlist_id = first.get("playlistId")

		# Recommended artists (Fans might also like)
		related = artist.get("related")
		recommended_artists = []
		if isinstance(related, list):
			for item in related:
				if not isinstance(item, dict):
					continue
				name = item.get("title") or item.get("name")
				browse = item.get("browseId")
				thumbs = item.get("thumbnails")
				thumb_url = None
				if isinstance(thumbs, list) and thumbs:
					first_thumb = thumbs[0]
					if isinstance(first_thumb, dict):
						thumb_url = first_thumb.get("url")
				recommended_artists.append({
					"name": name,
					"browseId": browse,
					"thumbnail": thumb_url,
				})

		# Featured on playlists
		playlists_section = artist.get("playlists")
		featured_on_playlists = []
		featured_results = []
		if isinstance(playlists_section, dict):
			maybe_results = playlists_section.get("results")
			if isinstance(maybe_results, list):
				featured_results = maybe_results
		elif isinstance(playlists_section, list):
			featured_results = playlists_section

		for pl in featured_results:
			if not isinstance(pl, dict):
				continue
			title = pl.get("title")
			browse = pl.get("browseId") or pl.get("playlistId")
			thumbs = pl.get("thumbnails")
			thumb_url = None
			if isinstance(thumbs, list) and thumbs:
				first_thumb = thumbs[0]
				if isinstance(first_thumb, dict):
					thumb_url = first_thumb.get("url")
			featured_on_playlists.append({
				"title": title,
				"browseId": browse,
				"thumbnail": thumb_url,
			})

		payload = {
			"artistName": artist_name,
			"playlistId": playlist_id,
			"recommendedArtists": recommended_artists or None,
			"featuredOnPlaylists": featured_on_playlists or None,
		}
		return jsonify(payload)
	except Exception as e:
		return jsonify({"error": f"Artist data unavailable: {str(e)}"}), 500
