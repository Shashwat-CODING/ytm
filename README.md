# YouTube Music & YouTube API (Unofficial)

Flask wrapper around `ytmusicapi` and `youtube-search-python-fork` exposing simple unauthenticated endpoints for both YouTube Music and regular YouTube content.

**Base URL**: `https://ytm-jgmk.onrender.com`

**Interactive API Docs**: https://ytm-jgmk.onrender.com/docs/

## Quick Start

### Local Development

1. Create a virtualenv (optional)
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the server:
   ```bash
   python app.py
   ```
   - Server: http://localhost:8000
   - Docs: http://localhost:8000/docs/

### Production Deployment
```bash
waitress-serve --host=0.0.0.0 --port=8000 app:app
```

## API Endpoints

### Health Check
- **GET** `/health` - API health status

### YouTube Music API (via ytmusicapi)

#### Search
- **GET** `/api/search?q={query}&filter={filter}&limit={limit}`
  - Search YouTube Music content
  - **Filters**: `songs`, `videos`, `albums`, `artists`, `playlists`, `profiles`, `podcasts`, `episodes`, `community_playlists`
  - **Example**: `https://ytm-jgmk.onrender.com/api/search?q=oasis&filter=songs&limit=10`

- **GET** `/api/search/suggestions?q={query}`
  - Get search suggestions
  - **Example**: `https://ytm-jgmk.onrender.com/api/search/suggestions?q=oasi`

#### Content Details
- **GET** `/api/songs/{video_id}`
  - Get song details by video ID
  - **Example**: `https://ytm-jgmk.onrender.com/api/songs/ZuB1I4eY2vE`

- **GET** `/api/albums/{browse_id}`
  - Get album details and tracks
  - **Example**: `https://ytm-jgmk.onrender.com/api/albums/MPREb_DemoBrowseId`

- **GET** `/api/artists/{browse_id}`
  - Get artist information and releases
  - **Example**: `https://ytm-jgmk.onrender.com/api/artists/UC123ArtistBrowseId`

- **GET** `/api/playlists/{playlist_id}?limit={limit}`
  - Get playlist details and items
  - **Example**: `https://ytm-jgmk.onrender.com/api/playlists/PL123456789?limit=50`

#### Explore & Discovery
- **GET** `/api/charts?country={country}`
  - Get music charts (global or by country)
  - **Example**: `https://ytm-jgmk.onrender.com/api/charts?country=US`

- **GET** `/api/moods`
  - Get mood/genre categories
  - **Example**: `https://ytm-jgmk.onrender.com/api/moods`

- **GET** `/api/moods/{category_id}`
  - Get playlists for a mood/genre category
  - **Example**: `https://ytm-jgmk.onrender.com/api/moods/egVnKQ`

- **GET** `/api/watch_playlist?videoId={id}&radio={bool}&shuffle={bool}&limit={limit}`
  - Get watch playlist (radio/shuffle)
  - **Example**: `https://ytm-jgmk.onrender.com/api/watch_playlist?videoId=ZuB1I4eY2vE&radio=true&limit=25`

### YouTube API (via youtube-search-python-fork)

#### Search
- **GET** `/api/yt_search?q={query}&filter={filter}&limit={limit}`
  - Search YouTube content
  - **Filters**: `all`, `videos`, `channels`, `playlists`
  - **Example**: `https://ytm-jgmk.onrender.com/api/yt_search?q=music&filter=videos&limit=10`

#### Content Details
- **GET** `/api/yt_channel/{channel_id}`
  - Get YouTube channel information
  - **Example**: `https://ytm-jgmk.onrender.com/api/yt_channel/UC_x5XG1OV2P6uZZ5FSM9Ttw`

- **GET** `/api/yt_playlists?q={query}&limit={limit}`
  - Search YouTube playlists
  - **Example**: `https://ytm-jgmk.onrender.com/api/yt_playlists?q=music&limit=20`

## Usage Examples

### YouTube Music Search
```bash
# Search for songs
curl "https://ytm-jgmk.onrender.com/api/search?q=oasis&filter=songs&limit=5"

# Get search suggestions
curl "https://ytm-jgmk.onrender.com/api/search/suggestions?q=oasi"

# Get charts
curl "https://ytm-jgmk.onrender.com/api/charts?country=US"
```

### YouTube Search
```bash
# Search videos
curl "https://ytm-jgmk.onrender.com/api/yt_search?q=music&filter=videos&limit=5"

# Search channels
curl "https://ytm-jgmk.onrender.com/api/yt_search?q=tech&filter=channels&limit=3"

# Search playlists
curl "https://ytm-jgmk.onrender.com/api/yt_playlists?q=music&limit=10"
```

## Sample Responses (local run snapshots)

Note: These are abbreviated examples to illustrate the response shape. Fields may vary based on content and availability.

### Health
GET `/health`
```json
{ "status": "ok" }
```

### YouTube Music

GET `/api/search?q=music&filter=songs&limit=1`
```json
{
  "results": [
    {
      "resultType": "song",
      "title": "Rain Sound (Pure White Noise for Natural Deep Sleep Inducing)",
      "videoId": "13EL6Mgeocc",
      "duration": "3:20:01",
      "duration_seconds": 12001,
      "artists": [
        { "id": "UCo5JkRVziPY8hl5VCpukMkQ", "name": "White Noise Masters" },
        { "id": "UC0VD-Sorq2XpUagaoemRAMA", "name": "Deep Sleep" }
      ],
      "album": {
        "id": "MPREb_k9b0KESuAJF",
        "name": "Rain Sound 200 Minutes for Deep Sleep Inducing – White Noise..."
      },
      "thumbnails": [ { "url": "https://lh3.googleusercontent.com/...", "width": 60, "height": 60 } ]
    }
  ]
}
```

GET `/api/search/suggestions?q=music`
```json
{ "suggestions": ["music", "music to watch boys to", "sleeping music"] }
```

GET `/api/songs/{video_id}` (example: `13EL6Mgeocc`)
```json
{
  "videoDetails": {
    "videoId": "13EL6Mgeocc",
    "title": "Rain Sound (Pure White Noise for Natural Deep Sleep Inducing)",
    "author": "White Noise Masters - Topic",
    "lengthSeconds": "12001"
  },
  "microformat": { "microformatDataRenderer": { "appName": "YouTube Music" } }
}
```

GET `/api/albums/{browse_id}` (example: `MPREb_k9b0KESuAJF`)
```json
{
  "title": "Rain Sound 200 Minutes for Deep Sleep Inducing – White Noise...",
  "artists": [{ "id": "UCo5JkRVziPY8hl5VCpukMkQ", "name": "White Noise Masters" }],
  "tracks": [ { "videoId": "13EL6Mgeocc", "title": "Rain Sound ...", "length": "3:20:01" } ]
}
```

GET `/api/artists/{browse_id}` (example: `UCyX0TcJ20FifnGP3M6J-IXQ`)
```json
{
  "name": "Meditation Music",
  "songs": { "results": [ { "videoId": "...", "title": "..." } ] },
  "albums": { "results": [ { "browseId": "...", "title": "..." } ] }
}
```

GET `/api/playlists/{playlist_id}?limit=5`
```json
{
  "id": "RDCLAK5uy_nDL8KeBrUagwyISwNmyEiSfYgz1gVCesg",
  "title": "Mellow Pop Classics",
  "author": "YouTube Music",
  "tracks": [ { "videoId": "...", "title": "...", "artists": [ { "name": "..." } ] } ]
}
```

GET `/api/charts?country=US`
```json
{
  "error": "Charts data unavailable: Charts service temporarily unavailable",
  "message": "YouTube Music charts are currently not accessible. This may be due to regional restrictions or service limitations.",
  "fallback": "Try using the search endpoint instead: /api/search?q=trending&filter=songs"
}
```

GET `/api/moods`
```json
{
  "Genres": [ { "title": "African", "params": "ggMPOg1uX0..." }, { "title": "Arabic" } ],
  "Moods & moments": [ { "title": "Chill", "params": "ggMPOg1uX1..." }, { "title": "Sleep" } ]
}
```

GET `/api/moods/{category_id}` (example: Chill category param)
```json
[
  {
    "title": "Coffee Shop Blend",
    "description": "Playlist • YouTube Music",
    "playlistId": "RDCLAK5uy_nBE4bLuBHUXWZrF59ZrkPEToKt8M_I3Vc",
    "thumbnails": [ { "url": "https://lh3.googleusercontent.com/...", "width": 226, "height": 226 } ]
  }
]
```

GET `/api/watch_playlist?videoId=13EL6Mgeocc&radio=true&limit=3`
```json
{
  "tracks": [ { "videoId": "...", "title": "...", "length": "..." } ],
  "related": true
}
```

### YouTube

GET `/api/yt_search?q=music&filter=videos&limit=1`
```json
{
  "query": "music",
  "filter": "videos",
  "results": [ { "title": "Shaky (Official Video) ...", "channel": { "name": "..." }, "duration": "3 minutes, 35 seconds" } ]
}
```

GET `/api/yt_channel/{channel_id}` (example: `UC_x5XG1OV2P6uZZ5FSM9Ttw`)
```json
{
  "channel_id": "UC_x5XG1OV2P6uZZ5FSM9Ttw",
  "channel_info": { "title": "Google for Developers", "subscribers": "...", "link": "https://www.youtube.com/..." }
}
```

GET `/api/yt_playlists?q=music&limit=1`
```json
{
  "query": "music",
  "playlists": [ { "title": "...", "playlistId": "PL...", "channel": { "name": "..." } } ]
}
```

### Standard Error Response
```json
{ "error": "Human-readable error message" }
```

## Rate Limits & Notes

- **Unauthenticated Access**: This API uses unauthenticated access, so some features may be limited compared to logged-in YouTube Music
- **Rate Limits**: No explicit rate limits, but please use responsibly
- **Data Source**: YouTube Music data via `ytmusicapi`, YouTube data via `youtube-search-python-fork`

## References

- **ytmusicapi documentation**: https://ytmusicapi.readthedocs.io/en/stable/
- **youtube-search-python-fork**: https://github.com/ahmedayyad-dev/youtube-search-python-fork
- **Interactive API Docs**: https://ytm-jgmk.onrender.com/docs/
