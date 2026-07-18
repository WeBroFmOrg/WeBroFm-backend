# WeBro FM — Website API Reference

> Base URL: `https://api.webrofm.in/api`

---

## Authentication Flow (OTP)

Website users authenticate via phone number OTP. JWT tokens are stored in localStorage.

### 1. Send OTP

```http
POST /api/auth/send-otp/
Content-Type: application/json

{
  "phone_number": "9999999999"
}
```

**Response** `200 OK`:
```json
{
  "message": "OTP sent successfully"
}
```

**Error** `429 Too Many Requests` (rate limited):
```json
{
  "error": "Too many OTP attempts. Try again after 1 hour."
}
```

### 2. Verify OTP

```http
POST /api/auth/verify-otp/
Content-Type: application/json

{
  "phone_number": "9999999999",
  "otp_code": "123456"
}
```

**Response** `200 OK`:
```json
{
  "message": "OTP verified successfully",
  "refresh": "eyJ0eXAiOiJKV1Qi...",
  "access": "eyJ0eXAiOiJKV1Qi...",
  "user": {
    "id": 1,
    "phone_number": "9999999999",
    "email": null,
    "full_name": "",
    "gender": "prefer_not_to_say",
    "date_of_birth": null,
    "profile_picture": null,
    "interests": [],
    "date_joined": "2026-07-05T18:33:16.944648Z"
  }
}
```

Store `access` token in localStorage and send as `Authorization: Bearer <token>` for all authenticated requests.

---

## Public Endpoints (No Login Required)

### 3. Preload Data — `/api/home/preload/`

Loads all shows (with first 5 episodes each), categories, languages, and teasers in one call.

```http
GET /api/home/preload/
# Optional: ?language=en  (filter by language code)
```

**Response** `200 OK`:
```json
{
  "shows": [
    {
      "id": 1,
      "title": "Show Title",
      "description": "Full show description text...",
      "thumbnail": "https://r2-url/shows/thumbnails/abc.jpg",
      "thumbnail_url": "https://signed-url/abc.jpg",
      "category_name": "Entertainment",
      "language_name": "English",
      "language_code": "en",
      "age_rating": "U",
      "episodes": [
        {
          "id": 1,
          "title": "Episode 1",
          "sequence_number": 1,
          "duration_seconds": 1800,
          "audio_file_key": "uploads/audio/abc.mp3",
          "hls_playlist_key": "",
          "language_name": "English",
          "language_code": "en"
        }
      ]
    }
  ],
  "categories": [
    {
      "id": 1,
      "name": "Entertainment",
      "slug": "entertainment",
      "icon": "https://r2-url/categories/icons/abc.png"
    }
  ],
  "languages": [
    {
      "id": 1,
      "name": "English",
      "code": "en",
      "icon": null,
      "is_active": true
    }
  ],
  "teasers": [
    {
      "id": 1,
      "title": "Coming Soon Title",
      "image": "https://r2-url/teasers/images/abc.jpg",
      "image_url": "https://signed-url/abc.jpg",
      "sequence": 1,
      "is_active": true,
      "is_converted": false,
      "converted_show": null,
      "converted_show_title": null,
      "created_at": "2026-07-05T18:33:16.944648Z"
    }
  ]
}
```

**Query Params:**
| Param | Type | Description |
|-------|------|-------------|
| `language` | string | Filter shows by language code: `en`, `hi`, `genz` |

---

### 4. Trending Shows — `/api/home/trending/`

All-time trending shows ranked by total episode plays. Cache updates every 12 hours via cron.

```http
GET /api/home/trending/
# Optional: ?language=en
```

**Response** `200 OK`:
```json
{
  "trending": [
    {
      "rank": 1,
      "id": 5,
      "title": "Trending Show",
      "description": "Show description",
      "thumbnail": "shows/thumbnails/abc.jpg",
      "category_name": "Entertainment",
      "language_name": "English",
      "language_code": "en",
      "total_hits": 1523,
      "age_rating": "U",
      "is_featured": false,
      "created_at": "2026-07-05T18:33:16.944648Z"
    }
  ],
  "cached": true,
  "updated_at": "2026-07-12T12:00:00Z"
}
```

---

## Authenticated Endpoints (Login Required)

Send header: `Authorization: Bearer <access_token>`

### 5. Home Page — `/api/home/`

```http
GET /api/home/
Authorization: Bearer <token>
# Optional: ?language=en
```

**Response** `200 OK`:
```json
{
  "featured": [
    {
      "id": 1,
      "title": "Featured Show",
      "description": "Description...",
      "category": 1,
      "author": 1,
      "category_name": "Entertainment",
      "author_name": "Author Name",
      "language": 1,
      "language_name": "English",
      "language_code": "en",
      "thumbnail": "https://r2-url/shows/thumbnails/abc.jpg",
      "age_rating": "U",
      "is_featured": true,
      "is_trending": false,
      "created_at": "2026-07-05T18:33:16.944648Z"
    }
  ],
  "trending": [ /* Show objects */ ],
  "recent": [ /* Show objects sorted by created_at */ ],
  "categories": [ /* Category objects */ ],
  "languages": [ /* Language objects */ ]
}
```

---

### 6. Show Episodes — `/api/shows/<show_id>/episodes/`

```http
GET /api/shows/1/episodes/
Authorization: Bearer <token>
# Optional: ?language=en
```

**Response** `200 OK`:
```json
[
  {
    "id": 1,
    "show": 1,
    "title": "Episode Title",
    "description": "Episode description text...",
    "duration_seconds": 1800,
    "sequence_number": 1,
    "audio_file_key": "uploads/audio/abc.mp3",
    "hls_playlist_key": "uploads/hls/abc.m3u8",
    "audio_url": "https://signed-r2-url/abc.mp3?Signature=...&Expires=...",
    "language": 1,
    "language_name": "English",
    "language_code": "en",
    "created_at": "2026-07-05T18:33:16.944648Z"
  }
]
```

| Field | Description |
|-------|-------------|
| `audio_url` | Signed Cloudflare R2 URL (expires in 1 hour). Use this for audio playback. |
| `hls_playlist_key` | Path to HLS .m3u8 file in R2 (if available for streaming) |
| `duration_seconds` | Length of episode in seconds |
| `language_name` / `language_code` | Language of this specific episode |

---

### 7. Episode Play — `/api/play/ep/<episode_id>/`

Get playable audio URL (signed) for an episode.

```http
GET /api/play/ep/1/
Authorization: Bearer <token>
```

**Response** `200 OK`:
```json
{
  "episode_id": 1,
  "audio_url": "https://signed-r2-url/abc.mp3?Signature=...&Expires=...",
  "hls_url": "https://signed-r2-url/abc.m3u8?Signature=...&Expires=...",
  "title": "Episode Title",
  "expires_in": 3600
}
```

> Use `audio_url` for direct audio playback. `hls_url` is for HLS streaming if available.

---

### 8. User Profile — `/api/auth/profile/`

```http
GET /api/auth/profile/
Authorization: Bearer <token>
```

**Response** `200 OK`:
```json
{
  "id": 1,
  "phone_number": "9999999999",
  "email": "user@example.com",
  "full_name": "John Doe",
  "gender": "male",
  "date_of_birth": "2000-01-15",
  "profile_picture": "https://r2-url/users/profiles/abc.jpg",
  "interests": [1, 3, 5],
  "date_joined": "2026-07-05T18:33:16.944648Z"
}
```

Update profile:
```http
PATCH /api/auth/profile/
Authorization: Bearer <token>
Content-Type: application/json

{
  "full_name": "John Doe",
  "email": "john@example.com",
  "gender": "male",
  "date_of_birth": "2000-01-15",
  "interests": [1, 3, 5]
}
```

> For `profile_picture`, use `multipart/form-data` with a file upload.

---

### 9. Favorites

**Toggle Favorite** (add/remove show):
```http
POST /api/user/favorite/toggle/
Authorization: Bearer <token>
Content-Type: application/json

{
  "show_id": 1
}
```

Response (added):
```json
{ "message": "Show added to favorites", "favorited": true }
```
Response (removed):
```json
{ "message": "Show removed from favorites", "favorited": false }
```

**List Favorites:**
```http
GET /api/user/favorites/
Authorization: Bearer <token>
```

```json
[
  {
    "id": 1,
    "show": {
      "id": 1,
      "title": "Show Title",
      "description": "Description...",
      "category": 1,
      "author": 1,
      "category_name": "Entertainment",
      "author_name": "Author",
      "language": 1,
      "language_name": "English",
      "language_code": "en",
      "thumbnail": "https://...",
      "age_rating": "U",
      "is_featured": false,
      "is_trending": false,
      "created_at": "2026-07-05T18:33:16.944648Z"
    },
    "created_at": "2026-07-12T12:33:08.250835Z"
  }
]
```

---

### 10. Likes

```http
POST /api/user/like/toggle/
Authorization: Bearer <token>
Content-Type: application/json

# For episode:
{ "episode_id": 1 }

# For story:
{ "story_id": 1 }
```

Response:
```json
{ "liked": true }   // or { "liked": false } on unlike
```

---

### 11. Comments

**List comments by episode:**
```http
GET /api/user/comments/?episode_id=1
Authorization: Bearer <token>
```

**List comments by story:**
```http
GET /api/user/comments/?story_id=1
Authorization: Bearer <token>
```

**Response:**
```json
[
  {
    "id": 1,
    "username": "John Doe",
    "episode": 1,
    "story": null,
    "text": "Great episode!",
    "created_at": "2026-07-12T12:33:08.250835Z"
  }
]
```

**Create comment:**
```http
POST /api/user/comments/
Authorization: Bearer <token>
Content-Type: application/json

{
  "episode_id": 1,
  "text": "Amazing content!"
}
```

---

### 12. Feedback

```http
POST /api/user/feedback/
Authorization: Bearer <token>
Content-Type: application/json

{
  "episode_id": 1,
  "rating": 5,
  "comment": "Loved this episode!"
}
```

**Response** `201 Created`:
```json
{
  "id": 1,
  "episode": 1,
  "rating": 5,
  "comment": "Loved this episode!",
  "created_at": "2026-07-12T12:33:08.250835Z"
}
```

---

### 13. Report Ad

```http
POST /api/ads/report/
Authorization: Bearer <token>
Content-Type: application/json

{
  "ad": 1,
  "reason": "Inappropriate content"
}
```

---

### 14. Resume Playback

**Update resume position:**
```http
POST /api/user/resume/update/
Authorization: Bearer <token>
Content-Type: application/json

{
  "episode_id": 1,
  "last_position_seconds": 450
}
```

**List resume points:**
```http
GET /api/user/resume/
Authorization: Bearer <token>
```

**Response:**
```json
[
  {
    "id": 1,
    "episode": {
      "id": 1,
      "show": 1,
      "title": "Episode Title",
      "description": "...",
      "duration_seconds": 1800,
      "sequence_number": 1,
      "audio_file_key": "uploads/audio/abc.mp3",
      "hls_playlist_key": "",
      "audio_url": "https://signed-r2-url/abc.mp3?...",
      "language": 1,
      "language_name": "English",
      "language_code": "en",
      "created_at": "2026-07-05T18:33:16.944648Z"
    },
    "last_position_seconds": 450,
    "updated_at": "2026-07-12T12:33:08.250835Z"
  }
]
```

---

### 15. Analytics Hit (Track Play)

```http
POST /api/analytics/hit/
Authorization: Bearer <token>
Content-Type: application/json

{
  "episode_id": 1
}
```

**Response** `201 Created`:
```json
{ "status": "recorded" }
```

> Call this when user starts playing an episode to track listen count.

---

### 16. Story Submission

```http
POST /api/collab/story/submit/
Authorization: Bearer <token>
Content-Type: application/json

{
  "title": "My Story Title",
  "content": "Full story content here..."
}
```

**List my stories:**
```http
GET /api/collab/stories/
Authorization: Bearer <token>
```

---

### 17. Sponsorship / Ad Request

```http
POST /api/collab/ads/submit/
Authorization: Bearer <token>
Content-Type: multipart/form-data

brand_name: "My Brand"
description: "Ad description"
ad_visual: <file_upload>
target_url: "https://mybrand.com"
```

**List my ads:**
```http
GET /api/collab/ads/
Authorization: Bearer <token>
```

---

## Website Usage — Code Examples

### JavaScript Fetch Example

```javascript
// ── OTP Login Flow ──

async function sendOTP(phone) {
  const res = await fetch('https://api.webrofm.in/api/auth/send-otp/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ phone_number: phone })
  });
  return res.json();
}

async function verifyOTP(phone, otp) {
  const res = await fetch('https://api.webrofm.in/api/auth/verify-otp/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ phone_number: phone, otp_code: otp })
  });
  const data = await res.json();
  if (data.access) {
    localStorage.setItem('access_token', data.access);
    localStorage.setItem('refresh_token', data.refresh);
    localStorage.setItem('user', JSON.stringify(data.user));
  }
  return data;
}

// ── Authenticated Request Helper ──

async function apiFetch(url, options = {}) {
  const token = localStorage.getItem('access_token');
  const headers = {
    'Content-Type': 'application/json',
    ...(token ? { 'Authorization': `Bearer ${token}` } : {}),
    ...options.headers,
  };
  // Remove Content-Type for FormData (browser sets it automatically)
  if (options.body instanceof FormData) delete headers['Content-Type'];
  const res = await fetch(`https://api.webrofm.in${url}`, { ...options, headers });
  if (!res.ok) throw new Error(`API Error: ${res.status}`);
  return res.json();
}

// ── Example Calls ──

// Preload (public - no token needed)
const preload = await apiFetch('/api/home/preload/');
console.log(preload.shows);       // All shows with episodes
console.log(preload.categories);  // All categories
console.log(preload.languages);   // All active languages
console.log(preload.teasers);     // Coming soon teasers

// Preload filtered by language
const hindiShows = await apiFetch('/api/home/preload/?language=hi');

// Home (authenticated)
const home = await apiFetch('/api/home/', { headers: { 'Authorization': `Bearer ${token}` } });

// Show episodes with language filter
const episodes = await apiFetch('/api/shows/1/episodes/?language=en', {
  headers: { 'Authorization': `Bearer ${token}` }
});

// Play episode
const playData = await apiFetch('/api/play/ep/1/', {
  headers: { 'Authorization': `Bearer ${token}` }
});
// playData.audio_url → use as <audio> src
// <audio src={playData.audio_url} controls />

// Favorites toggle
await apiFetch('/api/user/favorite/toggle/', {
  method: 'POST',
  body: JSON.stringify({ show_id: 1 }),
  headers: { 'Authorization': `Bearer ${token}` }
});

// Resume playback
await apiFetch('/api/user/resume/update/', {
  method: 'POST',
  body: JSON.stringify({ episode_id: 1, last_position_seconds: 300 }),
  headers: { 'Authorization': `Bearer ${token}` }
});

// Track play (analytics hit)
await apiFetch('/api/analytics/hit/', {
  method: 'POST',
  body: JSON.stringify({ episode_id: 1 }),
  headers: { 'Authorization': `Bearer ${token}` }
});

// Trending
const trending = await apiFetch('/api/home/trending/');
```

---

## Quick Reference — All Endpoints

| # | Method | Endpoint | Auth | Language Filter | Page/Feature |
|---|--------|----------|------|-----------------|-------------|
| 1 | POST | `/api/auth/send-otp/` | No | — | Login page |
| 2 | POST | `/api/auth/verify-otp/` | No | — | Login page |
| 3 | GET | `/api/home/preload/` | **No** | `?language=code` | Splash / Landing page |
| 4 | GET | `/api/home/trending/` | **No** | `?language=code` | Trending section |
| 5 | GET | `/api/home/` | Yes | `?language=code` | Home dashboard |
| 6 | GET | `/api/shows/{id}/episodes/` | Yes | `?language=code` | Show detail page |
| 7 | GET | `/api/play/ep/{id}/` | Yes | — | Audio player page |
| 8 | GET | `/api/auth/profile/` | Yes | — | Profile page |
| 9 | PATCH | `/api/auth/profile/` | Yes | — | Edit profile |
| 10 | POST | `/api/user/favorite/toggle/` | Yes | — | Show card / detail |
| 11 | GET | `/api/user/favorites/` | Yes | — | Favorites page |
| 12 | POST | `/api/user/like/toggle/` | Yes | — | Episode player |
| 13 | GET | `/api/user/comments/` | Yes | — | Comments section |
| 14 | POST | `/api/user/comments/` | Yes | — | Comment form |
| 15 | POST | `/api/user/feedback/` | Yes | — | Feedback form |
| 16 | POST | `/api/ads/report/` | Yes | — | Report ad |
| 17 | POST | `/api/user/resume/update/` | Yes | — | Audio player |
| 18 | GET | `/api/user/resume/` | Yes | — | Resume / Continue listening |
| 19 | POST | `/api/analytics/hit/` | Yes | — | Track play |
| 20 | POST | `/api/collab/story/submit/` | Yes | — | Story submission form |
| 21 | GET | `/api/collab/stories/` | Yes | — | My stories page |
| 22 | POST | `/api/collab/ads/submit/` | Yes | — | Ad request form |
| 23 | GET | `/api/collab/ads/` | Yes | — | My ads page |

---

## Language Filtering for Website

The website should show a language selector at the top. When user selects a language:

1. **Preload (no auth):** `GET /api/home/preload/?language=en`
2. **Home (auth):** `GET /api/home/?language=en`
3. **Trending:** `GET /api/home/trending/?language=en`
4. **Episodes:** `GET /api/shows/{id}/episodes/?language=en`

**Language options available:** English (`en`), Hindi (`hi`), GenZ (`genz`)
- Get full list from preload response's `languages` key.

---

## Audio Player Integration

For each episode, two ways to play audio:

```html
<!-- Method 1: Direct signed URL (recommended) -->
<audio src="{episode.audio_url}" controls preload="auto">
  Your browser does not support the audio element.
</audio>

<!-- Method 2: Get fresh signed URL via play endpoint -->
<script>
  async function playEpisode(episodeId) {
    const data = await apiFetch(`/api/play/ep/${episodeId}/`);
    const audio = new Audio(data.audio_url);
    audio.play();
    // Track play
    await apiFetch('/api/analytics/hit/', {
      method: 'POST',
      body: JSON.stringify({ episode_id: episodeId })
    });
  }
</script>
```

> Note: `audio_url` in episode list is already signed. Use `/api/play/ep/{id}/` to get a fresh URL if the previous one expired.
