# YouTube Music API (Unofficial)

Flask wrapper around `ytmusicapi` exposing simple unauthenticated endpoints.

Docs: `/docs/` (Swagger UI) after running the server.

## Quick start

1. Create a virtualenv (optional)
2. Install deps:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the server (dev):
   ```bash
   python app.py
   ```
   - Server: http://localhost:8000
   - Docs: http://localhost:8000/docs/

For production, you can run with `waitress`:
```bash
waitress-serve --host=0.0.0.0 --port=8000 app:app
```

## Endpoints (prefix: `/api`)

- GET `/health` – health check
- GET `/search?q=...&filter=...&limit=...&official=...`
- GET `/search/suggestions?q=...`
- GET `/songs/{video_id}`
- GET `/albums/{browse_id}`
- GET `/artists/{browse_id}`
- GET `/playlists/{playlist_id}?limit=...`
- GET `/charts?country=..`
- GET `/moods`
- GET `/moods/{category_id}`
- GET `/watch_playlist?videoId=...|playlistId=...&radio=true|false&shuffle=true|false&limit=...`

Notes:
- This is unauthenticated; some actions are limited compared to logged-in YT Music.
- Refer to `ytmusicapi` docs for parameter semantics and response shapes.

## References
- ytmusicapi documentation: https://ytmusicapi.readthedocs.io/en/stable/
