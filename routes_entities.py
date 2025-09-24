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
	"""
	data = _client().get_song(video_id)
	return jsonify(data)


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
	"""
	data = _client().get_album(browse_id)
	return jsonify(data)


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
	"""
	data = _client().get_artist(browse_id)
	return jsonify(data)


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
	"""
	limit = request.args.get("limit", default=100, type=int)
	data = _client().get_playlist(playlist_id, limit=limit)
	return jsonify(data)
