from flask import Flask, request, jsonify
from flask_cors import CORS
from config import Config
from database import get_db
from services.tmdb_service import get_tmdb_service
from services.chat_service import get_chat_service
from services.recommender import get_recommender
from typing import Dict


# Initialize Flask app
app = Flask(__name__)
app.config.from_object(Config)
CORS(app)

# Initialize services
db = get_db()
tmdb = get_tmdb_service()
chat_service = get_chat_service()

# Initialize recommender without training (will train on first use)
from services.recommender import HybridRecommender
recommender = HybridRecommender()


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def format_movie_for_frontend(movie: Dict) -> Dict:
    """Format movie data to match frontend Movie interface"""
    # Get genre names
    genre_ids = movie.get('genre_ids', [])
    genres = []
    if genre_ids:
        genres_data = tmdb.get_genres()
        if genres_data and 'genres' in genres_data:
            genre_map = {g['id']: g['name'] for g in genres_data['genres']}
            genres = [genre_map.get(gid) for gid in genre_ids if gid in genre_map]
    
    return {
        'id': movie.get('id'),
        'title': movie.get('title'),
        'poster': f"https://image.tmdb.org/t/p/w500{movie.get('poster_path')}" if movie.get('poster_path') else 'https://via.placeholder.com/500x750/1a1a2e/eee?text=No+Poster',
        'backdrop': f"https://image.tmdb.org/t/p/original{movie.get('backdrop_path')}" if movie.get('backdrop_path') else None,
        'rating': round(movie.get('vote_average', 0), 1),
        'genres': genres,
        'year': int(movie.get('release_date', '')[:4]) if movie.get('release_date') else None,
        'platforms': [],
        'overview': movie.get('overview'),
        'runtime': movie.get('runtime'),
        'director': None,
        'cast': [],
        'trailer': None
    }


# ============================================================================
# API ENDPOINTS
# ============================================================================

@app.route('/api/chat', methods=['POST'])
def chat():
    """
    Handle chat messages and return movie recommendations
    
    Request Body:
        {
            "user_id": 1,  // Optional, defaults to 1
            "message": "I want action movies like John Wick"
        }
    
    Response:
        {
            "reply": "Here are some action movies you might enjoy!",
            "movies": [...],
            "intent": "movie_search"
        }
    """
    try:
        data = request.get_json()
        
        if not data or 'message' not in data:
            return jsonify({
                'error': 'Missing required field: message'
            }), 400
        
        # Default user_id to 1 if not provided (for frontend compatibility)
        user_id = data.get('user_id', 1)
        message = data['message']
        
        # Process the message
        response = chat_service.process_message(user_id, message)
        
        return jsonify(response), 200
    
    except Exception as e:
        print(f"Error in /api/chat: {e}")
        return jsonify({'error': 'Internal server error'}), 500


@app.route('/api/rate', methods=['POST'])
def rate_movie():
    """
    Save or update a movie rating
    
    Request Body:
        {
            "user_id": 1,  // Optional, defaults to 1
            "movie_id": 550,
            "rating": 4.5  // 5-star scale (1-5)
        }
    
    Response:
        {
            "success": true,
            "message": "Rating saved"
        }
    """
    try:
        data = request.get_json()
        
        if not data or 'movie_id' not in data or 'rating' not in data:
            return jsonify({
                'error': 'Missing required fields: movie_id and rating'
            }), 400
        
        user_id = data.get('user_id', 1)  # Default to 1 for frontend compatibility
        movie_id = data['movie_id']
        rating = float(data['rating'])
        
        # Validate rating (5-star scale)
        if rating < 0 or rating > 5:
            return jsonify({
                'error': 'Rating must be between 0 and 5'
            }), 400
        
        # Convert 5-star rating to 10-point scale for internal storage
        rating_10_scale = rating * 2
        
        # Save rating
        success = db.add_rating(user_id, movie_id, rating_10_scale)
        
        if success:
            # Retrain recommender with new rating
            # (In production, do this asynchronously)
            try:
                recommender.train()
            except:
                pass  # Don't fail if training fails
            
            return jsonify({
                'success': True,
                'message': 'Rating saved successfully'
            }), 200
        else:
            return jsonify({
                'error': 'Failed to save rating'
            }), 500
    
    except ValueError:
        return jsonify({'error': 'Invalid rating value'}), 400
    except Exception as e:
        print(f"Error in /api/rate: {e}")
        return jsonify({'error': 'Internal server error'}), 500


@app.route('/api/recommendations/<int:user_id>', methods=['GET'])
def get_recommendations(user_id: int):
    """
    Get personalized recommendations for a user
    
    Query Parameters:
        limit: Number of recommendations (default: 10)
        movie_id: Optional reference movie for content-based filtering
    
    Response:
        {
            "movies": [...],
            "method": "hybrid"
        }
    """
    try:
        limit = request.args.get('limit', default=10, type=int)
        movie_id = request.args.get('movie_id', default=None, type=int)
        
        # Validate limit
        if limit < 1 or limit > 50:
            limit = 10
        
        # Check if user exists
        user = db.get_user(user_id)
        if not user:
            return jsonify({
                'error': 'User not found'
            }), 404
        
        # Get user rating count
        rating_count = db.get_user_rating_count(user_id)
        
        # Get recommendations
        if rating_count < Config.MIN_RATINGS_FOR_COLLABORATIVE:
            # New user - use trending/popular movies
            movies = recommender.get_recommendations_for_new_user(n=limit)
            method = 'popular'
        else:
            # Existing user - use hybrid recommendations
            movies = recommender.recommend(user_id, n=limit, movie_id=movie_id)
            method = 'hybrid'
        
        return jsonify({
            'movies': movies,
            'method': method,
            'count': len(movies)
        }), 200
    
    except Exception as e:
        print(f"Error in /api/recommendations: {e}")
        return jsonify({'error': 'Internal server error'}), 500


@app.route('/api/search', methods=['GET'])
def search_movies():
    """
    Search for movies with filters
    
    Query Parameters:
        query: Search query
        genre: Genre name
        year: Release year
        min_rating: Minimum rating
        page: Page number
    
    Response:
        {
            "movies": [...],
            "total_results": 25,
            "page": 1
        }
    """
    try:
        query = request.args.get('query', default=None, type=str)
        genre = request.args.get('genre', default=None, type=str)
        year = request.args.get('year', default=None, type=int)
        min_rating = request.args.get('min_rating', default=None, type=float)
        page = request.args.get('page', default=1, type=int)
        
        # Search or discover movies
        if query:
            # Text search
            result = tmdb.search_movies(query, page=page)
        elif genre or year or min_rating:
            # Filtered discovery
            genre_id = tmdb.get_genre_id(genre) if genre else None
            result = tmdb.discover_movies(
                genre=genre_id,
                year=year,
                min_rating=min_rating,
                page=page
            )
        else:
            # Default to popular movies
            result = tmdb.get_popular_movies(page=page)
        
        if not result:
            return jsonify({
                'movies': [],
                'total_results': 0,
                'page': page
            }), 200
        
        # Format movies
        movies = [tmdb.format_movie_data(m) for m in result.get('results', [])]
        
        return jsonify({
            'movies': movies,
            'total_results': result.get('total_results', 0),
            'page': result.get('page', page),
            'total_pages': result.get('total_pages', 1)
        }), 200
    
    except Exception as e:
        print(f"Error in /api/search: {e}")
        return jsonify({'error': 'Internal server error'}), 500


@app.route('/api/movie/<int:movie_id>', methods=['GET'])
def get_movie_details(movie_id: int):
    """
    Get detailed information about a movie with full details
    (cast, director, trailer, streaming platforms)
    
    Response:
        {
            "id": 550,
            "title": "Fight Club",
            "poster": "https://...",
            "backdrop": "https://...",
            "rating": 8.4,
            "genres": ["Drama", "Thriller"],
            "year": 1999,
            "platforms": [...],
            "overview": "...",
            "runtime": 139,
            "director": "David Fincher",
            "cast": ["Brad Pitt", "Edward Norton"],
            "trailer": "https://youtube.com/..."
        }
    """
    try:
        # Fetch full details from TMDb with append_to_response
        movie = tmdb.get_movie_details(movie_id)
        
        if not movie:
            return jsonify({
                'error': 'Movie not found'
            }), 404
        
        # Get streaming providers
        platforms = []
        try:
            providers_data = tmdb.get_watch_providers(movie_id)
            if providers_data and 'results' in providers_data:
                us_providers = providers_data['results'].get('US', {})
                link = us_providers.get('link')  # TMDb watch link
                flatrate = us_providers.get('flatrate', [])
                for provider in flatrate[:5]:
                    platforms.append({
                        'name': provider.get('provider_name'),
                        'color': get_platform_color(provider.get('provider_name')),
                        'link': link  # Same TMDb link for all providers
                    })
        except:
            pass
        
        # Extract cast from credits
        cast = []
        if movie.get('credits') and movie['credits'].get('cast'):
            cast = [person.get('name') for person in movie['credits']['cast'][:10]]
        
        # Extract director from credits
        director = None
        if movie.get('credits') and movie['credits'].get('crew'):
            for person in movie['credits']['crew']:
                if person.get('job') == 'Director':
                    director = person.get('name')
                    break
        
        # Extract trailer from videos
        trailer = None
        if movie.get('videos') and movie['videos'].get('results'):
            for video in movie['videos']['results']:
                if video.get('type') == 'Trailer' and video.get('site') == 'YouTube':
                    trailer = f"https://www.youtube.com/watch?v={video.get('key')}"
                    break
        
        # Format response for frontend
        formatted_movie = {
            'id': movie_id,
            'title': movie.get('title'),
            'poster': f"https://image.tmdb.org/t/p/w500{movie.get('poster_path')}" if movie.get('poster_path') else 'https://via.placeholder.com/500x750/1a1a2e/eee?text=No+Poster',
            'backdrop': f"https://image.tmdb.org/t/p/original{movie.get('backdrop_path')}" if movie.get('backdrop_path') else None,
            'rating': round(movie.get('vote_average', 0), 1),
            'genres': [g.get('name') for g in movie.get('genres', [])],
            'year': int(movie.get('release_date', '')[:4]) if movie.get('release_date') else None,
            'platforms': platforms,
            'overview': movie.get('overview'),
            'runtime': movie.get('runtime'),
            'director': director,
            'cast': cast,
            'trailer': trailer
        }
        
        return jsonify(formatted_movie), 200
    
    except Exception as e:
        print(f"Error in /api/movie/{movie_id}: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': 'Internal server error'}), 500


def get_platform_color(platform_name: str) -> str:
    """Get brand color for streaming platform"""
    colors = {
        'Netflix': '#E50914',
        'Amazon Prime Video': '#00A8E1',
        'Disney Plus': '#113CCF',
        'HBO Max': '#5822B4',
        'Hulu': '#1CE783',
        'Apple TV Plus': '#000000',
        'Paramount+': '#0064FF',
        'Peacock': '#000000'
    }
    return colors.get(platform_name, '#666666')


@app.route('/api/movie/<int:movie_id>/providers', methods=['GET'])
def get_streaming_providers(movie_id: int):
    """
    Get streaming availability for a movie
    
    Query Parameters:
        region: Country code (default: US)
    
    Response:
        {
            "movie_id": 550,
            "providers": {
                "flatrate": [...],
                "rent": [...],
                "buy": [...]
            }
        }
    """
    try:
        region = request.args.get('region', default='US', type=str)
        
        providers = tmdb.get_watch_providers(movie_id, region=region)
        
        if not providers:
            return jsonify({
                'movie_id': movie_id,
                'providers': {},
                'message': 'No streaming information available'
            }), 200
        
        return jsonify({
            'movie_id': movie_id,
            'providers': providers,
            'region': region
        }), 200
    
    except Exception as e:
        print(f"Error in /api/movie/{movie_id}/providers: {e}")
        return jsonify({'error': 'Internal server error'}), 500


@app.route('/api/user/<int:user_id>', methods=['GET'])
def get_user_profile(user_id: int):
    """
    Get user profile and statistics
    
    Response:
        {
            "user_id": 1,
            "username": "john_doe",
            "total_ratings": 45,
            "average_rating": 4.2,
            "favorite_genres": ["Action", "Sci-Fi"],
            "recent_ratings": [...]
        }
    """
    try:
        user = db.get_user(user_id)
        
        if not user:
            return jsonify({
                'error': 'User not found'
            }), 404
        
        # Get user stats
        stats = db.get_user_stats(user_id)
        
        # Get recent ratings
        recent_ratings = db.get_user_ratings(user_id)[:10]
        
        # Get preferences
        preferences = db.get_user_preferences(user_id)
        
        return jsonify({
            'user_id': user['user_id'],
            'username': user['username'],
            'created_at': user['created_at'],
            'total_ratings': stats['total_ratings'],
            'average_rating': stats['average_rating'],
            'top_genres': stats['top_genres'],
            'recent_ratings': recent_ratings,
            'preferences': preferences
        }), 200
    
    except Exception as e:
        print(f"Error in /api/user/{user_id}: {e}")
        return jsonify({'error': 'Internal server error'}), 500


@app.route('/api/user', methods=['POST'])
def create_user():
    """
    Create a new user
    
    Request Body:
        {
            "username": "john_doe"
        }
    
    Response:
        {
            "user_id": 1,
            "username": "john_doe",
            "created_at": "2026-01-12 10:30:00"
        }
    """
    try:
        data = request.get_json()
        
        if not data or 'username' not in data:
            return jsonify({
                'error': 'Missing required field: username'
            }), 400
        
        username = data['username'].strip()
        
        if not username:
            return jsonify({
                'error': 'Username cannot be empty'
            }), 400
        
        # Create user
        user_id = db.create_user(username)
        
        if user_id is None:
            return jsonify({
                'error': 'Username already exists'
            }), 409
        
        # Get created user
        user = db.get_user(user_id)
        
        return jsonify(user), 201
    
    except Exception as e:
        print(f"Error in /api/user (POST): {e}")
        return jsonify({'error': 'Internal server error'}), 500


@app.route('/api/genres', methods=['GET'])
def get_genres():
    """
    Get list of all movie genres
    
    Response:
        {
            "genres": [
                {"id": 28, "name": "Action"},
                {"id": 35, "name": "Comedy"},
                ...
            ]
        }
    """
    try:
        genres = tmdb.get_genres()
        
        if not genres:
            return jsonify({
                'error': 'Failed to fetch genres'
            }), 500
        
        return jsonify(genres), 200
    
    except Exception as e:
        print(f"Error in /api/genres: {e}")
        return jsonify({'error': 'Internal server error'}), 500


@app.route('/api/trending', methods=['GET'])
def get_trending():
    """
    Get trending movies
    
    Query Parameters:
        time_window: 'day' or 'week' (default: week)
    
    Response:
        {
            "movies": [...],
            "time_window": "week"
        }
    """
    try:
        time_window = request.args.get('time_window', default='week', type=str)
        
        if time_window not in ['day', 'week']:
            time_window = 'week'
        
        result = tmdb.get_trending_movies(time_window)
        
        if not result:
            return jsonify({
                'movies': [],
                'time_window': time_window
            }), 200
        
        movies = [tmdb.format_movie_data(m) for m in result.get('results', [])]
        
        return jsonify({
            'movies': movies,
            'time_window': time_window
        }), 200
    
    except Exception as e:
        print(f"Error in /api/trending: {e}")
        return jsonify({'error': 'Internal server error'}), 500


@app.route('/api/movies/popular', methods=['GET'])
def get_popular_movies():
    """Get popular movies"""
    try:
        page = request.args.get('page', default=1, type=int)
        result = tmdb.get_popular_movies(page)
        
        if not result:
            return jsonify({'movies': []}), 200
        
        movies = [format_movie_for_frontend(m) for m in result.get('results', [])]
        return jsonify({'movies': movies}), 200
    
    except Exception as e:
        print(f"Error in /api/movies/popular: {e}")
        return jsonify({'error': 'Internal server error'}), 500


@app.route('/api/movies/top-rated', methods=['GET'])
def get_top_rated_movies():
    """Get top rated movies"""
    try:
        page = request.args.get('page', default=1, type=int)
        result = tmdb.get_top_rated_movies(page)
        
        if not result:
            return jsonify({'movies': []}), 200
        
        movies = [format_movie_for_frontend(m) for m in result.get('results', [])]
        return jsonify({'movies': movies}), 200
    
    except Exception as e:
        print(f"Error in /api/movies/top-rated: {e}")
        return jsonify({'error': 'Internal server error'}), 500


@app.route('/api/movies/now-playing', methods=['GET'])
def get_now_playing_movies():
    """Get movies currently in theaters"""
    try:
        page = request.args.get('page', default=1, type=int)
        result = tmdb.get_now_playing(page)
        
        if not result:
            return jsonify({'movies': []}), 200
        
        movies = [format_movie_for_frontend(m) for m in result.get('results', [])]
        return jsonify({'movies': movies}), 200
    
    except Exception as e:
        print(f"Error in /api/movies/now-playing: {e}")
        return jsonify({'error': 'Internal server error'}), 500


@app.route('/api/movies/upcoming', methods=['GET'])
def get_upcoming_movies():
    """Get upcoming movies - only movies releasing in the future"""
    try:
        from datetime import datetime
        
        page = request.args.get('page', default=1, type=int)
        result = tmdb.get_upcoming_movies(page)
        
        if not result:
            return jsonify({'movies': []}), 200
        
        # Filter to only include movies with future release dates
        today = datetime.now().strftime('%Y-%m-%d')
        upcoming_movies = []
        
        for movie in result.get('results', []):
            release_date = movie.get('release_date', '')
            # Only include if release date is in the future
            if release_date and release_date > today:
                upcoming_movies.append(format_movie_for_frontend(movie))
        
        return jsonify({'movies': upcoming_movies}), 200
    
    except Exception as e:
        print(f"Error in /api/movies/upcoming: {e}")
        return jsonify({'error': 'Internal server error'}), 500


@app.route('/api/movies/by-year/<int:year>', methods=['GET'])
def get_movies_by_year(year: int):
    """Get popular movies from a specific year"""
    try:
        page = request.args.get('page', default=1, type=int)
        sort_by = request.args.get('sort_by', default='vote_average.desc', type=str)
        
        # Use discover endpoint with year filter
        params = {
            'primary_release_year': year,
            'sort_by': sort_by,
            'page': page,
            'language': 'en-US',
            'vote_count.gte': 100  # Only movies with enough votes
        }
        
        result = tmdb._make_request('/discover/movie', params)
        
        if not result:
            return jsonify({'movies': []}), 200
        
        movies = [format_movie_for_frontend(m) for m in result.get('results', [])]
        return jsonify({'movies': movies}), 200
    
    except Exception as e:
        print(f"Error in /api/movies/by-year/{year}: {e}")
        return jsonify({'error': 'Internal server error'}), 500


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'movie-recommendation-chatbot'
    }), 200


@app.route('/', methods=['GET'])
def index():
    """API information"""
    return jsonify({
        'name': 'Movie Recommendation Chatbot API',
        'version': '1.0.0',
        'endpoints': {
            'POST /api/chat': 'Chat with the bot and get movie recommendations',
            'POST /api/rate': 'Rate a movie',
            'GET /api/recommendations/<user_id>': 'Get personalized recommendations',
            'GET /api/search': 'Search movies with filters',
            'GET /api/movie/<movie_id>': 'Get movie details',
            'GET /api/movie/<movie_id>/providers': 'Get streaming providers',
            'GET /api/user/<user_id>': 'Get user profile',
            'POST /api/user': 'Create a new user',
            'GET /api/genres': 'Get all genres',
            'GET /api/trending': 'Get trending movies',
            'GET /api/health': 'Health check'
        }
    }), 200


# Error handlers
@app.route('/api/personalized-recommendations', methods=['GET'])
def get_personalized_recommendations():
    """Get personalized recommendations based on user's search history and ratings"""
    try:
        user_id = request.args.get('user_id', default=1, type=int)
        page = request.args.get('page', default=1, type=int)
        limit = request.args.get('limit', default=10, type=int)
        
        print(f"Getting personalized recommendations for user {user_id}...")
        
        # Get user's ratings and movie history
        user_ratings = db.get_user_ratings(user_id)
        chat_history = db.get_chat_history(user_id)
        
        if not user_ratings and not chat_history:
            # New user - return trending movies
            print("New user - returning trending movies")
            movies = recommender.get_recommendations_for_new_user(n=limit)
            return jsonify({'movies': [format_movie_for_frontend(m) for m in movies]}), 200
        
        # Get recommendations from the hybrid recommender
        recommendations = recommender.recommend(user_id, n=limit * 2)
        
        # Also analyze genres from user's watched movies
        if user_ratings:
            top_rated_movie = max(user_ratings, key=lambda x: x['rating'])
            top_movie_id = top_rated_movie['movie_id']
            
            # Get similar movies based on top rated
            similar_movies = recommender.content_recommender.recommend(top_movie_id, n=limit)
            
            # Merge recommendations
            rec_dict = {m['movie_id']: m for m in recommendations}
            for movie in similar_movies:
                if movie['movie_id'] not in rec_dict:
                    rec_dict[movie['movie_id']] = movie
            
            recommendations = list(rec_dict.values())[:limit]
        
        print(f"Returning {len(recommendations)} personalized recommendations")
        
        # Format for frontend
        formatted_movies = [format_movie_for_frontend(m) for m in recommendations]
        return jsonify({'movies': formatted_movies}), 200
    
    except Exception as e:
        print(f"Error in /api/personalized-recommendations: {e}")
        return jsonify({'error': 'Internal server error', 'details': str(e)}), 500


@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404


@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500


# ============================================================================
# MAIN
# ============================================================================

if __name__ == '__main__':
    print("=" * 60)
    print("Movie Recommendation Chatbot Backend")
    print("=" * 60)
    print(f"Server starting on http://{Config.HOST}:{Config.PORT}")
    print("=" * 60)
    
    # Run the app
    app.run(
        host=Config.HOST,
        port=Config.PORT,
        debug=Config.DEBUG
    )
