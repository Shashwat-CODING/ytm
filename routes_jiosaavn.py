from flask import Blueprint, jsonify, request
import requests
from jiosaavn_helpers import create_song_payload, normalize_string
from typing import Dict, Any, List

bp_jiosaavn = Blueprint("jiosaavn", __name__)


@bp_jiosaavn.get("/jiosaavn/search")
def jiosaavn_search():
    """Search for music on JioSaavn
    ---
    parameters:
      - name: title
        in: query
        type: string
        required: true
        description: Song title
      - name: artist
        in: query
        type: string
        required: true
        description: Artist name
    responses:
      200:
        description: Song information with download URL
      400:
        description: Missing title or artist parameters
      404:
        description: Music stream not found
      500:
        description: Internal server error
    """
    title = request.args.get("title", type=str)
    artist = request.args.get("artist", type=str)
    
    if not title or not artist:
        return jsonify({"error": "Missing title or artist parameters"}), 400
    
    # Construct JioSaavn API URL
    search_query = f"{title} {artist}"
    jiosaavn_api_url = (
        f"https://www.jiosaavn.com/api.php"
        f"?_format=json"
        f"&_marker=0"
        f"&api_version=4"
        f"&ctx=web6dot0"
        f"&__call=search.getResults"
        f"&q={requests.utils.quote(search_query)}"
        f"&p=0"
        f"&n=10"
    )
    
    try:
        response = requests.get(jiosaavn_api_url, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36'
        }, timeout=15)
        
        if not response.ok:
            return jsonify({
                "error": f"JioSaavn API returned {response.status_code}: {response.text[:200]}"
            }), 500
        
        data = response.json()
        
        if not data.get('results') or len(data['results']) == 0:
            return jsonify({"error": "Music stream not found in JioSaavn results"}), 404
        
        # Process results
        processed_results = [create_song_payload(raw_song) for raw_song in data['results']]
        
        # Find matching track
        matching_track = None
        for track in processed_results:
            # Get all artist names
            primary_artists = [artist['name'].strip() for artist in track['artists']['primary']] if track['artists']['primary'] else []
            singers = [artist['name'].strip() for artist in track['artists']['all'] if artist.get('role') == 'singer'] if track['artists']['all'] else []
            all_artists = primary_artists + singers
            
            # Check if artist matches
            artist_matches = any(
                normalize_string(artist).lower().startswith(normalize_string(track_artist_name).lower())
                for track_artist_name in all_artists
            )
            
            # Check if title matches
            title_matches = normalize_string(title).lower().startswith(normalize_string(track['name']).lower())
            
            if title_matches and artist_matches:
                matching_track = track
                break
        
        if not matching_track:
            return jsonify({"error": "Music stream not found in JioSaavn results"}), 404
        
        # Create final response
        final_response = {
            "name": matching_track['name'],
            "year": matching_track['year'],
            "copyright": matching_track['copyright'],
            "duration": matching_track['duration'],
            "label": matching_track['label'],
            "albumName": matching_track['album']['name'] if matching_track['album'] else None,
            "artists": [
                *(matching_track['artists']['primary'] or []),
                *(matching_track['artists']['featured'] or []),
                *(matching_track['artists']['all'] or [])
            ],
            "downloadUrl": matching_track['downloadUrl']
        }
        
        return jsonify(final_response)
        
    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Network error: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500


@bp_jiosaavn.get("/jiosaavn/search/all")
def jiosaavn_search_all():
    """Search for all music results on JioSaavn
    ---
    parameters:
      - name: q
        in: query
        type: string
        required: true
        description: Search query
      - name: limit
        in: query
        type: integer
        required: false
        default: 10
        description: Number of results to return
    responses:
      200:
        description: List of all matching songs
      400:
        description: Missing query parameter
      500:
        description: Internal server error
    """
    query = request.args.get("q", type=str)
    limit = request.args.get("limit", default=10, type=int)
    
    if not query:
        return jsonify({"error": "Missing query parameter 'q'"}), 400
    
    # Construct JioSaavn API URL
    jiosaavn_api_url = (
        f"https://www.jiosaavn.com/api.php"
        f"?_format=json"
        f"&_marker=0"
        f"&api_version=4"
        f"&ctx=web6dot0"
        f"&__call=search.getResults"
        f"&q={requests.utils.quote(query)}"
        f"&p=0"
        f"&n={limit}"
    )
    
    try:
        response = requests.get(jiosaavn_api_url, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36'
        }, timeout=15)
        
        if not response.ok:
            return jsonify({
                "error": f"JioSaavn API returned {response.status_code}: {response.text[:200]}"
            }), 500
        
        data = response.json()
        
        if not data.get('results') or len(data['results']) == 0:
            return jsonify({"results": []})
        
        # Process all results
        processed_results = [create_song_payload(raw_song) for raw_song in data['results']]
        
        return jsonify({
            "query": query,
            "total": len(processed_results),
            "results": processed_results
        })
        
    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Network error: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500
