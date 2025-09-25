from flask import Blueprint, current_app, jsonify, request

bp_explore = Blueprint("explore", __name__)


def _client():
	return current_app.config["YTMUSIC_CLIENT"]


@bp_explore.get("/charts")
def charts():
	"""Get charts (global or by country)
	---
	parameters:
	  - name: country
	    in: query
	    type: string
	    required: false
	responses:
	  200:
	    description: Charts data
	  500:
	    description: Charts data unavailable
	"""
	country = request.args.get("country", default=None, type=str)
	try:
		data = _client().get_charts(country=country)
		return jsonify(data)
	except Exception as e:
		return jsonify({"error": f"Charts data unavailable: {str(e)}"}), 500


@bp_explore.get("/moods")
def moods():
	"""Get mood/genre categories
	---
	responses:
	  200:
	    description: Mood categories
	  500:
	    description: Mood categories unavailable
	"""
	try:
		data = _client().get_mood_categories()
		return jsonify(data)
	except Exception as e:
		return jsonify({"error": f"Mood categories unavailable: {str(e)}"}), 500


@bp_explore.get("/moods/<category_id>")
def moods_playlists(category_id: str):
	"""Get playlists for a mood/genre category
	---
	parameters:
	  - name: category_id
	    in: path
	    type: string
	    required: true
	responses:
	  200:
	    description: Mood playlists
	  500:
	    description: Mood playlists unavailable
	"""
	try:
		data = _client().get_mood_playlists(category_id)
		return jsonify(data)
	except Exception as e:
		return jsonify({"error": f"Mood playlists unavailable: {str(e)}"}), 500


@bp_explore.get("/watch_playlist")
def watch_playlist():
	"""Get watch playlist (radio/shuffle)
	---
	parameters:
	  - name: videoId
	    in: query
	    type: string
	    required: false
	  - name: playlistId
	    in: query
	    type: string
	    required: false
	  - name: radio
	    in: query
	    type: boolean
	    required: false
	    default: false
	  - name: shuffle
	    in: query
	    type: boolean
	    required: false
	    default: false
	  - name: limit
	    in: query
	    type: integer
	    required: false
	    default: 25
	responses:
	  200:
	    description: Watch playlist data
	  400:
	    description: Missing params
	"""
	video_id = request.args.get("videoId")
	playlist_id = request.args.get("playlistId")
	radio = request.args.get("radio", default=False, type=lambda v: v.lower() == "true")
	shuffle = request.args.get("shuffle", default=False, type=lambda v: v.lower() == "true")
	limit = request.args.get("limit", default=25, type=int)
	if not video_id and not playlist_id:
		return jsonify({"error": "Provide either videoId or playlistId"}), 400
	try:
		data = _client().get_watch_playlist(videoId=video_id, playlistId=playlist_id, radio=radio, shuffle=shuffle, limit=limit)
		return jsonify(data)
	except Exception as e:
		return jsonify({"error": f"Watch playlist unavailable: {str(e)}"}), 500
