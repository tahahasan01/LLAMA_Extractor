from typing import Dict, List, Optional
from datetime import datetime


class Movie:
    """Movie model"""
    
    def __init__(self, movie_id: int, title: str, overview: str = "",
                 poster_path: str = None, backdrop_path: str = None,
                 release_date: str = "", vote_average: float = 0.0,
                 vote_count: int = 0, popularity: float = 0.0,
                 genres: str = "", runtime: int = 0, cached_at: str = None):
        """
        Initialize Movie
        
        Args:
            movie_id: TMDb movie ID
            title: Movie title
            overview: Movie description
            poster_path: Poster image path
            backdrop_path: Backdrop image path
            release_date: Release date (YYYY-MM-DD)
            vote_average: Average rating
            vote_count: Number of votes
            popularity: Popularity score
            genres: Comma-separated genre names
            runtime: Runtime in minutes
            cached_at: Cache timestamp
        """
        self.movie_id = movie_id
        self.title = title
        self.overview = overview
        self.poster_path = poster_path
        self.backdrop_path = backdrop_path
        self.release_date = release_date
        self.vote_average = vote_average
        self.vote_count = vote_count
        self.popularity = popularity
        self.genres = genres
        self.runtime = runtime
        self.cached_at = cached_at or datetime.now().isoformat()
    
    def get_genres_list(self) -> List[str]:
        """Get genres as list"""
        if not self.genres:
            return []
        return [g.strip() for g in self.genres.split(',') if g.strip()]
    
    def get_year(self) -> Optional[int]:
        """Extract year from release date"""
        if not self.release_date or len(self.release_date) < 4:
            return None
        try:
            return int(self.release_date[:4])
        except ValueError:
            return None
    
    def get_poster_url(self, base_url: str = "https://image.tmdb.org/t/p/w500") -> Optional[str]:
        """Get full poster URL"""
        if not self.poster_path:
            return None
        return f"{base_url}{self.poster_path}"
    
    def get_backdrop_url(self, base_url: str = "https://image.tmdb.org/t/p/original") -> Optional[str]:
        """Get full backdrop URL"""
        if not self.backdrop_path:
            return None
        return f"{base_url}{self.backdrop_path}"
    
    def to_dict(self) -> Dict:
        """Convert movie to dictionary"""
        return {
            'movie_id': self.movie_id,
            'title': self.title,
            'overview': self.overview,
            'poster_path': self.poster_path,
            'poster_url': self.get_poster_url(),
            'backdrop_path': self.backdrop_path,
            'backdrop_url': self.get_backdrop_url(),
            'release_date': self.release_date,
            'year': self.get_year(),
            'vote_average': round(self.vote_average, 1),
            'vote_count': self.vote_count,
            'popularity': round(self.popularity, 1),
            'genres': self.get_genres_list(),
            'runtime': self.runtime,
            'cached_at': self.cached_at
        }
    
    @staticmethod
    def from_dict(data: Dict) -> 'Movie':
        """Create Movie from dictionary"""
        return Movie(
            movie_id=data.get('movie_id'),
            title=data.get('title', ''),
            overview=data.get('overview', ''),
            poster_path=data.get('poster_path'),
            backdrop_path=data.get('backdrop_path'),
            release_date=data.get('release_date', ''),
            vote_average=data.get('vote_average', 0.0),
            vote_count=data.get('vote_count', 0),
            popularity=data.get('popularity', 0.0),
            genres=data.get('genres', ''),
            runtime=data.get('runtime', 0),
            cached_at=data.get('cached_at')
        )
    
    def __repr__(self):
        return f"Movie(id={self.movie_id}, title='{self.title}', year={self.get_year()})"


class Rating:
    """Movie rating model"""
    
    def __init__(self, rating_id: int = None, user_id: int = None,
                 movie_id: int = None, rating: float = 0.0,
                 timestamp: str = None):
        """
        Initialize Rating
        
        Args:
            rating_id: Rating ID
            user_id: User ID
            movie_id: Movie ID
            rating: Rating value (1-5)
            timestamp: Rating timestamp
        """
        self.rating_id = rating_id
        self.user_id = user_id
        self.movie_id = movie_id
        self.rating = rating
        self.timestamp = timestamp or datetime.now().isoformat()
    
    def to_dict(self) -> Dict:
        """Convert rating to dictionary"""
        return {
            'rating_id': self.rating_id,
            'user_id': self.user_id,
            'movie_id': self.movie_id,
            'rating': self.rating,
            'timestamp': self.timestamp
        }
    
    @staticmethod
    def from_dict(data: Dict) -> 'Rating':
        """Create Rating from dictionary"""
        return Rating(
            rating_id=data.get('rating_id'),
            user_id=data.get('user_id'),
            movie_id=data.get('movie_id'),
            rating=data.get('rating', 0.0),
            timestamp=data.get('timestamp')
        )
    
    def __repr__(self):
        return f"Rating(user_id={self.user_id}, movie_id={self.movie_id}, rating={self.rating})"
