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

## Response Format

All endpoints return JSON responses with the following structure:

### Success Response
```json
{
  "results": [...],
  "query": "search_term",
  "filter": "songs"
}
```

### Error Response
```json
{
  "error": "Error message",
  "detail": "Additional error details"
}
```

## Rate Limits & Notes

- **Unauthenticated Access**: This API uses unauthenticated access, so some features may be limited compared to logged-in YouTube Music
- **Rate Limits**: No explicit rate limits, but please use responsibly
- **Data Source**: YouTube Music data via `ytmusicapi`, YouTube data via `youtube-search-python-fork`

## References

- **ytmusicapi documentation**: https://ytmusicapi.readthedocs.io/en/stable/
- **youtube-search-python-fork**: https://github.com/ahmedayyad-dev/youtube-search-python-fork
- **Interactive API Docs**: https://ytm-jgmk.onrender.com/docs/
