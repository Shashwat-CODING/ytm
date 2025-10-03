from flask import Blueprint, current_app, jsonify, request
import requests

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


@bp_entities.get("/artist/<artist_id>")
def get_artist_summary(artist_id: str):
	"""Get artist summary via youtubei browse (Top songs, recommendations, featured-on)
	---
	parameters:
	  - name: artist_id
	    in: path
	    type: string
	    required: true
	  - name: country
	    in: query
	    type: string
	    required: false
	    default: US
	responses:
	  200:
	    description: Artist summary payload
	  500:
	    description: Artist data unavailable
	"""
	YOUTUBE_MUSIC_API_URL = "https://music.youtube.com/youtubei/v1/browse?prettyPrint=false"
	country = request.args.get("country", default="US", type=str)
	try:
		body = {
			"browseId": artist_id,
			"context": {
				"client": {
					"clientName": "WEB_REMIX",
					"clientVersion": "1.20250915.03.00",
					"gl": country,
				}
			}
		}
		resp = requests.post(
			YOUTUBE_MUSIC_API_URL,
			headers={"Content-Type": "application/json"},
			json=body,
			timeout=15,
		)
		if not resp.ok:
			return jsonify({"error": f"HTTP error: {resp.status_code}"}), 500
		data = resp.json()

		# Parse like the TS logic
		contents = (
			data.get("contents", {})
				.get("singleColumnBrowseResultsRenderer", {})
				.get("tabs", [])[0]
				.get("tabRenderer", {})
				.get("content", {})
				.get("sectionListRenderer", {})
				.get("contents", [])
		)

		artist_header = (
			data.get("header", {})
				.get("musicImmersiveHeaderRenderer", {})
				.get("title", {})
				.get("runs", [{}])[0]
				.get("text")
		)

		# Top songs shelf
		top_songs_shelf = None
		for item in contents:
			if isinstance(item, dict) and "musicShelfRenderer" in item:
				title_runs = (
					item["musicShelfRenderer"]
						.get("title", {})
						.get("runs", [{}])
				)
				if title_runs and title_runs[0].get("text") == "Top songs":
					top_songs_shelf = item["musicShelfRenderer"]
					break
		playlist_id = None
		if top_songs_shelf:
			try:
				playlist_id = (
					top_songs_shelf["contents"][0]
						["musicResponsiveListItemRenderer"]["flexColumns"][0]
						["musicResponsiveListItemFlexColumnRenderer"]["text"]["runs"][0]
						.get("navigationEndpoint", {})
						.get("watchEndpoint", {})
						.get("playlistId")
				)
			except Exception:
				playlist_id = None

		# Recommended artists
		recommended_artists = None
		for item in contents:
			if isinstance(item, dict) and "musicCarouselShelfRenderer" in item:
				header = (
					item["musicCarouselShelfRenderer"]["header"]
						.get("musicCarouselShelfBasicHeaderRenderer", {})
				)
				header_title = header.get("title", {}).get("runs", [{}])[0].get("text")
				if header_title == "Fans might also like":
					recommended_artists = []
					for it in item["musicCarouselShelfRenderer"].get("contents", []):
						two_row = it.get("musicTwoRowItemRenderer", {})
						recommended_artists.append({
							"name": two_row.get("title", {}).get("runs", [{}])[0].get("text"),
							"browseId": two_row.get("navigationEndpoint", {}).get("browseEndpoint", {}).get("browseId"),
							"thumbnail": two_row.get("thumbnailRenderer", {}).get("musicThumbnailRenderer", {}).get("thumbnail", {}).get("thumbnails", [{}])[0].get("url"),
						})
					break

		# Featured on
		featured_on_playlists = None
		for item in contents:
			if isinstance(item, dict) and "musicCarouselShelfRenderer" in item:
				header = (
					item["musicCarouselShelfRenderer"]["header"]
						.get("musicCarouselShelfBasicHeaderRenderer", {})
				)
				header_title = header.get("title", {}).get("runs", [{}])[0].get("text")
				if header_title == "Featured on":
					featured_on_playlists = []
					for it in item["musicCarouselShelfRenderer"].get("contents", []):
						two_row = it.get("musicTwoRowItemRenderer", {})
						featured_on_playlists.append({
							"title": two_row.get("title", {}).get("runs", [{}])[0].get("text"),
							"browseId": two_row.get("navigationEndpoint", {}).get("browseEndpoint", {}).get("browseId"),
							"thumbnail": two_row.get("thumbnailRenderer", {}).get("musicThumbnailRenderer", {}).get("thumbnail", {}).get("thumbnails", [{}])[0].get("url"),
						})
					break

		return jsonify({
			"artistName": artist_header,
			"playlistId": playlist_id,
			"recommendedArtists": recommended_artists,
			"featuredOnPlaylists": featured_on_playlists,
		})
	except Exception as e:
		return jsonify({"error": f"Artist data unavailable: {str(e)}"}), 500
