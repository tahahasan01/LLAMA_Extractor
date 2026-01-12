import pyodbc
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from config import Config


class SQLServerDatabase:
    """SQL Server database operations handler"""
    
    def __init__(self, connection_string: str = None):
        """Initialize SQL Server database connection"""
        self.connection_string = connection_string or Config.SQL_SERVER_CONNECTION_STRING
        self.connection = None
        self.initialize_db()
    
    def get_connection(self):
        """Get database connection"""
        if self.connection is None or not self._is_connection_alive():
            self.connection = pyodbc.connect(self.connection_string)
        return self.connection
    
    def _is_connection_alive(self):
        """Check if connection is still alive"""
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT 1")
            cursor.close()
            return True
        except:
            return False
    
    def initialize_db(self):
        """Initialize database with schema"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Create tables
        cursor.execute("""
            IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'users')
            CREATE TABLE users (
                user_id INT IDENTITY(1,1) PRIMARY KEY,
                username NVARCHAR(255) UNIQUE NOT NULL,
                created_at DATETIME DEFAULT GETDATE()
            )
        """)
        
        cursor.execute("""
            IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'ratings')
            CREATE TABLE ratings (
                rating_id INT IDENTITY(1,1) PRIMARY KEY,
                user_id INT NOT NULL,
                movie_id INT NOT NULL,
                rating FLOAT NOT NULL CHECK(rating >= 1 AND rating <= 5),
                timestamp DATETIME DEFAULT GETDATE(),
                FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
                UNIQUE(user_id, movie_id)
            )
        """)
        
        cursor.execute("""
            IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'movies_cache')
            CREATE TABLE movies_cache (
                movie_id INT PRIMARY KEY,
                title NVARCHAR(500) NOT NULL,
                genres NVARCHAR(500),
                poster_path NVARCHAR(500),
                overview NVARCHAR(MAX),
                vote_average FLOAT,
                release_date NVARCHAR(50),
                popularity FLOAT,
                runtime INT,
                cached_at DATETIME DEFAULT GETDATE()
            )
        """)
        
        cursor.execute("""
            IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'user_preferences')
            CREATE TABLE user_preferences (
                user_id INT PRIMARY KEY,
                favorite_genres NVARCHAR(MAX),
                favorite_actors NVARCHAR(MAX),
                updated_at DATETIME DEFAULT GETDATE(),
                FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
            )
        """)
        
        cursor.execute("""
            IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'chat_history')
            CREATE TABLE chat_history (
                chat_id INT IDENTITY(1,1) PRIMARY KEY,
                user_id INT NOT NULL,
                message NVARCHAR(MAX) NOT NULL,
                response NVARCHAR(MAX) NOT NULL,
                intent NVARCHAR(100),
                timestamp DATETIME DEFAULT GETDATE(),
                FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
            )
        """)
        
        # Create indexes
        cursor.execute("""
            IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'idx_ratings_user')
            CREATE INDEX idx_ratings_user ON ratings(user_id)
        """)
        
        cursor.execute("""
            IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'idx_ratings_movie')
            CREATE INDEX idx_ratings_movie ON ratings(movie_id)
        """)
        
        cursor.execute("""
            IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'idx_cache_cached_at')
            CREATE INDEX idx_cache_cached_at ON movies_cache(cached_at)
        """)
        
        conn.commit()
        cursor.close()
    
    def close(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()
            self.connection = None
    
    # User operations
    def create_user(self, username: str) -> Optional[int]:
        """Create a new user"""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO users (username) VALUES (?)",
                (username,)
            )
            conn.commit()
            cursor.execute("SELECT @@IDENTITY")
            user_id = cursor.fetchone()[0]
            cursor.close()
            return int(user_id)
        except pyodbc.IntegrityError:
            cursor.close()
            return None
        except Exception as e:
            print(f"Error creating user: {e}")
            cursor.close()
            return None
    
    def get_user(self, user_id: int) -> Optional[Dict]:
        """Get user by ID"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT user_id, username, created_at FROM users WHERE user_id = ?",
            (user_id,)
        )
        row = cursor.fetchone()
        cursor.close()
        
        if row:
            return {
                'user_id': row[0],
                'username': row[1],
                'created_at': str(row[2])
            }
        return None
    
    def get_user_by_username(self, username: str) -> Optional[Dict]:
        """Get user by username"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT user_id, username, created_at FROM users WHERE username = ?",
            (username,)
        )
        row = cursor.fetchone()
        cursor.close()
        
        if row:
            return {
                'user_id': row[0],
                'username': row[1],
                'created_at': str(row[2])
            }
        return None
    
    # Rating operations
    def add_rating(self, user_id: int, movie_id: int, rating: float) -> bool:
        """Add or update a movie rating"""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            # Check if rating exists
            cursor.execute(
                "SELECT rating_id FROM ratings WHERE user_id = ? AND movie_id = ?",
                (user_id, movie_id)
            )
            exists = cursor.fetchone()
            
            if exists:
                # Update existing rating
                cursor.execute(
                    "UPDATE ratings SET rating = ?, timestamp = GETDATE() WHERE user_id = ? AND movie_id = ?",
                    (rating, user_id, movie_id)
                )
            else:
                # Insert new rating
                cursor.execute(
                    "INSERT INTO ratings (user_id, movie_id, rating) VALUES (?, ?, ?)",
                    (user_id, movie_id, rating)
                )
            
            conn.commit()
            cursor.close()
            return True
        except Exception as e:
            print(f"Error adding rating: {e}")
            cursor.close()
            return False
    
    def get_user_ratings(self, user_id: int) -> List[Dict]:
        """Get all ratings for a user"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """SELECT r.rating_id, r.user_id, r.movie_id, r.rating, r.timestamp,
                      m.title, m.poster_path
               FROM ratings r
               LEFT JOIN movies_cache m ON r.movie_id = m.movie_id
               WHERE r.user_id = ?
               ORDER BY r.timestamp DESC""",
            (user_id,)
        )
        
        ratings = []
        for row in cursor.fetchall():
            ratings.append({
                'rating_id': row[0],
                'user_id': row[1],
                'movie_id': row[2],
                'rating': row[3],
                'timestamp': str(row[4]),
                'title': row[5],
                'poster_path': row[6]
            })
        
        cursor.close()
        return ratings
    
    def get_all_ratings(self) -> List[Dict]:
        """Get all ratings for collaborative filtering"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT user_id, movie_id, rating FROM ratings")
        
        ratings = []
        for row in cursor.fetchall():
            ratings.append({
                'user_id': row[0],
                'movie_id': row[1],
                'rating': row[2]
            })
        
        cursor.close()
        return ratings
    
    def get_user_rating_count(self, user_id: int) -> int:
        """Get total number of ratings by user"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT COUNT(*) FROM ratings WHERE user_id = ?",
            (user_id,)
        )
        count = cursor.fetchone()[0]
        cursor.close()
        return count
    
    # Movie cache operations
    def cache_movie(self, movie_data: Dict) -> bool:
        """Cache movie data"""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            # Check if movie exists
            cursor.execute(
                "SELECT movie_id FROM movies_cache WHERE movie_id = ?",
                (movie_data['movie_id'],)
            )
            exists = cursor.fetchone()
            
            if exists:
                # Update existing movie
                cursor.execute(
                    """UPDATE movies_cache SET 
                       title = ?, genres = ?, poster_path = ?, overview = ?,
                       vote_average = ?, release_date = ?, popularity = ?, runtime = ?,
                       cached_at = GETDATE()
                       WHERE movie_id = ?""",
                    (
                        movie_data['title'],
                        movie_data.get('genres', ''),
                        movie_data.get('poster_path', ''),
                        movie_data.get('overview', ''),
                        movie_data.get('vote_average', 0),
                        movie_data.get('release_date', ''),
                        movie_data.get('popularity', 0),
                        movie_data.get('runtime', 0),
                        movie_data['movie_id']
                    )
                )
            else:
                # Insert new movie
                cursor.execute(
                    """INSERT INTO movies_cache 
                       (movie_id, title, genres, poster_path, overview, vote_average, 
                        release_date, popularity, runtime)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (
                        movie_data['movie_id'],
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
            cursor.close()
            return True
        except Exception as e:
            print(f"Error caching movie: {e}")
            cursor.close()
            return False
    
    def get_cached_movie(self, movie_id: int) -> Optional[Dict]:
        """Get cached movie if not expired"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        expiry_hours = Config.CACHE_EXPIRY_HOURS
        cursor.execute(
            """SELECT movie_id, title, genres, poster_path, overview, 
                      vote_average, release_date, popularity, runtime, cached_at
               FROM movies_cache 
               WHERE movie_id = ? AND cached_at > DATEADD(hour, -?, GETDATE())""",
            (movie_id, expiry_hours)
        )
        
        row = cursor.fetchone()
        cursor.close()
        
        if row:
            return {
                'movie_id': row[0],
                'title': row[1],
                'genres': row[2],
                'poster_path': row[3],
                'overview': row[4],
                'vote_average': row[5],
                'release_date': row[6],
                'popularity': row[7],
                'runtime': row[8],
                'cached_at': str(row[9])
            }
        return None
    
    def get_all_cached_movies(self) -> List[Dict]:
        """Get all cached movies for ML training"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """SELECT movie_id, title, genres, poster_path, overview, 
                      vote_average, release_date, popularity, runtime, cached_at
               FROM movies_cache"""
        )
        
        movies = []
        for row in cursor.fetchall():
            movies.append({
                'movie_id': row[0],
                'title': row[1],
                'genres': row[2],
                'poster_path': row[3],
                'overview': row[4],
                'vote_average': row[5],
                'release_date': row[6],
                'popularity': row[7],
                'runtime': row[8],
                'cached_at': str(row[9])
            })
        
        cursor.close()
        return movies
    
    def clear_expired_cache(self):
        """Remove expired cache entries"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        expiry_hours = Config.CACHE_EXPIRY_HOURS
        cursor.execute(
            "DELETE FROM movies_cache WHERE cached_at < DATEADD(hour, -?, GETDATE())",
            (expiry_hours,)
        )
        
        conn.commit()
        cursor.close()
    
    # User preferences operations
    def update_user_preferences(self, user_id: int, 
                               favorite_genres: str = None,
                               favorite_actors: str = None) -> bool:
        """Update user preferences"""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            # Check if preferences exist
            cursor.execute(
                "SELECT user_id FROM user_preferences WHERE user_id = ?",
                (user_id,)
            )
            exists = cursor.fetchone()
            
            if exists:
                # Update
                updates = []
                params = []
                if favorite_genres is not None:
                    updates.append("favorite_genres = ?")
                    params.append(favorite_genres)
                if favorite_actors is not None:
                    updates.append("favorite_actors = ?")
                    params.append(favorite_actors)
                
                if updates:
                    updates.append("updated_at = GETDATE()")
                    params.append(user_id)
                    cursor.execute(
                        f"UPDATE user_preferences SET {', '.join(updates)} WHERE user_id = ?",
                        params
                    )
            else:
                # Insert
                cursor.execute(
                    "INSERT INTO user_preferences (user_id, favorite_genres, favorite_actors) VALUES (?, ?, ?)",
                    (user_id, favorite_genres, favorite_actors)
                )
            
            conn.commit()
            cursor.close()
            return True
        except Exception as e:
            print(f"Error updating preferences: {e}")
            cursor.close()
            return False
    
    def get_user_preferences(self, user_id: int) -> Optional[Dict]:
        """Get user preferences"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT user_id, favorite_genres, favorite_actors, updated_at FROM user_preferences WHERE user_id = ?",
            (user_id,)
        )
        row = cursor.fetchone()
        cursor.close()
        
        if row:
            return {
                'user_id': row[0],
                'favorite_genres': row[1],
                'favorite_actors': row[2],
                'updated_at': str(row[3])
            }
        return None
    
    # Chat history operations
    def save_chat(self, user_id: int, message: str, response: str, intent: str = None) -> bool:
        """Save chat interaction"""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            # Ensure user exists
            cursor.execute("SELECT user_id FROM users WHERE user_id = ?", (user_id,))
            if not cursor.fetchone():
                # Create default user if doesn't exist
                cursor.execute(
                    "INSERT INTO users (username) VALUES (?)",
                    (f"user_{user_id}",)
                )
                conn.commit()
            
            cursor.execute(
                "INSERT INTO chat_history (user_id, message, response, intent) VALUES (?, ?, ?, ?)",
                (user_id, message, response, intent)
            )
            conn.commit()
            cursor.close()
            return True
        except Exception as e:
            print(f"Error saving chat: {e}")
            cursor.close()
            return False
    
    def get_chat_history(self, user_id: int, limit: int = 10) -> List[Dict]:
        """Get recent chat history for a user"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """SELECT chat_id, user_id, message, response, intent, timestamp
               FROM chat_history 
               WHERE user_id = ?
               ORDER BY timestamp DESC
               OFFSET 0 ROWS FETCH NEXT ? ROWS ONLY""",
            (user_id, limit)
        )
        
        chats = []
        for row in cursor.fetchall():
            chats.append({
                'chat_id': row[0],
                'user_id': row[1],
                'message': row[2],
                'response': row[3],
                'intent': row[4],
                'timestamp': str(row[5])
            })
        
        cursor.close()
        return chats
    
    # Analytics
    def get_user_stats(self, user_id: int) -> Dict:
        """Get user statistics"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Get rating count
        cursor.execute(
            "SELECT COUNT(*) FROM ratings WHERE user_id = ?",
            (user_id,)
        )
        rating_count = cursor.fetchone()[0]
        
        # Get average rating
        cursor.execute(
            "SELECT AVG(CAST(rating AS FLOAT)) FROM ratings WHERE user_id = ?",
            (user_id,)
        )
        avg_rating = cursor.fetchone()[0] or 0
        
        # Get top genres
        cursor.execute(
            """SELECT TOP 3 m.genres, COUNT(*) as count
               FROM ratings r
               JOIN movies_cache m ON r.movie_id = m.movie_id
               WHERE r.user_id = ? AND m.genres IS NOT NULL
               GROUP BY m.genres
               ORDER BY count DESC""",
            (user_id,)
        )
        top_genres = [row[0] for row in cursor.fetchall()]
        
        cursor.close()
        
        return {
            'total_ratings': rating_count,
            'average_rating': round(avg_rating, 2),
            'top_genres': top_genres
        }


# Singleton instance
_sqlserver_db_instance = None

def get_sqlserver_db() -> SQLServerDatabase:
    """Get SQL Server database singleton instance"""
    global _sqlserver_db_instance
    if _sqlserver_db_instance is None:
        _sqlserver_db_instance = SQLServerDatabase()
    return _sqlserver_db_instance
