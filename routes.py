from flask import Blueprint, current_app, jsonify, request
from typing import Optional
import requests
import json

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


def _get_youtube_suggestions(query: str) -> list:
	"""Get search suggestions from YouTube's internal API"""
	try:
		# YouTube's internal suggestions API
		url = "https://suggestqueries-clients6.youtube.com/complete/search"
		params = {
			"ds": "yt",
			"hl": "en",
			"gl": "in", 
			"client": "youtube",
			"gs_ri": "youtube",
			"sugexp": "yrpeb_p,ytpso.bo.rwjb=50,ytpso.bo.rlcft=0.01",
			"tok": "cmbVoqd59wmnnS3CDslsDQ",
			"h": "180",
			"w": "320",
			"ytvs": "1",
			"gs_id": "1",
			"q": query,
			"cp": "1"
		}
		
		headers = {
			"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36",
			"Accept": "*/*",
			"Accept-Language": "en-US,en;q=0.9",
			"Accept-Encoding": "gzip, deflate, br",
			"Referer": "https://www.youtube.com/",
			"Origin": "https://www.youtube.com"
		}
		
		response = requests.get(url, params=params, headers=headers, timeout=10)
		response.raise_for_status()
		
		# Parse the JSONP response
		content = response.text
		
		# Remove the callback wrapper (e.g., "window.google.ac.h(" and ");")
		if content.startswith("window.google.ac.h(") and content.endswith(");"):
			content = content[20:-2]
		elif content.startswith("window.google.ac.s(") and content.endswith(");"):
			content = content[20:-2]
		else:
			# Try to find the start and end of the JSON
			start_idx = content.find('(')
			end_idx = content.rfind(')')
			if start_idx != -1 and end_idx != -1:
				content = content[start_idx + 1:end_idx]
		
		data = json.loads(content)
		
		# Extract suggestions from the response
		# The response format is: [query, [[suggestion, 0, [512]], ...], {}, {}]
		if len(data) >= 2 and isinstance(data[1], list):
			suggestions = []
			for item in data[1]:
				if isinstance(item, list) and len(item) > 0:
					suggestions.append(item[0])  # First element is the suggestion text
			return suggestions
		
		return []
		
	except Exception as e:
		# Log the error but don't fail completely
		print(f"Error getting YouTube suggestions: {e}")
		return []


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

	if flt and flt not in ALLOWED_FILTERS:
		return jsonify({"error": f"Invalid filter. Allowed: {sorted(list(ALLOWED_FILTERS))}"}), 400

	try:
		results = _client().search(query, filter=flt, limit=limit, ignore_spelling=False)
		return jsonify({"results": results})
	except Exception as e:
		return jsonify({"error": f"Search failed: {str(e)}"}), 500


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
	  - name: music
	    in: query
	    type: integer
	    required: false
	    description: If 1, get suggestions from YouTube Music. If not present or 0, get suggestions from YouTube
	responses:
	  200:
	    description: Suggestions
	  400:
	    description: Missing/invalid params
	"""
	query = request.args.get("q", type=str)
	if not query:
		return jsonify({"error": "Missing required query parameter 'q'"}), 400

	music = request.args.get("music", type=int)
	
	try:
		if music == 1:
			# Get suggestions from YouTube Music
			sugs = _client().get_search_suggestions(query)
			return jsonify({"suggestions": sugs, "source": "youtube_music"})
		else:
			# Get suggestions from YouTube
			sugs = _get_youtube_suggestions(query)
			return jsonify({"suggestions": sugs, "source": "youtube"})
	except Exception as e:
		return jsonify({"error": f"Suggestions failed: {str(e)}"}), 500
