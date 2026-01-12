import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.neighbors import NearestNeighbors
from typing import List, Dict, Optional
from database import get_db
from services.tmdb_service import get_tmdb_service
from config import Config


class ContentBasedRecommender:
    """Content-based movie recommendation using TF-IDF and cosine similarity"""
    
    def __init__(self):
        """Initialize content-based recommender"""
        self.db = get_db()
        self.tmdb = get_tmdb_service()
        self.tfidf_vectorizer = TfidfVectorizer(
            max_features=5000,
            stop_words='english',
            ngram_range=(1, 2)
        )
        self.movie_features = None
        self.movie_ids = []
        self.similarity_matrix = None
        self.movies_df = None
    
    def build_features(self, movies: List[Dict]):
        """
        Build TF-IDF feature vectors from movie data
        
        Args:
            movies: List of movie dictionaries
        """
        if not movies:
            return
        
        # Convert to DataFrame
        self.movies_df = pd.DataFrame(movies)
        
        # Create feature text from genres, overview, and other metadata
        self.movies_df['features'] = self.movies_df.apply(
            lambda x: self._create_feature_text(x), axis=1
        )
        
        # Build TF-IDF vectors
        self.movie_features = self.tfidf_vectorizer.fit_transform(
            self.movies_df['features']
        )
        
        # Store movie IDs for reference
        self.movie_ids = self.movies_df['movie_id'].tolist()
        
        # Compute similarity matrix
        self.similarity_matrix = cosine_similarity(self.movie_features)
    
    def _create_feature_text(self, movie: pd.Series) -> str:
        """
        Create feature text from movie attributes
        
        Args:
            movie: Movie row from DataFrame
        
        Returns:
            Combined feature text
        """
        features = []
        
        # Add genres (weighted more)
        genres = movie.get('genres', '')
        if genres:
            features.extend([genres] * 3)  # Triple weight for genres
        
        # Add overview
        overview = movie.get('overview', '')
        if overview:
            features.append(overview)
        
        # Add title
        title = movie.get('title', '')
        if title:
            features.append(title)
        
        return ' '.join(features)
    
    def recommend(self, movie_id: int, n: int = 10) -> List[Dict]:
        """
        Get similar movies based on content
        
        Args:
            movie_id: TMDb movie ID
            n: Number of recommendations
        
        Returns:
            List of recommended movies
        """
        if self.similarity_matrix is None or movie_id not in self.movie_ids:
            return []
        
        # Get index of the movie
        movie_idx = self.movie_ids.index(movie_id)
        
        # Get similarity scores
        similarity_scores = list(enumerate(self.similarity_matrix[movie_idx]))
        
        # Sort by similarity (excluding the movie itself)
        similarity_scores = sorted(
            similarity_scores,
            key=lambda x: x[1],
            reverse=True
        )[1:n+1]
        
        # Get movie indices
        movie_indices = [i[0] for i in similarity_scores]
        
        # Return recommended movies
        recommendations = self.movies_df.iloc[movie_indices].to_dict('records')
        
        return recommendations
    
    def train(self):
        """Train the content-based model with cached movies"""
        # Get cached movies from database
        cached_movies = self.db.get_all_cached_movies()
        
        if len(cached_movies) < 10:
            # Not enough data, fetch popular movies
            print("Fetching popular movies for training...")
            self._fetch_training_data()
            cached_movies = self.db.get_all_cached_movies()
        
        # Build features
        self.build_features(cached_movies)
        
        print(f"Content-based model trained with {len(cached_movies)} movies")
    
    def _fetch_training_data(self, pages: int = 5):
        """Fetch popular movies for training"""
        for page in range(1, pages + 1):
            result = self.tmdb.get_popular_movies(page=page)
            
            if result and 'results' in result:
                for movie in result['results']:
                    # Get detailed info
                    details = self.tmdb.get_movie_details(movie['id'])
                    
                    if details:
                        movie_data = {
                            'movie_id': details['id'],
                            'title': details['title'],
                            'overview': details.get('overview', ''),
                            'genres': ','.join(details.get('genre_names', [])),
                            'poster_path': details.get('poster_path', ''),
                            'vote_average': details.get('vote_average', 0),
                            'release_date': details.get('release_date', ''),
                            'popularity': details.get('popularity', 0),
                            'runtime': details.get('runtime', 0)
                        }
                        
                        self.db.cache_movie(movie_data)


class CollaborativeRecommender:
    """Collaborative filtering using K-Nearest Neighbors"""
    
    def __init__(self):
        """Initialize collaborative recommender"""
        self.db = get_db()
        self.model = NearestNeighbors(
            metric='cosine',
            algorithm='brute',
            n_neighbors=20
        )
        self.user_item_matrix = None
        self.user_ids = []
        self.movie_ids = []
        self.is_trained = False
    
    def build_user_item_matrix(self) -> bool:
        """
        Build user-item rating matrix
        
        Returns:
            True if successful, False otherwise
        """
        # Get all ratings
        ratings = self.db.get_all_ratings()
        
        if len(ratings) < Config.MIN_RATINGS_FOR_COLLABORATIVE:
            print(f"Not enough ratings for collaborative filtering: {len(ratings)}")
            return False
        
        # Convert to DataFrame
        ratings_df = pd.DataFrame(ratings)
        
        # Create pivot table (user-item matrix)
        self.user_item_matrix = ratings_df.pivot_table(
            index='user_id',
            columns='movie_id',
            values='rating'
        ).fillna(0)
        
        # Store user and movie IDs
        self.user_ids = self.user_item_matrix.index.tolist()
        self.movie_ids = self.user_item_matrix.columns.tolist()
        
        return True
    
    def train_model(self) -> bool:
        """
        Train the collaborative filtering model
        
        Returns:
            True if successful, False otherwise
        """
        if not self.build_user_item_matrix():
            return False
        
        if len(self.user_ids) < 2:
            print("Not enough users for collaborative filtering")
            return False
        
        # Fit KNN model
        self.model.fit(self.user_item_matrix.values)
        self.is_trained = True
        
        print(f"Collaborative model trained with {len(self.user_ids)} users and {len(self.movie_ids)} movies")
        
        return True
    
    def recommend_for_user(self, user_id: int, n: int = 10) -> List[Dict]:
        """
        Get personalized recommendations for a user
        
        Args:
            user_id: User ID
            n: Number of recommendations
        
        Returns:
            List of recommended movies
        """
        if not self.is_trained or user_id not in self.user_ids:
            return []
        
        # Get user's rating vector
        user_idx = self.user_ids.index(user_id)
        user_ratings = self.user_item_matrix.iloc[user_idx].values.reshape(1, -1)
        
        # Find similar users
        distances, indices = self.model.kneighbors(user_ratings, n_neighbors=6)
        
        # Get movies rated highly by similar users but not seen by current user
        similar_users_indices = indices.flatten()[1:]  # Exclude the user themselves
        
        # Aggregate ratings from similar users
        recommendations = {}
        user_seen_movies = set(
            self.user_item_matrix.iloc[user_idx][
                self.user_item_matrix.iloc[user_idx] > 0
            ].index
        )
        
        for similar_user_idx in similar_users_indices:
            similar_user_ratings = self.user_item_matrix.iloc[similar_user_idx]
            
            for movie_id, rating in similar_user_ratings.items():
                if rating > 0 and movie_id not in user_seen_movies:
                    if movie_id not in recommendations:
                        recommendations[movie_id] = []
                    recommendations[movie_id].append(rating)
        
        # Calculate average ratings
        movie_scores = {
            movie_id: np.mean(ratings)
            for movie_id, ratings in recommendations.items()
        }
        
        # Sort by score
        top_movies = sorted(
            movie_scores.items(),
            key=lambda x: x[1],
            reverse=True
        )[:n]
        
        # Get movie details
        recommended_movies = []
        for movie_id, score in top_movies:
            movie = self.db.get_cached_movie(movie_id)
            if movie:
                movie['predicted_rating'] = round(score, 2)
                recommended_movies.append(movie)
        
        return recommended_movies
    
    def get_similar_users(self, user_id: int, n: int = 5) -> List[int]:
        """
        Find similar users based on rating patterns
        
        Args:
            user_id: User ID
            n: Number of similar users
        
        Returns:
            List of similar user IDs
        """
        if not self.is_trained or user_id not in self.user_ids:
            return []
        
        user_idx = self.user_ids.index(user_id)
        user_ratings = self.user_item_matrix.iloc[user_idx].values.reshape(1, -1)
        
        distances, indices = self.model.kneighbors(user_ratings, n_neighbors=n+1)
        
        similar_user_indices = indices.flatten()[1:]  # Exclude the user themselves
        similar_user_ids = [self.user_ids[idx] for idx in similar_user_indices]
        
        return similar_user_ids


class HybridRecommender:
    """Hybrid recommendation combining content-based and collaborative filtering"""
    
    def __init__(self):
        """Initialize hybrid recommender"""
        self.content_recommender = ContentBasedRecommender()
        self.collaborative_recommender = CollaborativeRecommender()
        self.db = get_db()
        self.tmdb = get_tmdb_service()
    
    def train(self):
        """Train both recommendation models"""
        print("Training content-based recommender...")
        self.content_recommender.train()
        
        print("Training collaborative recommender...")
        collab_success = self.collaborative_recommender.train_model()
        
        if not collab_success:
            print("Collaborative filtering not available (insufficient data)")
    
    def recommend(self, user_id: int, n: int = 10, 
                  movie_id: int = None) -> List[Dict]:
        """
        Get hybrid recommendations
        
        Args:
            user_id: User ID
            n: Number of recommendations
            movie_id: Optional movie ID for content-based recommendations
        
        Returns:
            List of recommended movies
        """
        recommendations = {}
        
        # Get collaborative recommendations if available
        if self.collaborative_recommender.is_trained:
            collab_recs = self.collaborative_recommender.recommend_for_user(
                user_id,
                n=int(n * Config.COLLABORATIVE_WEIGHT * 2)
            )
            
            for movie in collab_recs:
                movie_id_key = movie['movie_id']
                recommendations[movie_id_key] = {
                    'movie': movie,
                    'score': movie.get('predicted_rating', 3.5) * Config.COLLABORATIVE_WEIGHT
                }
        
        # Get content-based recommendations
        if movie_id:
            content_recs = self.content_recommender.recommend(
                movie_id,
                n=int(n * Config.CONTENT_BASED_WEIGHT * 2)
            )
        else:
            # Use user's highest rated movie as reference
            user_ratings = self.db.get_user_ratings(user_id)
            if user_ratings:
                top_rated = max(user_ratings, key=lambda x: x['rating'])
                content_recs = self.content_recommender.recommend(
                    top_rated['movie_id'],
                    n=int(n * Config.CONTENT_BASED_WEIGHT * 2)
                )
            else:
                content_recs = []
        
        # Add content-based recommendations
        for movie in content_recs:
            movie_id_key = movie['movie_id']
            if movie_id_key in recommendations:
                recommendations[movie_id_key]['score'] += Config.CONTENT_BASED_WEIGHT * 4
            else:
                recommendations[movie_id_key] = {
                    'movie': movie,
                    'score': Config.CONTENT_BASED_WEIGHT * 4
                }
        
        # Boost by popularity and recency
        for movie_id_key, rec_data in recommendations.items():
            movie = rec_data['movie']
            
            # Boost by vote average
            vote_avg = movie.get('vote_average', 5)
            rec_data['score'] *= (vote_avg / 10)
            
            # Boost by popularity
            popularity = movie.get('popularity', 1)
            rec_data['score'] *= (1 + np.log10(popularity) / 10)
        
        # Sort and return top N
        sorted_recs = sorted(
            recommendations.values(),
            key=lambda x: x['score'],
            reverse=True
        )[:n]
        
        return [rec['movie'] for rec in sorted_recs]
    
    def get_recommendations_for_new_user(self, n: int = 10) -> List[Dict]:
        """
        Get recommendations for new users without rating history
        
        Args:
            n: Number of recommendations
        
        Returns:
            List of popular/trending movies
        """
        # Return trending movies for new users
        result = self.tmdb.get_trending_movies('week')
        
        if result and 'results' in result:
            movies = result['results'][:n]
            return [self.tmdb.format_movie_data(m) for m in movies]
        
        return []


# Singleton instance
_hybrid_recommender = None

def get_recommender() -> HybridRecommender:
    """Get hybrid recommender singleton instance"""
    global _hybrid_recommender
    if _hybrid_recommender is None:
        _hybrid_recommender = HybridRecommender()
        _hybrid_recommender.train()
    return _hybrid_recommender
