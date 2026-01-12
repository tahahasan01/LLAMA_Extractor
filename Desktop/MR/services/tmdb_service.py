import requests
import time
from typing import List, Dict, Optional
from config import Config


class TMDbService:
    """TMDb API integration service"""
    
    def __init__(self):
        """Initialize TMDb service"""
        self.api_key = Config.TMDB_API_KEY
        self.base_url = Config.TMDB_BASE_URL
        self.image_base_url = Config.TMDB_IMAGE_BASE_URL
        self.timeout = Config.TMDB_REQUEST_TIMEOUT
        self.last_request_time = 0
        self.min_request_interval = 0.05  # Reduced to 50ms (20 req/sec)
        self._cache = {}  # Simple response cache
        self._cache_ttl = 300  # 5 minutes cache
    
    def _rate_limit(self):
        """Implement rate limiting"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < self.min_request_interval:
            time.sleep(self.min_request_interval - time_since_last)
        
        self.last_request_time = time.time()
    
    def _make_request(self, endpoint: str, params: Dict = None) -> Optional[Dict]:
        """Make API request with error handling and caching"""
        if params is None:
            params = {}
        
        # Create cache key
        cache_key = f"{endpoint}:{sorted(params.items())}"
        
        # Check cache
        if cache_key in self._cache:
            cached_data, cached_time = self._cache[cache_key]
            if time.time() - cached_time < self._cache_ttl:
                return cached_data
        
        self._rate_limit()
        
        params['api_key'] = self.api_key
        url = f"{self.base_url}{endpoint}"
        
        try:
            response = requests.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()
            data = response.json()
            
            # Cache the response
            self._cache[cache_key] = (data, time.time())
            
            return data
        except requests.exceptions.RequestException as e:
            print(f"TMDb API error: {e}")
            return None
    
    def search_movies(self, query: str, page: int = 1) -> Optional[Dict]:
        """
        Search movies by title
        
        Args:
            query: Search query
            page: Page number (default: 1)
        
        Returns:
            Dictionary with search results
        """
        return self._make_request('/search/movie', {
            'query': query,
            'page': page,
            'language': 'en-US'
        })
    
    def get_movie_details(self, movie_id: int) -> Optional[Dict]:
        """
        Get detailed movie information with credits and videos
        
        Args:
            movie_id: TMDb movie ID
        
        Returns:
            Dictionary with movie details including credits and videos
        """
        movie = self._make_request(f'/movie/{movie_id}', {
            'append_to_response': 'credits,videos,keywords',
            'language': 'en-US'
        })
        
        return movie
    
    def get_watch_providers(self, movie_id: int, region: str = "US") -> Optional[Dict]:
        """
        Get streaming availability for a movie
        
        Args:
            movie_id: TMDb movie ID
            region: Country code (default: US)
        
        Returns:
            Dictionary with full provider information including all regions
        """
        data = self._make_request(f'/movie/{movie_id}/watch/providers')
        return data
    
    def discover_movies(self, genre: int = None, year: int = None, 
                       min_rating: float = None, sort_by: str = 'popularity.desc',
                       page: int = 1) -> Optional[Dict]:
        """
        Discover movies with filters
        
        Args:
            genre: Genre ID
            year: Release year
            min_rating: Minimum vote average
            sort_by: Sort method
            page: Page number
        
        Returns:
            Dictionary with discovered movies
        """
        params = {
            'sort_by': sort_by,
            'page': page,
            'language': 'en-US'
        }
        
        if genre:
            params['with_genres'] = genre
        if year:
            params['primary_release_year'] = year
        if min_rating:
            params['vote_average.gte'] = min_rating
            params['vote_count.gte'] = 100  # Ensure enough votes
        
        return self._make_request('/discover/movie', params)
    
    def get_similar_movies(self, movie_id: int, page: int = 1) -> Optional[Dict]:
        """
        Get movies similar to a given movie
        
        Args:
            movie_id: TMDb movie ID
            page: Page number
        
        Returns:
            Dictionary with similar movies
        """
        return self._make_request(f'/movie/{movie_id}/similar', {
            'page': page,
            'language': 'en-US'
        })
    
    def get_trending_movies(self, time_window: str = "week") -> Optional[Dict]:
        """
        Get trending movies
        
        Args:
            time_window: 'day' or 'week'
        
        Returns:
            Dictionary with trending movies
        """
        return self._make_request(f'/trending/movie/{time_window}', {
            'language': 'en-US'
        })
    
    def search_person(self, name: str) -> Optional[Dict]:
        """
        Search for a person (actor, director, etc.)
        
        Args:
            name: Person's name
        
        Returns:
            Dictionary with search results
        """
        return self._make_request('/search/person', {
            'query': name,
            'language': 'en-US'
        })
    
    def get_person_movies(self, person_id: int) -> Optional[Dict]:
        """
        Get movies for a person
        
        Args:
            person_id: TMDb person ID
        
        Returns:
            Dictionary with person's movie credits
        """
        return self._make_request(f'/person/{person_id}/movie_credits', {
            'language': 'en-US'
        })
    
    def search_by_actor(self, actor_name: str, limit: int = 20) -> List[Dict]:
        """
        Find movies featuring a specific actor
        
        Args:
            actor_name: Actor's name
            limit: Maximum number of movies to return
        
        Returns:
            List of movies featuring the actor
        """
        # Search for the person
        person_results = self.search_person(actor_name)
        
        if not person_results or not person_results.get('results'):
            return []
        
        # Get the first matching person
        person = person_results['results'][0]
        person_id = person['id']
        
        # Get their movie credits
        credits = self.get_person_movies(person_id)
        
        if not credits or 'cast' not in credits:
            return []
        
        # Sort by popularity and return top movies
        movies = sorted(
            credits['cast'],
            key=lambda x: x.get('popularity', 0),
            reverse=True
        )[:limit]
        
        return movies
    
    def get_genres(self) -> Optional[Dict]:
        """
        Get list of all movie genres
        
        Returns:
            Dictionary with genre list
        """
        return self._make_request('/genre/movie/list', {
            'language': 'en-US'
        })
    
    def get_genre_id(self, genre_name: str) -> Optional[int]:
        """
        Get genre ID from genre name
        
        Args:
            genre_name: Genre name (case-insensitive)
        
        Returns:
            Genre ID or None
        """
        genres_data = self.get_genres()
        
        if not genres_data or 'genres' not in genres_data:
            return None
        
        genre_name_lower = genre_name.lower()
        for genre in genres_data['genres']:
            if genre['name'].lower() == genre_name_lower:
                return genre['id']
        
        return None
    
    def get_genre_name(self, genre_id: int) -> Optional[str]:
        """
        Get genre name from genre ID
        
        Args:
            genre_id: Genre ID
        
        Returns:
            Genre name or None
        """
        genres_data = self.get_genres()
        
        if not genres_data or 'genres' not in genres_data:
            return None
        
        for genre in genres_data['genres']:
            if genre['id'] == genre_id:
                return genre['name']
        
        return None
    
    def get_popular_movies(self, page: int = 1) -> Optional[Dict]:
        """
        Get popular movies
        
        Args:
            page: Page number
        
        Returns:
            Dictionary with popular movies
        """
        return self._make_request('/movie/popular', {
            'page': page,
            'language': 'en-US'
        })
    
    def get_top_rated_movies(self, page: int = 1) -> Optional[Dict]:
        """
        Get top rated movies
        
        Args:
            page: Page number
        
        Returns:
            Dictionary with top rated movies
        """
        return self._make_request('/movie/top_rated', {
            'page': page,
            'language': 'en-US'
        })
    
    def get_now_playing(self, page: int = 1) -> Optional[Dict]:
        """
        Get movies currently in theaters
        
        Args:
            page: Page number
        
        Returns:
            Dictionary with now playing movies
        """
        return self._make_request('/movie/now_playing', {
            'page': page,
            'language': 'en-US',
            'region': 'US'
        })
    
    def get_upcoming_movies(self, page: int = 1) -> Optional[Dict]:
        """
        Get upcoming movies
        
        Args:
            page: Page number
        
        Returns:
            Dictionary with upcoming movies
        """
        return self._make_request('/movie/upcoming', {
            'page': page,
            'language': 'en-US',
            'region': 'US'
        })
    
    def format_movie_data(self, movie: Dict) -> Dict:
        """
        Format movie data for consistent structure
        
        Args:
            movie: Raw movie data from TMDb
        
        Returns:
            Formatted movie dictionary
        """
        return {
            'movie_id': movie.get('id'),
            'title': movie.get('title'),
            'overview': movie.get('overview'),
            'poster_path': movie.get('poster_path'),
            'backdrop_path': movie.get('backdrop_path'),
            'release_date': movie.get('release_date'),
            'vote_average': movie.get('vote_average'),
            'vote_count': movie.get('vote_count'),
            'popularity': movie.get('popularity'),
            'genre_ids': movie.get('genre_ids', []),
            'genres': ','.join(g['name'] for g in movie.get('genres', [])) if 'genres' in movie else '',
            'runtime': movie.get('runtime'),
            'poster_url': f"{self.image_base_url}{movie.get('poster_path')}" if movie.get('poster_path') else None
        }
    
    def get_recommendations(self, movie_id: int, page: int = 1) -> Optional[Dict]:
        """
        Get TMDb's recommended movies based on a movie
        
        Args:
            movie_id: TMDb movie ID
            page: Page number
        
        Returns:
            Dictionary with recommended movies
        """
        return self._make_request(f'/movie/{movie_id}/recommendations', {
            'page': page,
            'language': 'en-US'
        })


# Singleton instance
_tmdb_service = None

def get_tmdb_service() -> TMDbService:
    """Get TMDb service singleton instance"""
    global _tmdb_service
    if _tmdb_service is None:
        _tmdb_service = TMDbService()
    return _tmdb_service
