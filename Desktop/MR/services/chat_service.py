from typing import Dict, List
from services.tmdb_service import get_tmdb_service
from utils.intent_parser import IntentParser
from database import get_db
from config import Config
import random


class ChatService:
    """Handle chat interactions and generate responses"""
    
    def __init__(self):
        """Initialize chat service"""
        self.tmdb = get_tmdb_service()
        self.parser = IntentParser()
        self.db = get_db()
        self._genre_cache = None  # Cache for genre ID to name mapping
    
    def process_message(self, user_id: int, message: str) -> Dict:
        """
        Process user message and generate response
        
        Args:
            user_id: User ID
            message: User's message
        
        Returns:
            Dictionary with response and movies
        """
        # Parse intent
        intent_data = self.parser.parse(message)
        intent = intent_data['intent']
        entities = intent_data['entities']
        
        # Extract limit from message (e.g., "top 2 movies", "show me 5 films")
        limit = self._extract_limit(message)
        
        # Get movies based on intent
        movies = []
        response_text = ""
        
        try:
            if intent == 'trending':
                movies = self._handle_trending(entities)
                year = entities.get('year')
                if limit and year:
                    response_text = f"Here are the top {limit} movies from {year}! 🎬"
                elif year:
                    response_text = f"Here are the best movies from {year}! 🎬"
                elif limit:
                    response_text = f"Here are the top {limit} trending movies right now! 🎬"
                else:
                    response_text = "Here are the trending movies right now! 🎬"
            
            elif intent == 'similar_movie':
                movies = self._handle_similar_movie(entities)
                reference = entities.get('reference_movie', 'that movie')
                if movies:
                    response_text = f"Great choice! Here are movies similar to {reference}:"
                else:
                    response_text = f"I couldn't find '{reference}'. Could you try rephrasing or check the spelling?"
            
            elif intent == 'actor_search':
                movies = self._handle_actor_search(entities)
                actor = entities.get('actor', 'that actor')
                if movies:
                    response_text = f"Here are popular movies featuring {actor}:"
                else:
                    response_text = f"I couldn't find movies with {actor}. Could you check the spelling?"
            
            elif intent == 'genre_search' or intent == 'mood_search':
                movies = self._handle_genre_search(entities)
                genre = entities.get('genre', 'that genre')
                year = entities.get('year')
                
                if limit and year:
                    response_text = f"Here are the top {limit} {genre} movies from {year}! 🍿"
                elif year:
                    response_text = f"Here are some great {genre} movies from {year}! 🍿"
                elif limit:
                    response_text = f"Here are the top {limit} {genre} movies! 🍿"
                else:
                    response_text = f"Here are some great {genre} movies for you! 🍿"
            
            elif intent == 'year_search':
                movies = self._handle_year_search(entities)
                year = entities.get('year')
                response_text = f"Here are some popular movies from around {year}:"
            
            elif intent == 'title_search':
                movies = self._handle_title_search(entities)
                if movies:
                    response_text = "Here's what I found:"
                else:
                    response_text = "I couldn't find that movie. Try searching with a different title."
            
            else:
                # General recommendation
                movies = self._handle_general(user_id, entities)
                response_text = "Based on your preferences, you might enjoy these movies:"
            
            # Format movie results
            max_results = limit if limit else 10
            formatted_movies = [self._format_movie(m) for m in movies[:max_results]]
            
            # Cache movies
            for movie in formatted_movies:
                self._cache_movie(movie)
            
            # Save chat history
            self.db.save_chat(user_id, message, response_text, intent)
            
            return {
                'reply': response_text,
                'movies': formatted_movies,
                'intent': intent,
                'entities': entities
            }
        
        except Exception as e:
            print(f"Error processing message: {e}")
            return {
                'reply': "Sorry, I encountered an error. Please try again!",
                'movies': [],
                'intent': 'error',
                'entities': {}
            }
    
    def _extract_limit(self, message: str) -> int:
        """Extract number limit from message (e.g., 'top 2', 'show me 5')"""
        import re
        # Look for patterns like "top 2", "best 5", "show me 3"
        patterns = [
            r'top (\d+)',
            r'best (\d+)',
            r'show (?:me )?(\d+)',
            r'give (?:me )?(\d+)',
            r'(\d+) (?:movies|films)'
        ]
        
        message_lower = message.lower()
        for pattern in patterns:
            match = re.search(pattern, message_lower)
            if match:
                return int(match.group(1))
        
        return None
    
    def _handle_trending(self, entities: Dict) -> List[Dict]:
        """Handle trending movies request"""
        year = entities.get('year')
        
        # If a specific year is requested, use discover instead of trending
        if year:
            result = self.tmdb.discover_movies(
                year=year,
                sort_by='vote_average.desc',  # Sort by rating for "best" movies
                min_rating=7.0  # Only highly rated movies
            )
            return result.get('results', []) if result else []
        
        # Otherwise return current trending movies
        result = self.tmdb.get_trending_movies('week')
        return result.get('results', []) if result else []
    
    def _handle_similar_movie(self, entities: Dict) -> List[Dict]:
        """Handle similar movie request"""
        reference_movie = entities.get('reference_movie')
        
        if not reference_movie:
            return []
        
        # Search for the reference movie
        search_result = self.tmdb.search_movies(reference_movie)
        
        if not search_result or not search_result.get('results'):
            return []
        
        # Get the first matching movie
        movie = search_result['results'][0]
        movie_id = movie['id']
        
        # Get similar movies
        similar_result = self.tmdb.get_similar_movies(movie_id)
        
        return similar_result.get('results', []) if similar_result else []
    
    def _handle_actor_search(self, entities: Dict) -> List[Dict]:
        """Handle actor search request"""
        actor = entities.get('actor')
        
        if not actor:
            return []
        
        movies = self.tmdb.search_by_actor(actor, limit=20)
        
        # Apply genre filter if specified
        genre = entities.get('genre')
        if genre and movies:
            genre_id = self.tmdb.get_genre_id(genre)
            if genre_id:
                movies = [
                    m for m in movies 
                    if genre_id in m.get('genre_ids', [])
                ]
        
        return movies
    
    def _handle_genre_search(self, entities: Dict) -> List[Dict]:
        """Handle genre search request"""
        genre_name = entities.get('genre')
        year = entities.get('year')
        
        if not genre_name:
            return []
        
        # Get genre ID
        genre_id = self.tmdb.get_genre_id(genre_name)
        
        if not genre_id:
            return []
        
        # Discover movies with filters
        result = self.tmdb.discover_movies(
            genre=genre_id,
            year=year,
            sort_by='vote_average.desc',
            min_rating=6.0  # Only well-rated movies
        )
        
        return result.get('results', []) if result else []
    
    def _handle_year_search(self, entities: Dict) -> List[Dict]:
        """Handle year/decade search request"""
        year = entities.get('year')
        
        if not year:
            return []
        
        # Discover movies from that year
        result = self.tmdb.discover_movies(
            year=year,
            sort_by='vote_average.desc',
            min_rating=6.0
        )
        
        return result.get('results', []) if result else []
    
    def _handle_title_search(self, entities: Dict) -> List[Dict]:
        """Handle specific title search"""
        query = entities.get('query')
        
        if not query:
            return []
        
        result = self.tmdb.search_movies(query)
        
        return result.get('results', []) if result else []
    
    def _handle_general(self, user_id: int, entities: Dict) -> List[Dict]:
        """Handle general recommendation request"""
        # Get user's rating history
        ratings = self.db.get_user_ratings(user_id)
        
        if len(ratings) >= 5:
            # User has enough ratings, use collaborative filtering
            # For now, return popular movies (will be enhanced with ML)
            result = self.tmdb.get_popular_movies()
            return result.get('results', []) if result else []
        else:
            # New user, return trending/popular movies
            result = self.tmdb.get_trending_movies('week')
            return result.get('results', []) if result else []
    
    def _get_genre_map(self) -> Dict:
        """Get cached genre ID to name mapping"""
        if self._genre_cache is None:
            genres_data = self.tmdb.get_genres()
            if genres_data and 'genres' in genres_data:
                self._genre_cache = {g['id']: g['name'] for g in genres_data['genres']}
            else:
                self._genre_cache = {}
        return self._genre_cache
    
    def _format_movie(self, movie: Dict) -> Dict:
        """Format movie data for response to match frontend Movie interface"""
        movie_id = movie.get('id')
        
        # Skip streaming providers in list view for performance
        # They will be loaded when user clicks on a specific movie
        platforms = []
        
        # Get genre names efficiently using cache
        genre_ids = movie.get('genre_ids', [])
        genres = []
        if genre_ids:
            genre_map = self._get_genre_map()
            genres = [genre_map.get(gid) for gid in genre_ids if gid in genre_map]
        
        return {
            'id': movie_id,
            'title': movie.get('title'),
            'poster': f"https://image.tmdb.org/t/p/w500{movie.get('poster_path')}" if movie.get('poster_path') else 'https://via.placeholder.com/500x750/1a1a2e/eee?text=No+Poster',
            'backdrop': f"https://image.tmdb.org/t/p/original{movie.get('backdrop_path')}" if movie.get('backdrop_path') else None,
            'rating': round(movie.get('vote_average', 0), 1),  # 0-10 scale
            'genres': genres,
            'year': int(movie.get('release_date', '')[:4]) if movie.get('release_date') else None,
            'platforms': platforms,
            'overview': movie.get('overview'),
            'runtime': movie.get('runtime'),
            'director': None,  # Will be added if details requested
            'cast': [],  # Will be added if details requested
            'trailer': None  # Will be added if details requested
        }
    
    def _get_platform_color(self, platform_name: str) -> str:
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
    
    def _cache_movie(self, movie: Dict):
        """Cache movie in database"""
        try:
            # Only cache if we have an ID
            if not movie.get('id'):
                return
                
            movie_data = {
                'movie_id': movie['id'],
                'title': movie['title'],
                'overview': movie.get('overview', ''),
                'poster_path': movie.get('poster', '').split('/')[-1] if movie.get('poster') else '',
                'vote_average': movie.get('rating', 0),
                'release_date': str(movie.get('year', '')) if movie.get('year') else '',
                'popularity': 0,  # Not tracking popularity separately
                'genres': ','.join(movie.get('genres', []))
            }
            self.db.cache_movie(movie_data)
        except Exception as e:
            print(f"Error caching movie: {e}")
    
    def generate_response_variants(self, intent: str) -> str:
        """
        Generate varied responses for better UX
        
        Args:
            intent: Intent type
        
        Returns:
            Response text
        """
        responses = {
            'trending': [
                "Here are the hottest movies right now! 🔥",
                "Check out what everyone's watching! 🎬",
                "These are trending this week! 🍿"
            ],
            'genre_search': [
                "I found some great movies in that genre! 🎥",
                "Here are some top picks for you! ⭐",
                "You'll love these! 🍿"
            ],
            'similar_movie': [
                "If you liked that, you'll enjoy these! 🎬",
                "Here are some similar recommendations! 🎯",
                "Movies in the same vein! 🎥"
            ],
            'actor_search': [
                "Here are their best performances! 🌟",
                "Great movies featuring that actor! 🎭",
                "You'll enjoy these! 🎬"
            ]
        }
        
        return random.choice(responses.get(intent, ["Here are some recommendations for you! 🎬"]))


def get_chat_service() -> ChatService:
    """Get chat service singleton instance"""
    return ChatService()
