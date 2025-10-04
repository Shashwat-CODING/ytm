import base64
import re
from typing import List, Dict, Any, Optional
from Crypto.Cipher import DES


def create_download_links(encrypted_media_url: str) -> Optional[str]:
    """Create download links from encrypted media URL"""
    if not encrypted_media_url:
        return None
    
    try:
        key = '38346591'
        iv = '00000000'
        
        # Decode base64
        encrypted = base64.b64decode(encrypted_media_url)
        
        # Create DES cipher
        cipher = DES.new(key.encode(), DES.MODE_ECB)
        
        # Decrypt
        decrypted_link = cipher.decrypt(encrypted).decode('utf-8', errors='ignore')
        
        # Clean up the URL - remove null bytes and non-printable characters
        cleaned_link = ''.join(char for char in decrypted_link if 32 <= ord(char) < 127)
        
        # Remove any trailing characters that aren't part of the URL
        if '.' in cleaned_link:
            # Split by '.' and take everything up to the last valid file extension
            parts = cleaned_link.split('.')
            if len(parts) >= 2 and parts[-1].lower() in ['mp4', 'mp3', 'webm', 'm4a', 'opus']:
                cleaned_link = '.'.join(parts[:-1]) + '.' + parts[-1].lower()
        
        # Ensure https and remove @ symbol if present
        return cleaned_link.replace('@', '').replace('http:', 'https:')
    except Exception as e:
        print(f"Error decrypting download link: {e}")
        return None


def create_image_links(link: str) -> List[Dict[str, str]]:
    """Create image links with different qualities"""
    if not link:
        return []
    
    qualities = ['50x50', '150x150', '500x500']
    quality_regex = re.compile(r'150x150|50x50')
    protocol_regex = re.compile(r'^http://')
    
    return [
        {
            'quality': quality,
            'url': protocol_regex.sub('https://', quality_regex.sub(quality, link))
        }
        for quality in qualities
    ]


def create_artist_map_payload(artist: Dict[str, Any]) -> Dict[str, Any]:
    """Create artist payload from raw artist data"""
    return {
        'id': artist.get('id'),
        'name': artist.get('name'),
        'role': artist.get('role'),
        'image': create_image_links(artist.get('image', '')),
        'type': artist.get('type'),
        'url': artist.get('perma_url')
    }


def create_song_payload(song: Dict[str, Any]) -> Dict[str, Any]:
    """Create song payload from raw song data"""
    more_info = song.get('more_info', {})
    artist_map = more_info.get('artistMap', {})
    
    return {
        'id': song.get('id'),
        'name': song.get('title'),
        'type': song.get('type'),
        'year': song.get('year'),
        'releaseDate': more_info.get('release_date'),
        'duration': int(more_info.get('duration', 0)) if more_info.get('duration') else None,
        'label': more_info.get('label'),
        'explicitContent': song.get('explicit_content') == '1',
        'playCount': int(song.get('play_count', 0)) if song.get('play_count') else None,
        'language': song.get('language'),
        'hasLyrics': more_info.get('has_lyrics') == 'true',
        'lyricsId': more_info.get('lyrics_id'),
        'url': song.get('perma_url'),
        'copyright': more_info.get('copyright_text'),
        'album': {
            'id': more_info.get('album_id'),
            'name': more_info.get('album'),
            'url': more_info.get('album_url')
        },
        'artists': {
            'primary': [create_artist_map_payload(artist) for artist in artist_map.get('primary_artists', [])],
            'featured': [create_artist_map_payload(artist) for artist in artist_map.get('featured_artists', [])],
            'all': [create_artist_map_payload(artist) for artist in artist_map.get('artists', [])]
        },
        'image': create_image_links(song.get('image', '')),
        'downloadUrl': create_download_links(more_info.get('encrypted_media_url'))
    }


def normalize_string(text: str) -> str:
    """Normalize string by removing diacritics"""
    import unicodedata
    return unicodedata.normalize('NFD', text).encode('ascii', 'ignore').decode('ascii')
