# WeBro FM — Flutter API Integration Guide

**Base URL:** `https://api.webrofm.in/api`

---

## Table of Contents
1. [Auth (OTP Login)](#1-auth-otp-login)
2. [User Profile](#2-user-profile)
3. [Home / Discovery](#3-home--discovery)
4. [Shows & Episodes](#4-shows--episodes)
5. [Audio Streaming](#5-audio-streaming)
6. [Interactions (Like, Favorite, Comments)](#6-interactions)
7. [Continue Playing (Resume)](#7-continue-playing-resume)
8. [Analytics](#8-analytics)
9. [Collaboration (Stories & Sponsorships)](#9-collaboration)
10. [Reports](#10-reports)

---

## 1. Auth (OTP Login)

### Send OTP
```dart
Future<void> sendOtp(String phone) async {
  final response = await http.post(
    Uri.parse('$baseUrl/auth/send-otp/'),
    headers: {'Content-Type': 'application/json'},
    body: jsonEncode({'phone_number': phone}),
  );
  if (response.statusCode == 200) {
    print('OTP sent');
  }
}
```
**Body:** `{ "phone_number": "9999999999" }`
**Response:** `{ "message": "OTP sent successfully" }`

### Verify OTP
```dart
Future<Map<String, dynamic>> verifyOtp(String phone, String otp) async {
  final response = await http.post(
    Uri.parse('$baseUrl/auth/verify-otp/'),
    headers: {'Content-Type': 'application/json'},
    body: jsonEncode({'phone_number': phone, 'otp_code': otp}),
  );
  if (response.statusCode == 200) {
    final data = jsonDecode(response.body);
    // Save tokens
    await storage.write('access_token', data['access']);
    await storage.write('refresh_token', data['refresh']);
    return data['user'];
  }
  throw Exception('OTP verification failed');
}
```
**Body:** `{ "phone_number": "9999999999", "otp_code": "123456" }`
**Response:**
```json
{
  "access": "eyJ...",
  "refresh": "eyJ...",
  "user": {
    "id": 3,
    "phone_number": "9999999999",
    "email": null,
    "full_name": "Dummy User",
    "date_of_birth": null,
    "profile_picture": null,
    "interests": [],
    "date_joined": "2026-06-14T20:36:02.478393Z"
  }
}
```

> ⚠️ **Dev Mode:** Phone `9999999999` → OTP always `123456`
> MSG91 OTP is live for all other numbers.

---

## 2. User Profile

### Get Profile
```dart
Future<Map<String, dynamic>> getProfile(String token) async {
  final response = await http.get(
    Uri.parse('$baseUrl/auth/profile/'),
    headers: {'Authorization': 'Bearer $token'},
  );
  return jsonDecode(response.body);
}
```

### Update Profile
```dart
Future<void> updateProfile(String token, {String? name, String? email, String? dob, List<String>? interests}) async {
  final body = <String, dynamic>{};
  if (name != null) body['full_name'] = name;
  if (email != null) body['email'] = email;
  if (dob != null) body['date_of_birth'] = dob;
  if (interests != null) body['interests'] = interests;

  final response = await http.patch(
    Uri.parse('$baseUrl/auth/profile/'),
    headers: {
      'Authorization': 'Bearer $token',
      'Content-Type': 'application/json',
    },
    body: jsonEncode(body),
  );
}
```
**PATCH Body example:**
```json
{
  "full_name": "John Doe",
  "email": "john@example.com",
  "date_of_birth": "1995-06-15",
  "interests": ["action", "romance", "thriller"]
}
```

---

## 3. Home / Discovery

### Preload (Fast — All Shows + Categories)
No auth required. Cached in Redis for 5 minutes.

```dart
Future<Map<String, dynamic>> fetchPreload() async {
  final response = await http.get(
    Uri.parse('$baseUrl/home/preload/'),
  );
  return jsonDecode(response.body);
}
```

**Response structure:**
```json
{
  "shows": [
    {
      "id": 1,
      "title": "Show Title",
      "description": "Description...",
      "thumbnail": "https://...",
      "thumbnail_url": "https://r2.signed...",
      "category_name": "Action",
      "age_rating": "13+",
      "teasers": [
        {
          "id": 1,
          "title": "Teaser 1",
          "video_url": "https://r2.signed...",
          "thumbnail_url": "https://r2.signed..."
        }
      ],
      "episodes": [
        {
          "id": 1,
          "title": "Ep 1",
          "sequence_number": 1,
          "duration_seconds": 600,
          "audio_file_key": "uploads/audio/...",
          "hls_playlist_key": ""
        }
      ]
    }
  ],
  "categories": [
    { "id": 1, "name": "Action", "slug": "action", "icon": null }
  ]
}
```

> 💡 `thumbnail_url` and `video_url` are **signed R2 URLs** — use directly in `Image.network()` or `CachedNetworkImage`.

### Home Screen (Authenticated)
```dart
Future<Map<String, dynamic>> fetchHome(String token) async {
  final response = await http.get(
    Uri.parse('$baseUrl/home/'),
    headers: {'Authorization': 'Bearer $token'},
  );
  return jsonDecode(response.body);
}
```
Returns: `{ "featured": [...], "trending": [...], "recent": [...], "categories": [...] }`

### Trending (No Auth)
```dart
Future<List<dynamic>> fetchTrending() async {
  final response = await http.get(Uri.parse('$baseUrl/home/trending/'));
  final data = jsonDecode(response.body);
  return data['trending'];
}
```

---

## 4. Shows & Episodes

### Get Episodes for a Show
```dart
Future<List<dynamic>> fetchEpisodes(int showId, String token) async {
  final response = await http.get(
    Uri.parse('$baseUrl/shows/$showId/episodes/'),
    headers: {'Authorization': 'Bearer $token'},
  );
  return jsonDecode(response.body);
}
```

**Response (list):**
```json
[
  {
    "id": 1,
    "show": 5,
    "title": "Episode 1",
    "description": "Description...",
    "duration_seconds": 600,
    "sequence_number": 1,
    "audio_file_key": "uploads/audio/abc.mp3",
    "audio_url": "https://e75d0e418e83eb4f77917abd63f8ec0f.r2.cloudflarestorage.com/...signed...",
    "hls_playlist_key": "",
    "created_at": "2026-06-17T..."
  }
]
```

> 💡 `audio_url` is a **signed URL** valid for 1 hour — use directly for streaming.

---

## 5. Audio Streaming

### Play Episode (Get Signed URL)
```dart
Future<String> getPlayUrl(int episodeId, String token) async {
  final response = await http.get(
    Uri.parse('$baseUrl/play/ep/$episodeId/'),
    headers: {'Authorization': 'Bearer $token'},
  );
  if (response.statusCode == 200) {
    final data = jsonDecode(response.body);
    return data['audio_url'];
  }
  throw Exception('Failed to get play URL');
}
```

**Response:**
```json
{
  "episode_id": 1,
  "audio_url": "https://r2.cloudflare...signed...",
  "hls_url": null,
  "title": "Episode 1",
  "expires_in": 3600
}
```

### Flutter Audio Player Example
```dart
import 'package:just_audio/just_audio.dart';

final player = AudioPlayer();

Future<void> playEpisode(int episodeId, String token) async {
  // 1. Get signed URL from backend
  final response = await http.get(
    Uri.parse('$baseUrl/play/ep/$episodeId/'),
    headers: {'Authorization': 'Bearer $token'},
  );
  final data = jsonDecode(response.body);
  final audioUrl = data['audio_url'];

  // 2. Play with just_audio
  await player.setAudioSource(
    AudioSource.uri(Uri.parse(audioUrl)),
  );
  await player.play();
}
```

> 💡 The signed URL expires in 1 hour. If playback fails, fetch a new one from `play/ep/<id>/`.

---

## 6. Interactions

### Like / Unlike Episode
```dart
Future<bool> toggleLike(int episodeId, String token) async {
  final response = await http.post(
    Uri.parse('$baseUrl/user/like/toggle/'),
    headers: {
      'Authorization': 'Bearer $token',
      'Content-Type': 'application/json',
    },
    body: jsonEncode({'episode_id': episodeId}),
  );
  final data = jsonDecode(response.body);
  return data['is_liked']; // true = liked, false = unliked
}
```
**Response:** `{ "is_liked": true, "likes_count": 42 }`

### Favorite / Unfavorite Show
```dart
Future<bool> toggleFavorite(int showId, String token) async {
  final response = await http.post(
    Uri.parse('$baseUrl/user/favorite/toggle/'),
    headers: {
      'Authorization': 'Bearer $token',
      'Content-Type': 'application/json',
    },
    body: jsonEncode({'show_id': showId}),
  );
  final data = jsonDecode(response.body);
  return data['is_favorited'];
}
```
**Response:** `{ "is_favorited": true }`

### My Favorites List
```dart
Future<List<dynamic>> getFavorites(String token) async {
  final response = await http.get(
    Uri.parse('$baseUrl/user/favorites/'),
    headers: {'Authorization': 'Bearer $token'},
  );
  return jsonDecode(response.body);
}
```

### Comments
```dart
// Get comments for episode
Future<List<dynamic>> getComments(int episodeId, String token) async {
  final response = await http.get(
    Uri.parse('$baseUrl/user/comments/?episode=$episodeId'),
    headers: {'Authorization': 'Bearer $token'},
  );
  return jsonDecode(response.body);
}

// Post a comment
Future<void> postComment(int episodeId, String content, String token) async {
  final response = await http.post(
    Uri.parse('$baseUrl/user/comments/'),
    headers: {
      'Authorization': 'Bearer $token',
      'Content-Type': 'application/json',
    },
    body: jsonEncode({
      'episode_id': episodeId,
      'content': content,
    }),
  );
}
```

### Feedback
```dart
Future<void> submitFeedback(int episodeId, int rating, String comment, String token) async {
  final response = await http.post(
    Uri.parse('$baseUrl/user/feedback/'),
    headers: {
      'Authorization': 'Bearer $token',
      'Content-Type': 'application/json',
    },
    body: jsonEncode({
      'episode_id': episodeId,
      'rating': rating,
      'comment': comment,
    }),
  );
}
```

### Report Ad
```dart
Future<void> reportAd(int adId, String reason, String token) async {
  final response = await http.post(
    Uri.parse('$baseUrl/ads/report/'),
    headers: {
      'Authorization': 'Bearer $token',
      'Content-Type': 'application/json',
    },
    body: jsonEncode({
      'ad_id': adId,
      'reason': reason,
    }),
  );
}
```

---

## 7. Continue Playing (Resume)

### Update Playback Position
```dart
Future<void> updateResume(int episodeId, int positionSeconds, String token) async {
  final response = await http.post(
    Uri.parse('$baseUrl/user/resume/update/'),
    headers: {
      'Authorization': 'Bearer $token',
      'Content-Type': 'application/json',
    },
    body: jsonEncode({
      'episode_id': episodeId,
      'position_seconds': positionSeconds,
    }),
  );
}
```

### Get Resume List
```dart
Future<List<dynamic>> getResumeList(String token) async {
  final response = await http.get(
    Uri.parse('$baseUrl/user/resume/'),
    headers: {'Authorization': 'Bearer $token'},
  );
  return jsonDecode(response.body);
}
```
Returns episodes with `position_seconds` and `episode` details so you can show "Continue from 12:30" in UI.

---

## 8. Analytics

### Track Play Hit
```dart
Future<void> trackPlay(int episodeId, int durationListened, String token) async {
  final response = await http.post(
    Uri.parse('$baseUrl/analytics/hit/'),
    headers: {
      'Authorization': 'Bearer $token',
      'Content-Type': 'application/json',
    },
    body: jsonEncode({
      'episode_id': episodeId,
      'duration_listened': durationListened,
    }),
  );
}
```
Call this when user listens to an episode. Used for trending calculation.

---

## 9. Collaboration

### Submit Story
```dart
Future<void> submitStory(String title, String content, int categoryId, String token) async {
  final response = await http.post(
    Uri.parse('$baseUrl/collab/story/submit/'),
    headers: {
      'Authorization': 'Bearer $token',
      'Content-Type': 'application/json',
    },
    body: jsonEncode({
      'title': title,
      'content': content,
      'category': categoryId,
    }),
  );
}
```

### My Stories
```dart
Future<List<dynamic>> getMyStories(String token) async {
  final response = await http.get(
    Uri.parse('$baseUrl/collab/stories/'),
    headers: {'Authorization': 'Bearer $token'},
  );
  return jsonDecode(response.body);
}
```

### Submit Sponsorship / Ad
```dart
Future<void> submitAd(String title, String description, String audience, String token) async {
  final response = await http.post(
    Uri.parse('$baseUrl/collab/ads/submit/'),
    headers: {
      'Authorization': 'Bearer $token',
      'Content-Type': 'application/json',
    },
    body: jsonEncode({
      'title': title,
      'description': description,
      'target_audience': audience,
    }),
  );
}
```

### My Ads
```dart
Future<List<dynamic>> getMyAds(String token) async {
  final response = await http.get(
    Uri.parse('$baseUrl/collab/ads/'),
    headers: {'Authorization': 'Bearer $token'},
  );
  return jsonDecode(response.body);
}
```

---

## 10. Reports

### Report Ad
```dart
Future<void> reportAd(int adId, String reason, String token) async {
  final response = await http.post(
    Uri.parse('$baseUrl/ads/report/'),
    headers: {
      'Authorization': 'Bearer $token',
      'Content-Type': 'application/json',
    },
    body: jsonEncode({
      'ad_id': adId,
      'reason': reason,
    }),
  );
}
```

---

## Flutter App Flow — Recommended Order

1. **App Start** → `GET /home/preload/` (no auth) → show home screen
2. **User taps Login** → `POST /auth/send-otp/` → `POST /auth/verify-otp/` → save tokens
3. **User taps Show** → `GET /shows/<id>/episodes/` → show episode list
4. **User taps Play** → `GET /play/ep/<id>/` → stream audio via `just_audio`
5. **While playing** → `POST /user/resume/update/` periodically save position
6. **On episode end** → `POST /analytics/hit/` track listen
7. **User likes** → `POST /user/like/toggle/`
8. **User favorites** → `POST /user/favorite/toggle/`
9. **User comments** → `POST /user/comments/`
10. **Continue Watching** → `GET /user/resume/` → show resume list on home

---

## Quick Reference — All Endpoints

| # | Method | Endpoint | Auth | Description |
|---|--------|----------|------|-------------|
| 1 | POST | `/auth/send-otp/` | ❌ | Send OTP |
| 2 | POST | `/auth/verify-otp/` | ❌ | Verify OTP → JWT |
| 3 | GET | `/auth/profile/` | ✅ | Get profile |
| 4 | PATCH | `/auth/profile/` | ✅ | Update profile |
| 5 | GET | `/home/preload/` | ❌ | All shows + categories |
| 6 | GET | `/home/` | ✅ | Featured + Trending + Recent |
| 7 | GET | `/home/trending/` | ❌ | Weekly trending |
| 8 | GET | `/shows/<id>/episodes/` | ✅ | Episode list |
| 9 | GET | `/play/ep/<id>/` | ✅ | Get signed audio URL |
| 10 | POST | `/user/like/toggle/` | ✅ | Like/unlike episode |
| 11 | POST | `/user/favorite/toggle/` | ✅ | Favorite/unfavorite show |
| 12 | GET | `/user/favorites/` | ✅ | My favorites |
| 13 | GET | `/user/comments/?episode=` | ✅ | Get comments |
| 14 | POST | `/user/comments/` | ✅ | Post comment |
| 15 | POST | `/user/feedback/` | ✅ | Submit feedback |
| 16 | POST | `/ads/report/` | ✅ | Report ad |
| 17 | POST | `/user/resume/update/` | ✅ | Save playback position |
| 18 | GET | `/user/resume/` | ✅ | Get resume list |
| 19 | POST | `/analytics/hit/` | ✅ | Track play |
| 20 | POST | `/collab/story/submit/` | ✅ | Submit story |
| 21 | GET | `/collab/stories/` | ✅ | My stories |
| 22 | POST | `/collab/ads/submit/` | ✅ | Submit ad/sponsorship |
| 23 | GET | `/collab/ads/` | ✅ | My ads |
