# WeBro FM — Flutter App Complete API Guide

**Base URL:** `https://api.webrofm.in/api`

---

## Table of Contents
1. [Auth (OTP Login)](#1-auth-otp-login)
2. [Dev/Whitelist Mode](#2-devwhitelist-mode)
3. [User Profile](#3-user-profile)
4. [Home / Preload](#4-home--preload)
5. [Teasers (Coming Soon Cards)](#5-teasers-coming-soon-cards)
6. [Shows & Episodes](#6-shows--episodes)
7. [Audio Streaming](#7-audio-streaming)
8. [Interactions (Like, Favorite, Comments, Feedback)](#8-interactions)
9. [Continue Playing (Resume)](#9-continue-playing-resume)
10. [Analytics](#10-analytics)
11. [Collaboration (Stories & Sponsorships)](#11-collaboration)
12. [Ads & Reports](#12-ads--reports)
13. [Token Refresh](#13-token-refresh)
14. [Quick Reference — All Endpoints](#14-quick-reference--all-endpoints)
15. [Flutter App Navigation Flow](#15-flutter-app-navigation-flow)

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
  // Response: { "message": "OTP sent successfully" }
  // Dev mode also returns: { "otp": "123456", "message": "..." }
}
```

**Request:**
```json
{ "phone_number": "9999999999" }
```

**Response (production):**
```json
{ "message": "OTP sent successfully" }
```

**Response (dev mode — whitelisted phone):**
```json
{
  "message": "OTP sent successfully",
  "otp": "123456"
}
```

### Verify OTP → Get JWT
```dart
Future<Map<String, dynamic>> verifyOtp(String phone, String otp) async {
  final response = await http.post(
    Uri.parse('$baseUrl/auth/verify-otp/'),
    headers: {'Content-Type': 'application/json'},
    body: jsonEncode({'phone_number': phone, 'otp_code': otp}),
  );
  if (response.statusCode == 200) {
    final data = jsonDecode(response.body);
    await storage.write('access_token', data['access']);
    await storage.write('refresh_token', data['refresh']);
    return data['user'];
  }
  throw Exception('Invalid OTP');
}
```

**Request:**
```json
{
  "phone_number": "9999999999",
  "otp_code": "123456"
}
```

**Response:**
```json
{
  "access": "eyJhbGciOiJIUzI1NiIs...",
  "refresh": "eyJhbGciOiJIUzI1NiIs...",
  "user": {
    "id": 3,
    "phone_number": "9999999999",
    "email": null,
    "full_name": "",
    "date_of_birth": null,
    "profile_picture": null,
    "interests": [],
    "date_joined": "2026-06-14T20:36:02.478393Z"
  }
}
```

---

## 2. Dev/Whitelist Mode

The backend has a dev/login whitelist system:

| Setting | Value |
|---------|-------|
| `ENABLE_DEV_LOGIN` | `True` |
| **Whitelist phone** | `9999999999` |
| **Dev OTP** | `123456` |
| **Country code prefix** | `+91` (India) |

**How it works:**
- If `ENABLE_DEV_LOGIN=True` AND phone is `9999999999`:
  - Send OTP → returns OTP directly in response (`"otp": "123456"`)
  - OTP never expires (valid for 365 days)
  - Verify with any `"otp_code": "123456"` → works
- For ALL other numbers:
  - Real MSG91 OTP sent via SMS
  - OTP expires in 5 minutes
  - No OTP returned in API response

**Flutter logic:**
```dart
void handleOtpResponse(Map<String, dynamic> response) {
  // If dev mode returns OTP directly, auto-fill it
  if (response.containsKey('otp')) {
    // Auto-fill OTP field for easy testing
    setState(() => otpController.text = response['otp']);
  }
}
```

---

## 3. User Profile

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

**Response:**
```json
{
  "id": 3,
  "phone_number": "9999999999",
  "email": null,
  "full_name": "",
  "date_of_birth": null,
  "profile_picture": null,
  "interests": [],
  "date_joined": "2026-06-14T20:36:02.478393Z"
}
```

### Update Profile
```dart
Future<void> updateProfile(String token, Map<String, dynamic> updates) async {
  final response = await http.patch(
    Uri.parse('$baseUrl/auth/profile/'),
    headers: {
      'Authorization': 'Bearer $token',
      'Content-Type': 'application/json',
    },
    body: jsonEncode(updates),
  );
}
```

**Request example (PATCH):**
```json
{
  "full_name": "John Doe",
  "email": "john@example.com",
  "date_of_birth": "1995-06-15",
  "interests": [1, 3, 5]
}
```
> Note: `interests` is a list of **category IDs** (integers), not strings.

---

## 4. Home / Preload

**No auth required.** Cached in Redis for 5 minutes. This is the PRIMARY data source for the home screen — returns all shows with their episodes + categories + teasers in a single call.

```dart
Future<PreloadData> fetchPreload() async {
  final response = await http.get(
    Uri.parse('$baseUrl/home/preload/'),
  );
  if (response.statusCode == 200) {
    return PreloadData.fromJson(jsonDecode(response.body));
  }
  throw Exception('Failed to load preload');
}
```

**Complete Response Structure:**
```json
{
  "shows": [
    {
      "id": 1,
      "title": "Echoes of Darkness",
      "description": "A thrilling audio drama series...",
      "thumbnail": "shows/thumbnails/abc.jpg",
      "thumbnail_url": "https://r2.cloudflarestorage.com/...signed...",
      "category_name": "Thriller",
      "age_rating": "13+",
      "episodes": [
        {
          "id": 1,
          "title": "The Beginning",
          "sequence_number": 1,
          "duration_seconds": 3600,
          "audio_file_key": "uploads/audio/xyz.mp3",
          "hls_playlist_key": "uploads/hls/xyz.m3u8"
        }
      ]
    }
  ],
  "categories": [
    {
      "id": 1,
      "name": "Thriller",
      "slug": "thriller",
      "icon": null
    }
  ],
  "teasers": [
    {
      "id": 1,
      "title": "Coming Soon: New Show",
      "image": "teasers/images/abc.jpg",
      "image_url": "https://r2.cloudflarestorage.com/...signed...",
      "sequence": 0,
      "is_active": true,
      "is_converted": false,
      "created_at": "2026-06-27T..."
    }
  ]
}
```

**Dart data models:**
```dart
class PreloadData {
  final List<ShowSummary> shows;
  final List<Category> categories;
  final List<Teaser> teasers;
  // fromJson constructor...
}

class ShowSummary {
  final int id;
  final String title;
  final String? thumbnailUrl;
  final String categoryName;
  final String ageRating;
  final List<EpisodeSummary> episodes;
  // fromJson...
}

class Category {
  final int id;
  final String name;
  final String slug;
  final String? icon;
  // fromJson...
}

class EpisodeSummary {
  final int id;
  final String title;
  final int sequenceNumber;
  final int durationSeconds;
  final String? audioFileKey;
  final String? hlsPlaylistKey;
  // fromJson...
}
```

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
**Response:** `{ "featured": [...shows], "trending": [...shows], "recent": [...shows], "categories": [...] }`

### Weekly Trending (No Auth)
```dart
Future<List<dynamic>> fetchTrending() async {
  final response = await http.get(Uri.parse('$baseUrl/home/trending/'));
  final data = jsonDecode(response.body);
  return data['trending'];
}
```

---

## 5. Teasers (Coming Soon Cards)

Teasers are **standalone image cards** (no video). They represent upcoming/promotional content.
Teasers are **not linked to any show** until converted by admin.
Teasers that have been "converted to show" are filtered out (`is_converted: false` only).

### Data Source

Teasers come from the preload endpoint at the top level `"teasers": [...]`.

### Dart Model
```dart
class Teaser {
  final int id;
  final String title;
  final String? imageUrl;
  final int sequence;
  final bool isActive;
  final bool isConverted;
  final DateTime createdAt;

  Teaser({
    required this.id,
    required this.title,
    this.imageUrl,
    required this.sequence,
    required this.isActive,
    required this.isConverted,
    required this.createdAt,
  });

  factory Teaser.fromJson(Map<String, dynamic> json) {
    return Teaser(
      id: json['id'],
      title: json['title'],
      imageUrl: json['image_url'],
      sequence: json['sequence'] ?? 0,
      isActive: json['is_active'] ?? true,
      isConverted: json['is_converted'] ?? false,
      createdAt: DateTime.parse(json['created_at']),
    );
  }
}
```

### Flutter UI Flow

1. Extract teasers from preload response → filter `is_converted == false`
2. Sort by `sequence` ascending
3. Display as horizontal scrolling row on home screen (height ~200px)
4. Each card: teaser image with dark gradient overlay, title at bottom, "Coming Soon" chip
5. Tap → navigate to Teaser Detail Screen (full image view + title + notify button placeholder)

### Teaser Card Widget Pattern
```dart
Widget buildTeaserCard(Teaser teaser) {
  return GestureDetector(
    onTap: () => Navigator.push(context, TeaserDetailScreen(teaser: teaser)),
    child: Container(
      width: 160,
      margin: EdgeInsets.only(right: 12),
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(16),
        image: teaser.imageUrl != null
          ? DecorationImage(image: CachedNetworkImageProvider(teaser.imageUrl!), fit: BoxFit.cover)
          : null,
        gradient: teaser.imageUrl == null
          ? LinearGradient(from: Color(0xFF00D2FF), to: Color(0xFF7000FF))
          : null,
      ),
      child: Stack(
        children: [
          // Dark gradient overlay
          Positioned.fill(
            child: Container(
              decoration: BoxDecoration(
                borderRadius: BorderRadius.circular(16),
                gradient: LinearGradient(
                  begin: Alignment.topCenter, end: Alignment.bottomCenter,
                  colors: [Colors.transparent, Colors.black.withOpacity(0.7)],
                ),
              ),
            ),
          ),
          // "COMING SOON" badge
          Positioned(top: 8, right: 8, child: Badge(label: 'COMING SOON')),
          // Title at bottom
          Positioned(bottom: 12, left: 12, right: 12,
            child: Text(teaser.title, style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 13)),
          ),
        ],
      ),
    ),
  );
}
```

---

## 6. Shows & Episodes

### Get Episodes for a Show
```dart
Future<List<Episode>> fetchEpisodes(int showId, String token) async {
  final response = await http.get(
    Uri.parse('$baseUrl/shows/$showId/episodes/'),
    headers: {'Authorization': 'Bearer $token'},
  );
  if (response.statusCode == 200) {
    final List data = jsonDecode(response.body);
    return data.map((e) => Episode.fromJson(e)).toList();
  }
  throw Exception('Failed to load episodes');
}
```

**Response (list):**
```json
[
  {
    "id": 1,
    "show": 5,
    "title": "Episode 1",
    "description": "Episode description text",
    "duration_seconds": 600,
    "sequence_number": 1,
    "audio_file_key": "uploads/audio/abc.mp3",
    "audio_url": "https://e75d0e418e83eb4f77917abd63f8ec0f.r2.cloudflarestorage.com/...signed...",
    "hls_playlist_key": "",
    "created_at": "2026-06-17T..."
  }
]
```

### Dart Model
```dart
class Episode {
  final int id;
  final int show;
  final String title;
  final String description;
  final int durationSeconds;
  final int sequenceNumber;
  final String? audioUrl; // Signed R2 URL — use directly for streaming
  final String? audioFileKey;
  final String? hlsPlaylistKey;

  int get durationMinutes => durationSeconds ~/ 60;

  Episode({required this.id, required this.show, required this.title, ...});

  factory Episode.fromJson(Map<String, dynamic> json) {
    return Episode(
      id: json['id'],
      show: json['show'],
      title: json['title'],
      description: json['description'] ?? '',
      durationSeconds: json['duration_seconds'] ?? 0,
      sequenceNumber: json['sequence_number'] ?? 0,
      audioUrl: json['audio_url'],
      audioFileKey: json['audio_file_key'],
      hlsPlaylistKey: json['hls_playlist_key'],
    );
  }
}
```

---

## 7. Audio Streaming

The signed URL from `audio_url` can be used directly with `just_audio`. No extra endpoint call needed for streaming — `audio_url` is included in every episode response.

```dart
import 'package:just_audio/just_audio.dart';

final player = AudioPlayer();

Future<void> playEpisode(Episode episode) async {
  await player.stop();
  await player.setAudioSource(
    AudioSource.uri(Uri.parse(episode.audioUrl!)),
  );
  await player.play();
}
```

### Fallback: Get Fresh Signed URL
If the signed URL expires (valid for 1 hour), fetch a new one:
```dart
Future<String> getFreshAudioUrl(int episodeId, String token) async {
  final response = await http.get(
    Uri.parse('$baseUrl/play/ep/$episodeId/'),
    headers: {'Authorization': 'Bearer $token'},
  );
  final data = jsonDecode(response.body);
  return data['audio_url'];
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

> Note: If `hls_url` is not null, prefer HLS for better streaming. Otherwise use MP3 `audio_url`.

---

## 8. Interactions

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
  return data['is_liked'];
}
```
**Response:** `{ "is_liked": true, "message": "Liked" }`

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
**Response:** `{ "is_favorited": true, "message": "Added to favorites" }`

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
**Response:** `[{ "id": 1, "show": { full show object }, "created_at": "..." }]`

### Comments — Get for Episode
```dart
Future<List<dynamic>> getComments(int episodeId, String token) async {
  final response = await http.get(
    Uri.parse('$baseUrl/user/comments/?episode=$episodeId'),
    headers: {'Authorization': 'Bearer $token'},
  );
  return jsonDecode(response.body);
}
```
**Response:** `[{ "id": 1, "username": "John", "episode": 1, "text": "Great episode!", "created_at": "..." }]`

### Comments — Post
```dart
Future<void> postComment(int episodeId, String text, String token) async {
  await http.post(
    Uri.parse('$baseUrl/user/comments/'),
    headers: {
      'Authorization': 'Bearer $token',
      'Content-Type': 'application/json',
    },
    body: jsonEncode({'episode': episodeId, 'text': text}),
  );
}
```
**Request:** `{ "episode": 1, "text": "Great episode!" }`

### Feedback / Rating
```dart
Future<void> submitFeedback(int episodeId, int rating, String comment, String token) async {
  await http.post(
    Uri.parse('$baseUrl/user/feedback/'),
    headers: {
      'Authorization': 'Bearer $token',
      'Content-Type': 'application/json',
    },
    body: jsonEncode({'episode': episodeId, 'rating': rating, 'comment': comment}),
  );
}
```
**Request:** `{ "episode": 1, "rating": 4, "comment": "Loved it!" }`
> `rating` is 1-5 (integer).

---

## 9. Continue Playing (Resume)

### Update Playback Position
Call this every 30 seconds while the user is listening.

```dart
Future<void> updateResume(int episodeId, int positionSeconds, String token) async {
  await http.post(
    Uri.parse('$baseUrl/user/resume/update/'),
    headers: {
      'Authorization': 'Bearer $token',
      'Content-Type': 'application/json',
    },
    body: jsonEncode({
      'episode_id': episodeId,
      'last_position_seconds': positionSeconds,
    }),
  );
}
```

**Request:** `{ "episode_id": 1, "last_position_seconds": 1800 }`

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

**Response:**
```json
[
  {
    "id": 1,
    "episode": { "id": 5, "title": "Ep 3", "show": 2, "audio_url": "...", ... },
    "last_position_seconds": 1800,
    "updated_at": "2026-06-27T..."
  }
]
```

> Use `last_position_seconds` to show "Continue from 30:00" button and seek the player to that position.

---

## 10. Analytics

### Track Play Hit
Send this when user starts or finishes an episode.

```dart
Future<void> trackPlay(int episodeId, String token) async {
  await http.post(
    Uri.parse('$baseUrl/analytics/hit/'),
    headers: {
      'Authorization': 'Bearer $token',
      'Content-Type': 'application/json',
    },
    body: jsonEncode({'episode_id': episodeId}),
  );
}
```

**Request:** `{ "episode_id": 1 }`

---

## 11. Collaboration

### Story Submission
```dart
Future<Map<String, dynamic>> submitStory(String title, String content, String token) async {
  final response = await http.post(
    Uri.parse('$baseUrl/collab/story/submit/'),
    headers: {
      'Authorization': 'Bearer $token',
      'Content-Type': 'application/json',
    },
    body: jsonEncode({'title': title, 'content': content}),
  );
  return jsonDecode(response.body);
}
```
**Response:** `{ "id": 1, "title": "...", "status": "pending", "created_at": "..." }`

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
**Response:** `[{ "id": 1, "username": "9999999999", "title": "...", "content": "...", "status": "pending", "rejection_reason": null, "created_at": "..." }]`
> Statuses: `pending`, `reviewing`, `approved`, `rejected`

### Sponsorship / Ad Request
```dart
Future<Map<String, dynamic>> submitAd({
  required String brandName,
  required String description,
  String? targetUrl,
  String? imagePath,
  required String token,
}) async {
  final request = http.MultipartRequest(
    'POST',
    Uri.parse('$baseUrl/collab/ads/submit/'),
  );
  request.headers['Authorization'] = 'Bearer $token';
  request.fields['brand_name'] = brandName;
  request.fields['description'] = description;
  if (targetUrl != null) request.fields['target_url'] = targetUrl;
  if (imagePath != null) {
    request.files.add(await http.MultipartFile.fromPath('ad_visual', imagePath));
  }
  final streamedResponse = await request.send();
  final response = await http.Response.fromStream(streamedResponse);
  return jsonDecode(response.body);
}
```
**Response:** `{ "id": 1, "brand_name": "...", "status": "pending" }`

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
**Response:** `[{ "id": 1, "brand_name": "...", "description": "...", "ad_visual": null, "target_url": null, "status": "pending", "created_at": "..." }]`

---

## 12. Ads & Reports

### Report an Ad
```dart
Future<void> reportAd(int adId, String reason, String token) async {
  await http.post(
    Uri.parse('$baseUrl/ads/report/'),
    headers: {
      'Authorization': 'Bearer $token',
      'Content-Type': 'application/json',
    },
    body: jsonEncode({'ad': adId, 'reason': reason}),
  );
}
```

**Request:** `{ "ad": 1, "reason": "Inappropriate content" }`

---

## 13. Token Refresh

When any API returns 401, try to refresh the token:

```dart
Future<String?> refreshAccessToken(String refreshToken) async {
  final urls = [
    '$baseUrl/admin/token/refresh/',
    '$baseUrl/token/refresh/',
    '$baseUrl/admin/refresh/',
  ];
  for (final url in urls) {
    try {
      final response = await http.post(
        Uri.parse(url),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({'refresh': refreshToken}),
      );
      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        return data['access'];
      }
    } catch (_) {}
  }
  return null; // All failed — logout user
}
```

**Full interceptor pattern (dio example):**
```dart
import 'package:dio/dio.dart';

class AuthInterceptor extends Interceptor {
  @override
  void onError(DioException err, ErrorInterceptorHandler handler) async {
    if (err.response?.statusCode == 401) {
      final refreshToken = await storage.read('refresh_token');
      if (refreshToken != null) {
        final newAccess = await refreshAccessToken(refreshToken);
        if (newAccess != null) {
          await storage.write('access_token', newAccess);
          err.requestOptions.headers['Authorization'] = 'Bearer $newAccess';
          final response = await Dio().fetch(err.requestOptions);
          return handler.resolve(response);
        }
      }
      // Logout
      await storage.remove('access_token');
      await storage.remove('refresh_token');
    }
    return handler.next(err);
  }
}
```

---

## 14. Quick Reference — All Endpoints

| # | Method | Endpoint | Auth | Description |
|---|--------|----------|------|-------------|
| 1 | POST | `/auth/send-otp/` | ❌ | Send OTP (dev: returns OTP for 9999999999) |
| 2 | POST | `/auth/verify-otp/` | ❌ | Verify OTP → JWT access + refresh tokens |
| 3 | GET | `/auth/profile/` | ✅ | Get user profile |
| 4 | PATCH | `/auth/profile/` | ✅ | Update user profile |
| 5 | GET | `/home/preload/` | ❌ | **Main data**: shows + episodes + categories + teasers |
| 6 | GET | `/home/` | ✅ | Authenticated home (featured + trending + recent) |
| 7 | GET | `/home/trending/` | ❌ | Weekly trending shows |
| 8 | GET | `/shows/<id>/episodes/` | ✅ | Episodes for a show (with `audio_url` signed URLs) |
| 9 | GET | `/play/ep/<id>/` | ✅ | Get fresh signed audio URL (fallback) |
| 10 | POST | `/user/like/toggle/` | ✅ | Like/unlike episode |
| 11 | POST | `/user/favorite/toggle/` | ✅ | Favorite/unfavorite show |
| 12 | GET | `/user/favorites/` | ✅ | List favorite shows |
| 13 | GET | `/user/comments/?episode=<id>` | ✅ | Get comments for episode |
| 14 | POST | `/user/comments/` | ✅ | Post a comment |
| 15 | POST | `/user/feedback/` | ✅ | Submit episode rating (1-5) |
| 16 | POST | `/user/resume/update/` | ✅ | Save playback position |
| 17 | GET | `/user/resume/` | ✅ | Get resume list (continue watching) |
| 18 | POST | `/analytics/hit/` | ✅ | Track episode play |
| 19 | POST | `/collab/story/submit/` | ✅ | Submit a story |
| 20 | GET | `/collab/stories/` | ✅ | My submitted stories |
| 21 | POST | `/collab/ads/submit/` | ✅ | Submit sponsorship/ad (FormData with image) |
| 22 | GET | `/collab/ads/` | ✅ | My submitted ads |
| 23 | POST | `/ads/report/` | ✅ | Report an ad |

---

## 15. Flutter App Navigation Flow

```
App Start
  │
  ├─ Check stored tokens
  │   ├─ Valid → Home Screen
  │   └─ Expired/None → Login
  │
  Login Flow
  │  ├─ Phone Entry Screen
  │  │   └─ POST /auth/send-otp/
  │  ├─ OTP Screen
  │  │   └─ POST /auth/verify-otp/ → save tokens
  │  └─ Profile (optional) → PATCH /auth/profile/
  │
  Home Screen (Bottom Tab 1)
  │  ├─ GET /home/preload/ (no auth)
  │  ├─ Teaser Row (horizontal scroll)
  │  │   └─ Tap teaser → Teaser Detail Screen (full image)
  │  ├─ Featured Shows Row
  │  ├─ Trending Shows Row
  │  ├─ Recent Shows Row
  │  └─ Tap Show → Show Detail Screen
  │
  Show Detail Screen
  │  ├─ Show info (title, description, category badge)
  │  ├─ POST /user/favorite/toggle/ (heart icon)
  │  ├─ GET /shows/<id>/episodes/ → episode list
  │  └─ Tap Episode → Player Screen
  │
  Player Screen (Full-screen or bottom sheet)
  │  ├─ GET /play/ep/<id>/ (get signed URL)
  │  ├─ just_audio → stream audio
  │  ├─ POST /user/resume/update/ (every 30s)
  │  ├─ POST /analytics/hit/ (on start/finish)
  │  ├─ POST /user/like/toggle/ (heart icon)
  │  ├─ Comments section
  │  │   ├─ GET /user/comments/?episode=<id>
  │  │   └─ POST /user/comments/
  │  └─ Feedback → POST /user/feedback/
  │
  Search (Bottom Tab 2)
  │  └─ Search shows → filter preload locally or via API
  │
  My Library (Bottom Tab 3)
  │  ├─ Favorites → GET /user/favorites/
  │  ├─ Continue Playing → GET /user/resume/
  │  └─ My Submissions
  │      ├─ Stories → GET /collab/stories/
  │      └─ Ads → GET /collab/ads/
  │
  Profile (Bottom Tab 4)
  │  ├─ GET /auth/profile/
  │  └─ Edit → PATCH /auth/profile/
  │
  Collaboration
  │  ├─ Submit Story → POST /collab/story/submit/
  │  └─ Submit Ad → POST /collab/ads/submit/ (FormData)
```

---

## Image & Placeholder Guide

| Scenario | What to Show |
|----------|-------------|
| Show has `thumbnail_url` | `CachedNetworkImage(url: thumbnailUrl)` |
| No show thumbnail | Gradient placeholder (`from #00D2FF to #7000FF`) + Film icon |
| Teaser has `image_url` | `CachedNetworkImage(url: imageUrl)` with dark overlay |
| No teaser image | Gradient placeholder (`from #00D2FF to #7000FF`) + Image icon |
| User has `profile_picture` | Circle avatar with cached image |
| No profile picture | Circle with first letter of `full_name` (white on gradient bg) |
| Episode has `audio_url` | Play button + AudioPlayer |
| Episode URL expired | Fetch new URL from `GET /play/ep/<id>/` |

---

## Important Notes

- **All signed URLs expire in 1 hour** — handle 403 errors by fetching fresh URLs
- **Preload is cached** (5 min Redis + 5 min client-side) — refresh on pull-to-refresh
- **Dev mode**: `ENABLE_DEV_LOGIN=True`, whitelisted phone `9999999999`, OTP always `123456`
- **MSG91 is live** for all other phone numbers (real SMS OTP)
- **JWT tokens**: `access` (short-lived, use for API calls), `refresh` (long-lived, use to get new access)
- **Audio streaming**: direct R2 signed URLs, no HLS conversion needed — MP3 works great
