# Movie Recommendation Chatbot Backend

A complete movie recommendation chatbot backend with ML capabilities, built using Flask, TMDb API, and scikit-learn.

## Features

✅ **TMDb API Integration** - Search movies, get details, trending content, and streaming providers  
✅ **Intelligent Chat Service** - Parse user messages and understand intent  
✅ **Content-Based Filtering** - Recommend similar movies using TF-IDF and cosine similarity  
✅ **Collaborative Filtering** - Personalized recommendations using K-Nearest Neighbors  
✅ **Hybrid Recommendations** - Combine both ML approaches for better results  
✅ **SQLite Database** - Store user ratings, preferences, and movie cache  
✅ **RESTful API** - Well-documented endpoints for easy frontend integration  
✅ **Rate Limiting** - Respect TMDb API limits with built-in throttling  

## Tech Stack

- **Backend**: Python 3.8+ with Flask
- **Database**: SQLite
- **ML**: Scikit-learn, Pandas, NumPy
- **API**: TMDb API (free tier)
- **NLP**: Regex-based intent parsing

## Project Structure

```
movie-chatbot-backend/
├── app.py                    # Main Flask application
├── config.py                 # Configuration settings
├── requirements.txt          # Python dependencies
├── database/
│   ├── db.py                # Database operations
│   └── schema.sql           # Database schema
├── services/
│   ├── tmdb_service.py      # TMDb API integration
│   ├── chat_service.py      # Chat logic and responses
│   └── recommender.py       # ML recommendation engines
├── models/
│   ├── user.py              # User models
│   └── movie.py             # Movie models
├── utils/
│   ├── helpers.py           # Utility functions
│   └── intent_parser.py     # Message intent parsing
└── tests/
    ├── test_tmdb.py         # TMDb service tests
    └── test_recommender.py  # Recommender tests
```

## Installation

### 1. Clone the repository

```bash
git clone <repository-url>
cd movie-chatbot-backend
```

### 2. Create virtual environment

```bash
python -m venv venv
```

### 3. Activate virtual environment

**Windows:**
```bash
venv\Scripts\activate
```

**macOS/Linux:**
```bash
source venv/bin/activate
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

### 5. Configure API key

1. Get your free TMDb API key from [https://www.themoviedb.org/settings/api](https://www.themoviedb.org/settings/api)
2. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```
3. Edit `.env` and add your API key:
   ```
   TMDB_API_KEY=your_actual_api_key_here
   ```

### 6. Run the application

```bash
python app.py
```

The server will start on `http://localhost:5000`

## API Endpoints

### 1. Chat with Bot
```http
POST /api/chat
Content-Type: application/json

{
  "user_id": 1,
  "message": "I want action movies like John Wick"
}
```

**Response:**
```json
{
  "reply": "Here are some action movies you might enjoy!",
  "movies": [...],
  "intent": "similar_movie"
}
```

### 2. Rate a Movie
```http
POST /api/rate
Content-Type: application/json

{
  "user_id": 1,
  "movie_id": 550,
  "rating": 4.5
}
```

### 3. Get Recommendations
```http
GET /api/recommendations/1?limit=10
```

### 4. Search Movies
```http
GET /api/search?query=inception&genre=action&year=2010
```

### 5. Get Movie Details
```http
GET /api/movie/550
```

### 6. Get Streaming Providers
```http
GET /api/movie/550/providers?region=US
```

### 7. Get User Profile
```http
GET /api/user/1
```

### 8. Create User
```http
POST /api/user
Content-Type: application/json

{
  "username": "john_doe"
}
```

### 9. Get Genres
```http
GET /api/genres
```

### 10. Get Trending Movies
```http
GET /api/trending?time_window=week
```

## Chat Examples

The chatbot understands various types of queries:

**Genre Search:**
- "I want action movies"
- "Show me horror films"
- "Looking for comedy"

**Actor Search:**
- "Movies with Tom Cruise"
- "Films starring Meryl Streep"

**Similar Movies:**
- "Movies like Inception"
- "Similar to The Dark Knight"

**Mood/Theme:**
- "Something scary"
- "Feel-good movies"
- "Suspenseful films"

**Trending:**
- "What's popular?"
- "Trending movies"
- "What's everyone watching?"

**Time Period:**
- "90s movies"
- "Recent films"
- "Movies from 2020"

## Database Schema

### Users Table
- `user_id` (Primary Key)
- `username` (Unique)
- `created_at` (Timestamp)

### Ratings Table
- `rating_id` (Primary Key)
- `user_id` (Foreign Key)
- `movie_id`
- `rating` (1-5)
- `timestamp`

### Movies Cache Table
- `movie_id` (Primary Key)
- `title`, `genres`, `poster_path`, `overview`
- `vote_average`, `release_date`, `popularity`
- `cached_at` (Timestamp)

### User Preferences Table
- `user_id` (Primary Key)
- `favorite_genres`, `favorite_actors`
- `updated_at`

## ML Recommendation System

### Content-Based Filtering
- Uses TF-IDF vectorization on movie genres, overview, and metadata
- Calculates cosine similarity between movies
- Recommends similar movies based on content features

### Collaborative Filtering
- Builds user-item rating matrix
- Uses K-Nearest Neighbors to find similar users
- Recommends movies liked by similar users

### Hybrid Approach
- Combines 60% collaborative + 40% content-based recommendations
- Boosts recommendations by popularity and recency
- Provides best results when sufficient rating data exists

## Testing

Run tests with:

```bash
# Run all tests
python -m unittest discover tests

# Run specific test file
python -m unittest tests.test_tmdb
python -m unittest tests.test_recommender
```

## Configuration

Edit `config.py` to customize:

- `TMDB_API_KEY` - Your TMDb API key
- `DATABASE_PATH` - SQLite database location
- `DEFAULT_RECOMMENDATIONS` - Number of recommendations
- `CACHE_EXPIRY_HOURS` - How long to cache TMDb data
- `COLLABORATIVE_WEIGHT` / `CONTENT_BASED_WEIGHT` - Hybrid model weights

## Error Handling

The backend handles:
- TMDb API rate limits (4 requests/second)
- Invalid movie IDs
- Empty search results
- Missing user data
- Database errors

## Caching Strategy

- TMDb responses are cached for 24 hours
- Reduces API calls and improves response time
- Cached data stored in SQLite database
- Automatic cleanup of expired cache

## Production Deployment

For production:

1. Set `DEBUG = False` in `config.py`
2. Use a production WSGI server (e.g., Gunicorn):
   ```bash
   pip install gunicorn
   gunicorn -w 4 -b 0.0.0.0:5000 app:app
   ```
3. Set up proper environment variables
4. Use PostgreSQL instead of SQLite for better concurrency
5. Add authentication and rate limiting
6. Set up HTTPS
7. Monitor with logging and error tracking

## API Rate Limits

TMDb API limits:
- 40 requests per 10 seconds
- The backend implements throttling to stay within limits

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

MIT License - feel free to use this project for learning and development.

## Support

For issues and questions:
- Open an issue on GitHub
- Check TMDb API documentation: https://developers.themoviedb.org/3

## Acknowledgments

- TMDb for providing the free movie database API
- Flask and scikit-learn communities
- All contributors to this project

---

**Happy movie recommending! 🎬🍿**
