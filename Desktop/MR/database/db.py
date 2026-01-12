import sqlite3
import os
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from config import Config


class Database:
    """Database operations handler"""
    
    def __init__(self, db_path: str = None):
        """Initialize database connection"""
        self.db_path = db_path or Config.DATABASE_PATH
        self.connection = None
        self.initialize_db()
    
    def get_connection(self):
        """Get database connection"""
        if self.connection is None:
            self.connection = sqlite3.connect(self.db_path, check_same_thread=False)
            self.connection.row_factory = sqlite3.Row
        return self.connection
    
    def initialize_db(self):
        """Initialize database with schema"""
        conn = self.get_connection()
        schema_path = os.path.join(os.path.dirname(__file__), 'schema.sql')
        
        with open(schema_path, 'r') as f:
            schema = f.read()
        
        conn.executescript(schema)
        conn.commit()
    
    def close(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()
            self.connection = None
    
    # User operations
    def create_user(self, username: str) -> Optional[int]:
        """Create a new user"""
        conn = self.get_connection()
        try:
            cursor = conn.execute(
                "INSERT INTO users (username) VALUES (?)",
                (username,)
            )
            conn.commit()
            return cursor.lastrowid
        except sqlite3.IntegrityError:
            return None
    
    def get_user(self, user_id: int) -> Optional[Dict]:
        """Get user by ID"""
        conn = self.get_connection()
        cursor = conn.execute(
            "SELECT * FROM users WHERE user_id = ?",
            (user_id,)
        )
        row = cursor.fetchone()
        return dict(row) if row else None
    
    def get_user_by_username(self, username: str) -> Optional[Dict]:
        """Get user by username"""
        conn = self.get_connection()
        cursor = conn.execute(
            "SELECT * FROM users WHERE username = ?",
            (username,)
        )
        row = cursor.fetchone()
        return dict(row) if row else None
    
    # Rating operations
    def add_rating(self, user_id: int, movie_id: int, rating: float) -> bool:
        """Add or update a movie rating"""
        conn = self.get_connection()
        try:
            conn.execute(
                """INSERT INTO ratings (user_id, movie_id, rating) 
                   VALUES (?, ?, ?)
                   ON CONFLICT(user_id, movie_id) 
                   DO UPDATE SET rating = ?, timestamp = CURRENT_TIMESTAMP""",
                (user_id, movie_id, rating, rating)
            )
            conn.commit()
            return True
        except Exception as e:
            print(f"Error adding rating: {e}")
            return False
    
    def get_user_ratings(self, user_id: int) -> List[Dict]:
        """Get all ratings for a user"""
        conn = self.get_connection()
        cursor = conn.execute(
            """SELECT r.*, m.title, m.poster_path 
               FROM ratings r
               LEFT JOIN movies_cache m ON r.movie_id = m.movie_id
               WHERE r.user_id = ?
               ORDER BY r.timestamp DESC""",
            (user_id,)
        )
        return [dict(row) for row in cursor.fetchall()]
    
    def get_all_ratings(self) -> List[Dict]:
        """Get all ratings for collaborative filtering"""
        conn = self.get_connection()
        cursor = conn.execute(
            "SELECT user_id, movie_id, rating FROM ratings"
        )
        return [dict(row) for row in cursor.fetchall()]
    
    def get_user_rating_count(self, user_id: int) -> int:
        """Get total number of ratings by user"""
        conn = self.get_connection()
        cursor = conn.execute(
            "SELECT COUNT(*) as count FROM ratings WHERE user_id = ?",
            (user_id,)
        )
        return cursor.fetchone()['count']
    
    # Movie cache operations
    def cache_movie(self, movie_data: Dict) -> bool:
        """Cache movie data"""
        conn = self.get_connection()
        try:
            conn.execute(
                """INSERT INTO movies_cache 
                   (movie_id, title, genres, poster_path, overview, 
                    vote_average, release_date, popularity, runtime)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                   ON CONFLICT(movie_id) 
                   DO UPDATE SET 
                       title = ?,
                       genres = ?,
                       poster_path = ?,
                       overview = ?,
                       vote_average = ?,
                       release_date = ?,
                       popularity = ?,
                       runtime = ?,
                       cached_at = CURRENT_TIMESTAMP""",
                (
                    movie_data['movie_id'],
                    movie_data['title'],
                    movie_data.get('genres', ''),
                    movie_data.get('poster_path', ''),
                    movie_data.get('overview', ''),
                    movie_data.get('vote_average', 0),
                    movie_data.get('release_date', ''),
                    movie_data.get('popularity', 0),
                    movie_data.get('runtime', 0),
                    # Update values
                    movie_data['title'],
                    movie_data.get('genres', ''),
                    movie_data.get('poster_path', ''),
                    movie_data.get('overview', ''),
                    movie_data.get('vote_average', 0),
                    movie_data.get('release_date', ''),
                    movie_data.get('popularity', 0),
                    movie_data.get('runtime', 0)
                )
            )
            conn.commit()
            return True
        except Exception as e:
            print(f"Error caching movie: {e}")
            return False
    
    def get_cached_movie(self, movie_id: int) -> Optional[Dict]:
        """Get cached movie if not expired"""
        conn = self.get_connection()
        expiry_time = datetime.now() - timedelta(hours=Config.CACHE_EXPIRY_HOURS)
        
        cursor = conn.execute(
            """SELECT * FROM movies_cache 
               WHERE movie_id = ? AND cached_at > ?""",
            (movie_id, expiry_time)
        )
        row = cursor.fetchone()
        return dict(row) if row else None
    
    def get_all_cached_movies(self) -> List[Dict]:
        """Get all cached movies for ML training"""
        conn = self.get_connection()
        cursor = conn.execute(
            "SELECT * FROM movies_cache"
        )
        return [dict(row) for row in cursor.fetchall()]
    
    def clear_expired_cache(self):
        """Remove expired cache entries"""
        conn = self.get_connection()
        expiry_time = datetime.now() - timedelta(hours=Config.CACHE_EXPIRY_HOURS)
        
        conn.execute(
            "DELETE FROM movies_cache WHERE cached_at < ?",
            (expiry_time,)
        )
        conn.commit()
    
    # User preferences operations
    def update_user_preferences(self, user_id: int, 
                               favorite_genres: str = None,
                               favorite_actors: str = None) -> bool:
        """Update user preferences"""
        conn = self.get_connection()
        try:
            conn.execute(
                """INSERT INTO user_preferences (user_id, favorite_genres, favorite_actors)
                   VALUES (?, ?, ?)
                   ON CONFLICT(user_id)
                   DO UPDATE SET
                       favorite_genres = COALESCE(?, favorite_genres),
                       favorite_actors = COALESCE(?, favorite_actors),
                       updated_at = CURRENT_TIMESTAMP""",
                (user_id, favorite_genres, favorite_actors, favorite_genres, favorite_actors)
            )
            conn.commit()
            return True
        except Exception as e:
            print(f"Error updating preferences: {e}")
            return False
    
    def get_user_preferences(self, user_id: int) -> Optional[Dict]:
        """Get user preferences"""
        conn = self.get_connection()
        cursor = conn.execute(
            "SELECT * FROM user_preferences WHERE user_id = ?",
            (user_id,)
        )
        row = cursor.fetchone()
        return dict(row) if row else None
    
    # Chat history operations
    def save_chat(self, user_id: int, message: str, response: str, intent: str = None) -> bool:
        """Save chat interaction"""
        conn = self.get_connection()
        try:
            conn.execute(
                """INSERT INTO chat_history (user_id, message, response, intent)
                   VALUES (?, ?, ?, ?)""",
                (user_id, message, response, intent)
            )
            conn.commit()
            return True
        except Exception as e:
            print(f"Error saving chat: {e}")
            return False
    
    def get_chat_history(self, user_id: int, limit: int = 10) -> List[Dict]:
        """Get recent chat history for a user"""
        conn = self.get_connection()
        cursor = conn.execute(
            """SELECT * FROM chat_history 
               WHERE user_id = ?
               ORDER BY timestamp DESC
               LIMIT ?""",
            (user_id, limit)
        )
        return [dict(row) for row in cursor.fetchall()]
    
    # Analytics
    def get_user_stats(self, user_id: int) -> Dict:
        """Get user statistics"""
        conn = self.get_connection()
        
        # Get rating count
        rating_cursor = conn.execute(
            "SELECT COUNT(*) as count FROM ratings WHERE user_id = ?",
            (user_id,)
        )
        rating_count = rating_cursor.fetchone()['count']
        
        # Get average rating given
        avg_cursor = conn.execute(
            "SELECT AVG(rating) as avg FROM ratings WHERE user_id = ?",
            (user_id,)
        )
        avg_rating = avg_cursor.fetchone()['avg'] or 0
        
        # Get favorite genres from ratings
        genre_cursor = conn.execute(
            """SELECT m.genres, COUNT(*) as count
               FROM ratings r
               JOIN movies_cache m ON r.movie_id = m.movie_id
               WHERE r.user_id = ? AND m.genres IS NOT NULL
               GROUP BY m.genres
               ORDER BY count DESC
               LIMIT 3""",
            (user_id,)
        )
        top_genres = [row['genres'] for row in genre_cursor.fetchall()]
        
        return {
            'total_ratings': rating_count,
            'average_rating': round(avg_rating, 2),
            'top_genres': top_genres
        }


# Singleton instance
_db_instance = None

def get_db() -> Database:
    """Get database singleton instance"""
    global _db_instance
    if _db_instance is None:
        _db_instance = Database()
    return _db_instance
