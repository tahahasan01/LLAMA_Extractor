import re
from typing import Dict, List, Optional


class IntentParser:
    """Parse user messages to extract intent and entities"""
    
    # Intent patterns
    GENRE_KEYWORDS = {
        'action', 'comedy', 'drama', 'horror', 'thriller', 'romance', 'sci-fi',
        'science fiction', 'fantasy', 'animation', 'documentary', 'crime',
        'mystery', 'adventure', 'family', 'musical', 'war', 'western', 'biography'
    }
    
    MOOD_KEYWORDS = {
        'scary': 'horror',
        'funny': 'comedy',
        'romantic': 'romance',
        'exciting': 'action',
        'sad': 'drama',
        'feel-good': 'comedy',
        'uplifting': 'drama',
        'suspenseful': 'thriller',
        'creepy': 'horror',
        'heartwarming': 'family'
    }
    
    TIME_KEYWORDS = {
        'recent': 2020,
        'new': 2022,
        'latest': 2023,
        'old': 1990,
        'classic': 1980,
        '90s': 1995,
        '80s': 1985,
        '70s': 1975,
        '2000s': 2005,
        '2010s': 2015
    }
    
    TRENDING_KEYWORDS = {
        'trending', 'popular', 'hot', 'viral', 'everyone watching',
        'what\'s popular', 'most watched', 'top movies', 'best movies',
        'top rated', 'highest rated', 'best rated', 'top 10', 'top 5',
        'top 2', 'best of all time', 'greatest', 'must watch'
    }
    
    QUESTION_KEYWORDS = {
        'what is', 'what are', 'tell me', 'show me', 'can you',
        'rating of', 'rating for', 'how good', 'is it good'
    }
    
    SIMILAR_KEYWORDS = {
        'like', 'similar to', 'similar', 'same as', 'resembles',
        'reminds me of', 'comparable to', 'in the style of'
    }
    
    ACTOR_KEYWORDS = {
        'with', 'starring', 'featuring', 'actor', 'actress', 'cast'
    }
    
    def __init__(self):
        """Initialize intent parser"""
        pass
    
    def parse(self, message: str) -> Dict:
        """
        Parse user message to extract intent and entities
        
        Args:
            message: User's message
        
        Returns:
            Dictionary with intent and entities
        """
        message_lower = message.lower().strip()
        
        intent_data = {
            'intent': 'general',
            'entities': {},
            'original_message': message
        }
        
        # Check for trending/popular intent
        # But first check if there's a genre specified - genre takes priority
        genre = self._extract_genre(message_lower)
        mood_genre = self._extract_mood(message_lower)  # Also check mood keywords
        year = self._extract_year(message_lower)
        
        if self._check_trending(message_lower):
            # If genre is specified with trending keywords, treat as genre search
            # Check both direct genre and mood-based genre
            if genre or mood_genre:
                intent_data['intent'] = 'genre_search'
                intent_data['entities']['genre'] = genre if genre else mood_genre
                if year:
                    intent_data['entities']['year'] = year
                return intent_data
            
            # Otherwise it's a trending request
            intent_data['intent'] = 'trending'
            if year:
                intent_data['entities']['year'] = year
            return intent_data
        
        # Check for question about specific movie (rating, info, etc)
        if self._is_movie_question(message_lower):
            # Extract movie title from question
            movie_title = self._extract_movie_from_question(message_lower)
            if movie_title:
                intent_data['intent'] = 'title_search'
                intent_data['entities']['query'] = movie_title
                return intent_data
        
        # Check for similar movie intent
        similar_movie = self._extract_similar_movie(message_lower)
        if similar_movie:
            intent_data['intent'] = 'similar_movie'
            intent_data['entities']['reference_movie'] = similar_movie
            return intent_data
        
        # Check for actor search intent
        actor = self._extract_actor(message_lower)
        if actor:
            intent_data['intent'] = 'actor_search'
            intent_data['entities']['actor'] = actor
            
            # May also have genre filter
            genre = self._extract_genre(message_lower)
            if genre:
                intent_data['entities']['genre'] = genre
            
            return intent_data
        
        # Check for genre search intent
        genre = self._extract_genre(message_lower)
        if genre:
            intent_data['intent'] = 'genre_search'
            intent_data['entities']['genre'] = genre
            
            # May also have year/decade
            year = self._extract_year(message_lower)
            if year:
                intent_data['entities']['year'] = year
            
            return intent_data
        
        # Check for mood-based search
        mood_genre = self._extract_mood(message_lower)
        if mood_genre:
            intent_data['intent'] = 'mood_search'
            intent_data['entities']['genre'] = mood_genre
            return intent_data
        
        # Check for year/decade search
        year = self._extract_year(message_lower)
        if year:
            intent_data['intent'] = 'year_search'
            intent_data['entities']['year'] = year
            return intent_data
        
        # Check for specific title search (with or without keywords)
        if self._is_title_search(message_lower):
            intent_data['intent'] = 'title_search'
            intent_data['entities']['query'] = message
            return intent_data
        
        # Default: treat short messages without genre/actor/etc as title search
        # This handles cases like "top gun" or "F1"
        words = message_lower.split()
        if len(words) <= 3 and not genre and not mood_genre and not year:
            # Short message without known keywords - likely a movie title
            intent_data['intent'] = 'title_search'
            intent_data['entities']['query'] = message
            return intent_data
    
    def _check_trending(self, message: str) -> bool:
        """Check if message is asking for trending movies"""
        return any(keyword in message for keyword in self.TRENDING_KEYWORDS)
    
    def _is_movie_question(self, message: str) -> bool:
        """Check if message is asking a question about a movie"""
        return any(keyword in message for keyword in self.QUESTION_KEYWORDS)
    
    def _extract_movie_from_question(self, message: str) -> Optional[str]:
        """Extract movie title from a question"""
        # Patterns like "what is the rating of inception"
        patterns = [
            r'rating (?:of|for) (.+)',
            r'tell me about (.+)',
            r'what is (.+)',
            r'show me (.+)',
            r'how good is (.+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, message)
            if match:
                title = match.group(1).strip()
                # Remove common trailing words
                title = re.sub(r'\s+(movie|film)$', '', title)
                return title
        
        return None
    
    def _extract_genre(self, message: str) -> Optional[str]:
        intent_data['entities']['query'] = message
        
        return intent_data
    
    def _check_trending(self, message: str) -> bool:
        """Check if message is asking for trending movies"""
        return any(keyword in message for keyword in self.TRENDING_KEYWORDS)
    
    def _extract_genre(self, message: str) -> Optional[str]:
        """Extract genre from message"""
        for genre in self.GENRE_KEYWORDS:
            if genre in message:
                # Normalize genre name
                if genre == 'sci-fi' or genre == 'science fiction':
                    return 'Science Fiction'
                return genre.title()
        return None
    
    def _extract_mood(self, message: str) -> Optional[str]:
        """Extract mood and map to genre"""
        for mood, genre in self.MOOD_KEYWORDS.items():
            if mood in message:
                return genre.title()
        return None
    
    def _extract_year(self, message: str) -> Optional[int]:
        """Extract year or decade from message"""
        # Check for time keywords
        for keyword, year in self.TIME_KEYWORDS.items():
            if keyword in message:
                return year
        
        # Check for specific year (1900-2099)
        year_match = re.search(r'\b(19\d{2}|20\d{2})\b', message)
        if year_match:
            return int(year_match.group(1))
        
        return None
    
    def _extract_similar_movie(self, message: str) -> Optional[str]:
        """Extract reference movie for similarity search"""
        for keyword in self.SIMILAR_KEYWORDS:
            if keyword in message:
                # Extract the movie title after the keyword
                pattern = rf'{keyword}\s+(["\']?)([^"\']+)\1'
                match = re.search(pattern, message)
                if match:
                    return match.group(2).strip()
                
                # Try to extract quoted title
                quote_match = re.search(r'["\']([^"\']+)["\']', message)
                if quote_match:
                    return quote_match.group(1).strip()
                
                # Extract capitalized words after keyword
                parts = message.split(keyword, 1)
                if len(parts) > 1:
                    remaining = parts[1].strip()
                    # Get capitalized words or first few words
                    words = remaining.split()[:5]
                    title = ' '.join(words).strip('.,!?')
                    if title:
                        return title
        
        return None
    
    def _extract_actor(self, message: str) -> Optional[str]:
        """Extract actor name from message"""
        for keyword in self.ACTOR_KEYWORDS:
            if keyword in message:
                # Extract name after keyword
                pattern = rf'{keyword}\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)'
                match = re.search(pattern, message, re.IGNORECASE)
                if match:
                    return match.group(1).strip()
        
        # Look for capitalized names (likely actors)
        name_pattern = r'\b([A-Z][a-z]+\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\b'
        matches = re.findall(name_pattern, message)
        if matches:
            return matches[0]
        
        return None
    
    def _is_title_search(self, message: str) -> bool:
        """Check if message is searching for a specific title"""
        # If message is short and doesn't match other patterns, likely a title
        search_indicators = ['find', 'search', 'look for', 'show me', 'get']
        return any(indicator in message for indicator in search_indicators)
    
    def extract_filters(self, message: str) -> Dict:
        """
        Extract additional filters from message
        
        Args:
            message: User's message
        
        Returns:
            Dictionary with filter parameters
        """
        message_lower = message.lower()
        filters = {}
        
        # Extract minimum rating
        rating_match = re.search(r'rated?\s+(?:above|over|at least)\s+(\d+(?:\.\d+)?)', message_lower)
        if rating_match:
            filters['min_rating'] = float(rating_match.group(1))
        
        # Extract rating threshold
        high_rated = ['highly rated', 'top rated', 'best rated', 'good ratings']
        if any(phrase in message_lower for phrase in high_rated):
            filters['min_rating'] = 7.0
        
        # Extract language preference
        if 'foreign' in message_lower or 'international' in message_lower:
            filters['language'] = 'foreign'
        
        return filters


def parse_user_message(message: str) -> Dict:
    """
    Convenience function to parse user message
    
    Args:
        message: User's message
    
    Returns:
        Dictionary with intent and entities
    """
    parser = IntentParser()
    return parser.parse(message)
