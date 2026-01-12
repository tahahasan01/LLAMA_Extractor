# Backend-Frontend Alignment Changes

## Overview
Updated the backend API to match the frontend's Movie interface and data expectations.

## Frontend Requirements Analysis

### Movie Interface (TypeScript)
```typescript
interface Movie {
  id: number;
  title: string;
  poster: string;          // Full URL
  backdrop?: string;       // Full URL
  rating: number;          // 0-10 scale
  genres: string[];        // Array of genre names
  year: number;            // Release year
  platforms: StreamingPlatform[];
  overview?: string;
  runtime?: number;
  director?: string;
  cast?: string[];
  trailer?: string;        // YouTube URL
}

interface StreamingPlatform {
  name: string;
  color: string;           // Brand hex color
}
```

### Rating System
- Frontend uses **5-star rating** (0-5 scale)
- Backend converts to **10-point scale** internally for TMDb compatibility

## Backend Changes Made

### 1. ChatService (`services/chat_service.py`)

#### Updated `_format_movie()` method:
- Returns `poster` and `backdrop` as full URLs (not just paths)
- Returns `rating` in 0-10 scale (TMDb format)
- Returns `genres` as array of strings (genre names, not IDs)
- Returns `year` as integer extracted from release_date
- Added `platforms` array with streaming service info
- Added `overview`, `runtime`, `director`, `cast`, `trailer` fields
- Calls TMDb API to fetch streaming providers

#### Added `_get_platform_color()` helper:
- Maps streaming platform names to brand colors
- Supports Netflix, Prime Video, Disney+, HBO Max, Hulu, etc.

#### Updated `_cache_movie()` method:
- Handles new movie format for database caching
- Stores genres as comma-separated string

### 2. Flask App (`app.py`)

#### Updated `/api/chat` endpoint:
- Made `user_id` **optional** (defaults to 1)
- Frontend doesn't require user authentication initially
- Only `message` field is required

#### Updated `/api/rate` endpoint:
- Made `user_id` **optional** (defaults to 1)
- Accepts **5-star rating** (0-5 scale)
- **Converts to 10-point scale** internally (rating * 2)
- Validates rating range 0-5 instead of 1-5
- Gracefully handles recommender training failures

#### Updated `/api/movie/<id>` endpoint:
- Returns **full movie details** in frontend format
- Fetches credits (cast, director) from TMDb
- Fetches videos (trailer) from TMDb
- Fetches streaming platforms
- Returns formatted response matching Movie interface
- Added error handling with traceback logging

#### Added `get_platform_color()` helper function:
- Shared utility for platform color mapping
- Used by movie details endpoint

### 3. TMDb Service (`services/tmdb_service.py`)

#### Updated `get_movie_details()`:
- Simplified to return raw TMDb data
- Includes `append_to_response=credits,videos,keywords`
- Frontend formatting happens in Flask app layer

#### Updated `get_watch_providers()`:
- Returns full provider data structure
- No longer filters to single region in service
- Region filtering done in API endpoint layer

## API Response Examples

### Chat Response
```json
{
  "reply": "Here are some great action movies for you! 🍿",
  "movies": [
    {
      "id": 550,
      "title": "Fight Club",
      "poster": "https://image.tmdb.org/t/p/w500/pB8BM7pdSp6B6Ih7QZ4DrQ3PmJK.jpg",
      "backdrop": "https://image.tmdb.org/t/p/original/fCayJrkfRaCRCTh8GqN30f8oyQF.jpg",
      "rating": 8.4,
      "genres": ["Drama", "Thriller", "Comedy"],
      "year": 1999,
      "platforms": [
        {"name": "Netflix", "color": "#E50914"},
        {"name": "Amazon Prime Video", "color": "#00A8E1"}
      ],
      "overview": "A ticking-time-bomb insomniac...",
      "runtime": 139,
      "director": null,
      "cast": [],
      "trailer": null
    }
  ],
  "intent": "genre_search",
  "entities": {"genre": "action"}
}
```

### Movie Details Response
```json
{
  "id": 550,
  "title": "Fight Club",
  "poster": "https://image.tmdb.org/t/p/w500/pB8BM7pdSp6B6Ih7QZ4DrQ3PmJK.jpg",
  "backdrop": "https://image.tmdb.org/t/p/original/fCayJrkfRaCRCTh8GqN30f8oyQF.jpg",
  "rating": 8.4,
  "genres": ["Drama", "Thriller", "Comedy"],
  "year": 1999,
  "platforms": [
    {"name": "Netflix", "color": "#E50914"}
  ],
  "overview": "A ticking-time-bomb insomniac and a slippery soap salesman...",
  "runtime": 139,
  "director": "David Fincher",
  "cast": ["Brad Pitt", "Edward Norton", "Helena Bonham Carter", "Meat Loaf", "Jared Leto"],
  "trailer": "https://www.youtube.com/watch?v=SUXWAEX2jlg"
}
```

### Rating Request
```json
{
  "movie_id": 550,
  "rating": 4.5  // 5-star scale (0-5)
}
// Stored internally as 9.0 (10-point scale)
```

## Breaking Changes

### Changed:
1. `poster_url` → `poster` (full URL)
2. `backdrop_url` → `backdrop` (full URL)
3. `vote_average` → `rating` (0-10 scale)
4. `genre_ids` → `genres` (array of strings)
5. `release_date` → `year` (integer)

### Added:
1. `platforms` array (streaming services)
2. `runtime` (minutes)
3. `director` (string)
4. `cast` (array of actor names)
5. `trailer` (YouTube URL)

### Optional Fields:
1. `user_id` now defaults to 1 if not provided

## Database Compatibility

All changes are **backward compatible** with existing database:
- Ratings stored in 10-point scale (0-10)
- User IDs still tracked normally
- Movie cache format updated to handle new fields
- Graceful fallback if fields missing

## Testing Recommendations

1. **Test chat endpoint** with various queries:
   - "action movies"
   - "movies like Inception"
   - "Tom Cruise movies"
   - "trending now"

2. **Test movie details** endpoint:
   - Verify all fields present
   - Check platform colors correct
   - Verify trailer URLs work

3. **Test rating** endpoint:
   - Submit 5-star ratings
   - Verify conversion to 10-point scale
   - Check database storage

4. **Test without user_id**:
   - Send chat messages without user_id
   - Send ratings without user_id
   - Verify default user_id=1 used

## Next Steps

When frontend connects:
1. Update frontend API base URL to backend server
2. Replace mock data with real API calls
3. Test end-to-end flow
4. Add error handling for network failures
5. Add loading states during API calls
