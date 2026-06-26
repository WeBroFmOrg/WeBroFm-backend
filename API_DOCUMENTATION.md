# WeBro FM — Complete API Reference

**Base URL:** `https://api.webrofm.in/api`

**Auth:** Most endpoints require `Authorization: Bearer <access_token>`
Token from `/auth/verify-otp/` ya `/admin/login/`

---

## 1. AUTH — OTP Login / Profile

### Send OTP
```
POST /auth/send-otp/
Body: { "phone_number": "9999999999" }
```
Dev mode: phone=9999999999 → OTP always 123456

### Verify OTP
```
POST /auth/verify-otp/
Body: { "phone_number": "9999999999", "otp_code": "123456" }
```
Response: `{ "access": "...", "refresh": "...", "user": {...} }`

### Get / Update Profile
```
GET  /auth/profile/
PATCH /auth/profile/
```
PATCH body: `{ "full_name": "...", "email": "...", "date_of_birth": "2000-01-01", "interests": ["action", "romance"] }`

---

## 2. CONTENT — Shows / Episodes / Stream

### Preload (Home + All Shows) — NO AUTH
```
GET /home/preload/
```
Response: `{ shows: [{...}], categories: [{...}] }`
Each show: `id, title, description, thumbnail_url, category_name, age_rating, teasers[], episodes[]`

### Home Screen — AUTH
```
GET /home/
```
Response: `{ featured: [], trending: [], recent: [], categories: [] }`

### Trending — NO AUTH
```
GET /home/trending/
```

### Show Episodes
```
GET /shows/<show_id>/episodes/
```
Response: `[{ id, show, title, description, duration_seconds, sequence_number, audio_file_key, audio_url, hls_playlist_key }]`

### Episode Stream (Play)
```
GET /play/ep/<episode_id>/
```
Response: `{ episode_id, audio_url, hls_url, title, expires_in }`
`audio_url` is a signed R2 URL — use directly in audio player.

---

## 3. USER INTERACTIONS

### Like Toggle
```
POST /user/like/toggle/
Body: { "episode_id": 1 }
```

### Favorite Toggle
```
POST /user/favorite/toggle/
Body: { "show_id": 1 }
```

### My Favorites
```
GET /user/favorites/
```

### Comments
```
GET  /user/comments/?episode=1
POST /user/comments/
Body: { "episode_id": 1, "content": "Awesome!" }
```

### Feedback
```
POST /user/feedback/
Body: { "episode_id": 1, "rating": 5, "comment": "Nice" }
```

### Report Ad
```
POST /ads/report/
Body: { "ad_id": 1, "reason": "Inappropriate" }
```

### Resume / Continue Playing
```
POST /user/resume/update/
Body: { "episode_id": 1, "position_seconds": 120 }
GET  /user/resume/
```

### Analytics Hit (track play)
```
POST /analytics/hit/
Body: { "episode_id": 1, "duration_listened": 30 }
```

---

## 4. COLLAB — Stories & Sponsorships

### Submit Story
```
POST /collab/story/submit/
Body: { "title": "...", "content": "...", "category": 1 }
```

### My Stories
```
GET /collab/stories/
```

### Submit Ad
```
POST /collab/ads/submit/
Body: { "title": "...", "description": "...", "target_audience": "..." }
```

### My Ads
```
GET /collab/ads/
```

---

## 5. ADMIN PANEL

All admin endpoints under `/admin/*` require `IsAdminUser`.

### Login
```
POST /admin/login/
Body: { "phone_number": "8888888888", "password": "Admin@12345" }
```

### Dashboard
```
GET /admin/dashboard/stats/
```

### Users
```
GET    /admin/users/?search=
GET    /admin/users/<id>/
PUT    /admin/users/<id>/
DELETE /admin/users/<id>/
POST   /admin/users/<id>/action/
Body: { "action": "block"|"activate"|"make_staff"|"remove_staff" }
```

### Categories
```
GET    /admin/categories/
POST   /admin/categories/
GET    /admin/categories/<id>/
PUT    /admin/categories/<id>/
DELETE /admin/categories/<id>/
```

### Authors
```
GET    /admin/authors/
POST   /admin/authors/
GET    /admin/authors/<id>/
PUT    /admin/authors/<id>/
DELETE /admin/authors/<id>/
```

### Shows
```
GET    /admin/shows/?search=&category=
POST   /admin/shows/
GET    /admin/shows/<id>/
PUT    /admin/shows/<id>/
DELETE /admin/shows/<id>/
```
POST/PUT (JSON): `{ "title", "description", "category", "author", "age_rating", "is_featured", "is_trending" }`
Thumbnail: `multipart/form-data` with `thumbnail` file field.

### Episodes
```
GET    /admin/episodes/?show=
POST   /admin/episodes/
GET    /admin/episodes/<id>/
PUT    /admin/episodes/<id>/
DELETE /admin/episodes/<id>/
GET    /admin/episodes/<id>/play/
```
POST/PUT (multipart): `show, title, description, duration_seconds, sequence_number, audio_file (file)`
Ya JSON: `{ "show", "title", "description", "duration_seconds", "sequence_number" }`

### Episode Analytics
```
GET  /admin/episodes/<id>/analytics/
PUT  /admin/episodes/<id>/analytics/
```

### Comments (Admin)
```
GET    /admin/comments/?episode=
DELETE /admin/comments/<id>/
PATCH  /admin/comments/<id>/ Body: { "is_active": false }
```

### Reports
```
GET  /admin/reports/?resolved=true|false
POST /admin/reports/<id>/resolve/
```

### Feedback / Likes / Favorites
```
GET /admin/feedback/
GET /admin/likes/?episode=
GET /admin/favorites/
```

### Stories / Sponsorships (Admin)
```
GET    /admin/stories/?status=
GET    /admin/stories/<id>/
PUT    /admin/stories/<id>/
DELETE /admin/stories/<id>/
POST   /admin/collab/<id>/action/ Body: { "action": "approve"|"reject"|"reviewing" }

GET    /admin/sponsorships/?status=
GET    /admin/sponsorships/<id>/
PUT    /admin/sponsorships/<id>/
DELETE /admin/sponsorships/<id>/
POST   /admin/sponsorships/<id>/action/ Body: { "action": "approve"|"reject"|"expire" }
```

### R2 Storage
```
GET    /admin/storage/explorer/?prefix=
POST   /admin/storage/upload/ (multipart: file, prefix, compress)
DELETE /admin/storage/delete/?key=
```
