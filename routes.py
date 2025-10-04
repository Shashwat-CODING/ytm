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


def _get_youtube_suggestions_fallback(query: str) -> list:
	"""Fallback method using a different approach"""
	try:
		# Try multiple fallback endpoints
		endpoints = [
			{
				"url": "https://clients1.google.com/complete/search",
				"params": {
					"client": "youtube",
					"hl": "en",
					"gl": "in",
					"q": query,
					"callback": "google.sbox.p50"
				}
			},
			{
				"url": "https://suggestqueries-clients6.youtube.com/complete/search",
				"params": {
					"ds": "yt",
					"hl": "en",
					"gl": "in",
					"client": "youtube",
					"q": query
				}
			}
		]
		
		headers = {
			"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
			"Accept": "*/*",
			"Referer": "https://www.youtube.com/"
		}
		
		for endpoint in endpoints:
			try:
				response = requests.get(endpoint["url"], params=endpoint["params"], headers=headers, timeout=10)
				if response.status_code == 200:
					content = response.text
					
					# Handle different callback formats
					if content.startswith("google.sbox.p50(") and content.endswith(");"):
						content = content[16:-2]
					elif content.startswith("window.google.ac.h(") and content.endswith(");"):
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
					if len(data) >= 2 and isinstance(data[1], list):
						suggestions = []
						for item in data[1]:
							if isinstance(item, list) and len(item) > 0:
								suggestions.append(item[0])
							elif isinstance(item, str):
								suggestions.append(item)
						
						if suggestions:
							print(f"Fallback API returned {len(suggestions)} suggestions")
							return suggestions[:10]  # Limit to 10 suggestions
			except Exception as e:
				print(f"Fallback endpoint failed: {e}")
				continue
		
		# If all APIs fail, return basic suggestions based on query
		return _get_static_suggestions(query)
	except:
		return _get_static_suggestions(query)


def _get_static_suggestions(query: str) -> list:
	"""Static fallback suggestions for common queries"""
	query_lower = query.lower()
	
	# Common suggestion patterns
	suggestions_map = {
		"music": ["music", "music video", "music song", "music 2024", "music playlist"],
		"video": ["video", "video song", "video 2024", "video download", "video editing"],
		"movie": ["movie", "movie trailer", "movie song", "movie review", "movie 2024"],
		"song": ["song", "song 2024", "song download", "song lyrics", "song video"],
		"dance": ["dance", "dance video", "dance song", "dance tutorial", "dance 2024"],
		"comedy": ["comedy", "comedy video", "comedy show", "comedy movie", "comedy 2024"],
		"tutorial": ["tutorial", "tutorial video", "tutorial 2024", "tutorial hindi", "tutorial english"],
		"news": ["news", "news today", "news 2024", "news hindi", "news english"],
		"cooking": ["cooking", "cooking video", "cooking recipe", "cooking tutorial", "cooking 2024"],
		"fitness": ["fitness", "fitness video", "fitness workout", "fitness tips", "fitness 2024"]
	}
	
	# Check for exact matches first
	if query_lower in suggestions_map:
		return suggestions_map[query_lower]
	
	# Check for partial matches
	for key, suggestions in suggestions_map.items():
		if key in query_lower or query_lower in key:
			return suggestions
	
	# Default generic suggestions
	return [query, f"{query} video", f"{query} 2024", f"{query} tutorial", f"{query} song"]


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
		
		# Use a more generic user agent that's less likely to be blocked
		# Remove Accept-Encoding to avoid compression issues on server
		headers = {
			"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
			"Accept": "*/*",
			"Accept-Language": "en-US,en;q=0.9",
			"Referer": "https://www.youtube.com/",
			"Origin": "https://www.youtube.com",
			"Cache-Control": "no-cache",
			"Pragma": "no-cache"
		}
		
		response = requests.get(url, params=params, headers=headers, timeout=15)
		
		# Log response details for debugging
		print(f"YouTube API Response - Status: {response.status_code}, Length: {len(response.text)}")
		
		if response.status_code != 200:
			print(f"YouTube API Error - Status: {response.status_code}, Response: {response.text[:200]}")
			return []
		
		# Parse the JSONP response
		content = response.text
		
		# Check if response is empty or invalid
		if not content or len(content) < 10:
			print(f"YouTube API returned empty/invalid response: {content}")
			return []
		
		# Check if content looks like binary/compressed data
		if any(ord(c) < 32 and c not in '\t\n\r' for c in content[:50]):
			print(f"YouTube API returned binary/compressed data, trying fallback...")
			return _get_youtube_suggestions_fallback(query)
		
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
			else:
				print(f"Could not parse YouTube API response: {content[:100]}...")
				return []
		
		data = json.loads(content)
		
		# Extract suggestions from the response
		# The response format is: [query, [[suggestion, 0, [512]], ...], {}, {}]
		if len(data) >= 2 and isinstance(data[1], list):
			suggestions = []
			for item in data[1]:
				if isinstance(item, list) and len(item) > 0:
					suggestions.append(item[0])  # First element is the suggestion text
			print(f"YouTube API returned {len(suggestions)} suggestions")
			return suggestions
		
		print(f"YouTube API response format unexpected: {data}")
		# Try fallback method
		print("Trying fallback method...")
		return _get_youtube_suggestions_fallback(query)
		
	except requests.exceptions.RequestException as e:
		print(f"Network error getting YouTube suggestions: {e}")
		# Try fallback method
		print("Trying fallback method...")
		return _get_youtube_suggestions_fallback(query)
	except json.JSONDecodeError as e:
		print(f"JSON decode error getting YouTube suggestions: {e}")
		# Try fallback method
		print("Trying fallback method...")
		return _get_youtube_suggestions_fallback(query)
	except Exception as e:
		# Log the error but don't fail completely
		print(f"Unexpected error getting YouTube suggestions: {e}")
		# Try fallback method
		print("Trying fallback method...")
		return _get_youtube_suggestions_fallback(query)


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


@bp.get("/search/suggestions/debug")
def suggestions_debug():
	"""Debug endpoint to test YouTube suggestions API directly"""
	query = request.args.get("q", type=str)
	if not query:
		return jsonify({"error": "Missing required query parameter 'q'"}), 400
	
	try:
		# Test the YouTube suggestions function directly
		suggestions = _get_youtube_suggestions(query)
		return jsonify({
			"query": query,
			"suggestions": suggestions,
			"count": len(suggestions),
			"source": "youtube_debug"
		})
	except Exception as e:
		return jsonify({
			"error": f"Debug failed: {str(e)}",
			"query": query
		}), 500


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
