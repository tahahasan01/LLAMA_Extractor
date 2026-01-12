from typing import Dict, Optional
from datetime import datetime


class User:
    """User model"""
    
    def __init__(self, user_id: int = None, username: str = None, 
                 created_at: str = None):
        """
        Initialize User
        
        Args:
            user_id: User ID
            username: Username
            created_at: Creation timestamp
        """
        self.user_id = user_id
        self.username = username
        self.created_at = created_at or datetime.now().isoformat()
    
    def to_dict(self) -> Dict:
        """Convert user to dictionary"""
        return {
            'user_id': self.user_id,
            'username': self.username,
            'created_at': self.created_at
        }
    
    @staticmethod
    def from_dict(data: Dict) -> 'User':
        """Create User from dictionary"""
        return User(
            user_id=data.get('user_id'),
            username=data.get('username'),
            created_at=data.get('created_at')
        )
    
    def __repr__(self):
        return f"User(id={self.user_id}, username='{self.username}')"


class UserPreferences:
    """User preferences model"""
    
    def __init__(self, user_id: int, favorite_genres: str = None,
                 favorite_actors: str = None, updated_at: str = None):
        """
        Initialize UserPreferences
        
        Args:
            user_id: User ID
            favorite_genres: Comma-separated genre names
            favorite_actors: Comma-separated actor names
            updated_at: Last update timestamp
        """
        self.user_id = user_id
        self.favorite_genres = favorite_genres or ""
        self.favorite_actors = favorite_actors or ""
        self.updated_at = updated_at or datetime.now().isoformat()
    
    def get_genres_list(self) -> list:
        """Get favorite genres as list"""
        if not self.favorite_genres:
            return []
        return [g.strip() for g in self.favorite_genres.split(',') if g.strip()]
    
    def get_actors_list(self) -> list:
        """Get favorite actors as list"""
        if not self.favorite_actors:
            return []
        return [a.strip() for a in self.favorite_actors.split(',') if a.strip()]
    
    def add_genre(self, genre: str):
        """Add a favorite genre"""
        genres = self.get_genres_list()
        if genre not in genres:
            genres.append(genre)
            self.favorite_genres = ','.join(genres)
    
    def add_actor(self, actor: str):
        """Add a favorite actor"""
        actors = self.get_actors_list()
        if actor not in actors:
            actors.append(actor)
            self.favorite_actors = ','.join(actors)
    
    def to_dict(self) -> Dict:
        """Convert preferences to dictionary"""
        return {
            'user_id': self.user_id,
            'favorite_genres': self.get_genres_list(),
            'favorite_actors': self.get_actors_list(),
            'updated_at': self.updated_at
        }
    
    @staticmethod
    def from_dict(data: Dict) -> 'UserPreferences':
        """Create UserPreferences from dictionary"""
        return UserPreferences(
            user_id=data.get('user_id'),
            favorite_genres=data.get('favorite_genres', ''),
            favorite_actors=data.get('favorite_actors', ''),
            updated_at=data.get('updated_at')
        )
    
    def __repr__(self):
        return f"UserPreferences(user_id={self.user_id}, genres={len(self.get_genres_list())}, actors={len(self.get_actors_list())})"
