from flask import Blueprint, jsonify, request
import requests
from jiosaavn_helpers import create_song_payload, normalize_string
from typing import Dict, Any, List

bp_jiosaavn = Blueprint("jiosaavn", __name__)


def _try_jiosaavn_fallback(title: str, artist: str):
    """Try alternative JioSaavn API endpoints"""
    print(f"Trying fallback for: {title} by {artist}")
    
    # Try different API endpoints
    fallback_urls = [
        f"https://www.jiosaavn.com/api.php?_format=json&_marker=0&api_version=4&ctx=web6dot0&__call=search.getResults&q={requests.utils.quote(f'{title} {artist}')}&p=0&n=5",
        f"https://www.jiosaavn.com/api.php?_format=json&_marker=0&api_version=4&ctx=web6dot0&__call=search.getResults&q={requests.utils.quote(title)}&p=0&n=5",
        f"https://www.jiosaavn.com/api.php?_format=json&_marker=0&api_version=4&ctx=web6dot0&__call=search.getResults&q={requests.utils.quote(artist)}&p=0&n=5"
    ]
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36'
    }
    
    for url in fallback_urls:
        try:
            print(f"Trying fallback URL: {url}")
            response = requests.get(url, headers=headers, timeout=10)
            if response.ok:
                data = response.json()
                if data.get('results') and len(data['results']) > 0:
                    print(f"Fallback found {len(data['results'])} results")
                    processed_results = [create_song_payload(raw_song) for raw_song in data['results']]
                    
                    # Try to find a match
                    for track in processed_results:
                        primary_artists = [artist['name'].strip() for artist in track['artists']['primary']] if track['artists']['primary'] else []
                        singers = [artist['name'].strip() for artist in track['artists']['all'] if artist.get('role') == 'singer'] if track['artists']['all'] else []
                        all_artists = primary_artists + singers
                        
                        artist_matches = any(
                            normalize_string(artist).lower().startswith(normalize_string(track_artist_name).lower())
                            for track_artist_name in all_artists
                        )
                        
                        title_matches = normalize_string(title).lower().startswith(normalize_string(track['name']).lower())
                        
                        if title_matches and artist_matches:
                            final_response = {
                                "name": track['name'],
                                "year": track['year'],
                                "copyright": track['copyright'],
                                "duration": track['duration'],
                                "label": track['label'],
                                "albumName": track['album']['name'] if track['album'] else None,
                                "artists": [
                                    *(track['artists']['primary'] or []),
                                    *(track['artists']['featured'] or []),
                                    *(track['artists']['all'] or [])
                                ],
                                "downloadUrl": track['downloadUrl']
                            }
                            return jsonify(final_response)
        except Exception as e:
            print(f"Fallback URL failed: {e}")
            continue
    
    # If all fallbacks fail, return a generic response
    return jsonify({
        "error": "Music stream not found in JioSaavn results",
        "message": "Unable to find the requested song. This might be due to server restrictions or the song not being available on JioSaavn.",
        "suggestion": "Try searching with different keywords or check if the song is available on other platforms."
    }), 404


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
        print(f"Making request to JioSaavn API: {jiosaavn_api_url}")
        response = requests.get(jiosaavn_api_url, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36'
        }, timeout=15)
        
        print(f"JioSaavn API Response - Status: {response.status_code}, Length: {len(response.text)}")
        
        if not response.ok:
            print(f"JioSaavn API Error - Status: {response.status_code}, Response: {response.text[:200]}")
            return jsonify({
                "error": f"JioSaavn API returned {response.status_code}: {response.text[:200]}"
            }), 500
        
        data = response.json()
        print(f"JioSaavn API Data - Results count: {len(data.get('results', []))}")
        
        if not data.get('results') or len(data['results']) == 0:
            print("No results found in JioSaavn API response, trying fallback...")
            return _try_jiosaavn_fallback(title, artist)
        
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
            print("No matching track found in main results, trying fallback...")
            return _try_jiosaavn_fallback(title, artist)
        
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
        print(f"Network error: {e}")
        return _try_jiosaavn_fallback(title, artist)
    except Exception as e:
        print(f"Internal server error: {e}")
        return _try_jiosaavn_fallback(title, artist)


@bp_jiosaavn.get("/jiosaavn/debug")
def jiosaavn_debug():
    """Debug endpoint to test JioSaavn API directly"""
    title = request.args.get("title", type=str)
    artist = request.args.get("artist", type=str)
    
    if not title or not artist:
        return jsonify({"error": "Missing title or artist parameters"}), 400
    
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
        f"&n=5"
    )
    
    try:
        print(f"Debug - Making request to JioSaavn API: {jiosaavn_api_url}")
        response = requests.get(jiosaavn_api_url, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36'
        }, timeout=15)
        
        print(f"Debug - JioSaavn API Response - Status: {response.status_code}, Length: {len(response.text)}")
        
        if not response.ok:
            return jsonify({
                "error": f"JioSaavn API returned {response.status_code}",
                "response_text": response.text[:500],
                "url": jiosaavn_api_url
            }), 500
        
        data = response.json()
        
        return jsonify({
            "query": search_query,
            "url": jiosaavn_api_url,
            "status_code": response.status_code,
            "response_length": len(response.text),
            "results_count": len(data.get('results', [])),
            "raw_data": data,
            "processed_results": [create_song_payload(raw_song) for raw_song in data.get('results', [])]
        })
        
    except Exception as e:
        return jsonify({
            "error": f"Debug failed: {str(e)}",
            "url": jiosaavn_api_url
        }), 500


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
