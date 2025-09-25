from flask import Blueprint, current_app, jsonify, request
from typing import Optional

bp = Blueprint("api", __name__)


ALLOWED_FILTERS = {
	"songs",
	"videos",
	"albums",
	"artists",
	"playlists",
	"profiles",
	"podcasts",
	"episodes",
	"community_playlists",
}


def _client():
	return current_app.config["YTMUSIC_CLIENT"]


@bp.get("/search")
def search():
	"""Search YouTube Music
	---
	parameters:
	  - name: q
	    in: query
	    type: string
	    required: true
	    description: Search query string
	  - name: filter
	    in: query
	    type: string
	    required: false
	    enum: [songs, videos, albums, artists, playlists, profiles, podcasts, episodes, community_playlists]
	    description: Restrict results to a specific type
	  - name: limit
	    in: query
	    type: integer
	    required: false
	    default: 25
	    description: Maximum number of results
	  - name: official
	    in: query
	    type: boolean
	    required: false
	    description: Prefer official music videos when filter=videos
	responses:
	  200:
	    description: Search results
	  400:
	    description: Missing/invalid params
	"""
	query = request.args.get("q", type=str)
	if not query:
		return jsonify({"error": "Missing required query parameter 'q'"}), 400

	flt: Optional[str] = request.args.get("filter", type=str)
	limit: int = request.args.get("limit", default=25, type=int)
	official: Optional[bool] = request.args.get("official", default=None, type=lambda v: v.lower() == "true")

	if flt and flt not in ALLOWED_FILTERS:
		return jsonify({"error": f"Invalid filter. Allowed: {sorted(list(ALLOWED_FILTERS))}"}), 400

	results = _client().search(query, filter=flt, limit=limit, ignore_spelling=False, official_music_video=official)
	return jsonify({"results": results})


@bp.get("/search/suggestions")
def suggestions():
	"""Get search suggestions
	---
	parameters:
	  - name: q
	    in: query
	    type: string
	    required: true
	    description: Partial query to get suggestions for
	responses:
	  200:
	    description: Suggestions
	  400:
	    description: Missing/invalid params
	"""
	query = request.args.get("q", type=str)
	if not query:
		return jsonify({"error": "Missing required query parameter 'q'"}), 400

	sugs = _client().get_search_suggestions(query)
	return jsonify({"suggestions": sugs})
