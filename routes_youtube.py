from flask import Blueprint, current_app, jsonify, request
from youtubesearchpython import VideosSearch, ChannelsSearch, PlaylistsSearch
from typing import Optional

bp_youtube = Blueprint("youtube", __name__)

# YouTube search filters
YT_FILTERS = {
    "all",
    "channels", 
    "playlists",
    "videos"
}

@bp_youtube.get("/yt_search")
def youtube_search():
    """Search YouTube
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
        enum: [all, channels, playlists, videos]
        default: all
        description: Filter results by type
      - name: limit
        in: query
        type: integer
        required: false
        default: 20
        description: Maximum number of results
    responses:
      200:
        description: YouTube search results
      400:
        description: Missing/invalid params
    """
    query = request.args.get("q", type=str)
    if not query:
        return jsonify({"error": "Missing required query parameter 'q'"}), 400

    flt: str = request.args.get("filter", default="all", type=str)
    limit: int = request.args.get("limit", default=20, type=int)

    if flt not in YT_FILTERS:
        return jsonify({"error": f"Invalid filter. Allowed: {sorted(list(YT_FILTERS))}"}), 400

    try:
        results = []
        
        if flt == "videos" or flt == "all":
            videos_search = VideosSearch(query, limit=limit)
            video_results = videos_search.result()
            results.extend(video_results.get("result", []))
        
        if flt == "channels" or flt == "all":
            channels_search = ChannelsSearch(query, limit=limit)
            channel_results = channels_search.result()
            results.extend(channel_results.get("result", []))
        
        if flt == "playlists" or flt == "all":
            playlists_search = PlaylistsSearch(query, limit=limit)
            playlist_results = playlists_search.result()
            results.extend(playlist_results.get("result", []))
        
        return jsonify({
            "query": query,
            "filter": flt,
            "results": results
        })
    except Exception as e:
        return jsonify({"error": f"Search failed: {str(e)}"}), 500

@bp_youtube.get("/yt_channel/<channel_id>")
def youtube_channel(channel_id: str):
    """Get YouTube channel information
    ---
    parameters:
      - name: channel_id
        in: path
        type: string
        required: true
        description: YouTube channel ID
    responses:
      200:
        description: Channel information
      400:
        description: Invalid channel ID
    """
    try:
        # Get channel info using search
        channels_search = ChannelsSearch(f"channel:{channel_id}", limit=1)
        results = channels_search.result()
        channel_results = results.get("result", [])
        
        if not channel_results:
            return jsonify({"error": "Channel not found"}), 404
            
        return jsonify({
            "channel_id": channel_id,
            "channel_info": channel_results[0]
        })
    except Exception as e:
        return jsonify({"error": f"Failed to get channel info: {str(e)}"}), 500

@bp_youtube.get("/yt_playlists")
def youtube_playlists():
    """Search YouTube playlists
    ---
    parameters:
      - name: q
        in: query
        type: string
        required: true
        description: Search query for playlists
      - name: limit
        in: query
        type: integer
        required: false
        default: 20
        description: Maximum number of playlists
    responses:
      200:
        description: YouTube playlists
      400:
        description: Missing/invalid params
    """
    query = request.args.get("q", type=str)
    if not query:
        return jsonify({"error": "Missing required query parameter 'q'"}), 400

    limit: int = request.args.get("limit", default=20, type=int)

    try:
        playlists_search = PlaylistsSearch(query, limit=limit)
        results = playlists_search.result()
        playlist_results = results.get("result", [])
        
        return jsonify({
            "query": query,
            "playlists": playlist_results
        })
    except Exception as e:
        return jsonify({"error": f"Failed to search playlists: {str(e)}"}), 500
