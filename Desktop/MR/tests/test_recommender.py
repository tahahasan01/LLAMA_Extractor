import unittest
import numpy as np
import pandas as pd
from services.recommender import ContentBasedRecommender, CollaborativeRecommender


class TestContentBasedRecommender(unittest.TestCase):
    """Test content-based recommender"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.recommender = ContentBasedRecommender()
        
        # Sample movie data
        self.sample_movies = [
            {
                'movie_id': 1,
                'title': 'The Dark Knight',
                'genres': 'Action,Crime,Drama',
                'overview': 'Batman fights the Joker in Gotham City'
            },
            {
                'movie_id': 2,
                'title': 'Inception',
                'genres': 'Action,Sci-Fi,Thriller',
                'overview': 'A thief enters dreams to steal secrets'
            },
            {
                'movie_id': 3,
                'title': 'The Notebook',
                'genres': 'Romance,Drama',
                'overview': 'A love story spanning decades'
            },
            {
                'movie_id': 4,
                'title': 'Interstellar',
                'genres': 'Sci-Fi,Drama,Adventure',
                'overview': 'Astronauts travel through a wormhole'
            }
        ]
    
    def test_build_features(self):
        """Test feature building"""
        self.recommender.build_features(self.sample_movies)
        
        self.assertIsNotNone(self.recommender.movie_features)
        self.assertEqual(len(self.recommender.movie_ids), 4)
        self.assertIsNotNone(self.recommender.similarity_matrix)
    
    def test_recommend(self):
        """Test content-based recommendations"""
        self.recommender.build_features(self.sample_movies)
        
        # Get recommendations for Inception (Sci-Fi/Action)
        recommendations = self.recommender.recommend(movie_id=2, n=2)
        
        self.assertIsNotNone(recommendations)
        self.assertTrue(len(recommendations) > 0)
        
        # Should recommend similar Sci-Fi/Action movies
        rec_ids = [m['movie_id'] for m in recommendations]
        
        # Should not recommend the same movie
        self.assertNotIn(2, rec_ids)
    
    def test_create_feature_text(self):
        """Test feature text creation"""
        movie_series = pd.Series(self.sample_movies[0])
        feature_text = self.recommender._create_feature_text(movie_series)
        
        self.assertIsInstance(feature_text, str)
        self.assertTrue(len(feature_text) > 0)
        self.assertIn('Action', feature_text)


class TestCollaborativeRecommender(unittest.TestCase):
    """Test collaborative filtering recommender"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.recommender = CollaborativeRecommender()
        
        # Mock database ratings
        self.sample_ratings = [
            {'user_id': 1, 'movie_id': 1, 'rating': 5.0},
            {'user_id': 1, 'movie_id': 2, 'rating': 4.5},
            {'user_id': 1, 'movie_id': 3, 'rating': 2.0},
            {'user_id': 2, 'movie_id': 1, 'rating': 4.5},
            {'user_id': 2, 'movie_id': 2, 'rating': 5.0},
            {'user_id': 2, 'movie_id': 4, 'rating': 4.0},
            {'user_id': 3, 'movie_id': 3, 'rating': 5.0},
            {'user_id': 3, 'movie_id': 4, 'rating': 3.5},
            {'user_id': 3, 'movie_id': 1, 'rating': 2.5},
        ]
    
    def test_build_user_item_matrix(self):
        """Test building user-item matrix"""
        # Mock database method
        original_method = self.recommender.db.get_all_ratings
        self.recommender.db.get_all_ratings = lambda: self.sample_ratings
        
        result = self.recommender.build_user_item_matrix()
        
        self.assertTrue(result)
        self.assertIsNotNone(self.recommender.user_item_matrix)
        self.assertEqual(len(self.recommender.user_ids), 3)
        
        # Restore original method
        self.recommender.db.get_all_ratings = original_method
    
    def test_train_model(self):
        """Test model training"""
        # Mock database method
        original_method = self.recommender.db.get_all_ratings
        self.recommender.db.get_all_ratings = lambda: self.sample_ratings
        
        result = self.recommender.train_model()
        
        self.assertTrue(result)
        self.assertTrue(self.recommender.is_trained)
        
        # Restore original method
        self.recommender.db.get_all_ratings = original_method


class TestRecommenderIntegration(unittest.TestCase):
    """Test recommender system integration"""
    
    def test_similarity_calculation(self):
        """Test that similarity scores are reasonable"""
        recommender = ContentBasedRecommender()
        
        # Create movies with clear similarity
        movies = [
            {
                'movie_id': 1,
                'title': 'Action Movie 1',
                'genres': 'Action,Thriller',
                'overview': 'Explosions and car chases'
            },
            {
                'movie_id': 2,
                'title': 'Action Movie 2',
                'genres': 'Action,Thriller',
                'overview': 'More explosions and car chases'
            },
            {
                'movie_id': 3,
                'title': 'Romance Movie',
                'genres': 'Romance,Drama',
                'overview': 'Love story with flowers'
            }
        ]
        
        recommender.build_features(movies)
        
        # Action movies should be more similar to each other
        # than to romance movie
        sim_matrix = recommender.similarity_matrix
        
        action_similarity = sim_matrix[0][1]
        cross_genre_similarity = sim_matrix[0][2]
        
        self.assertGreater(action_similarity, cross_genre_similarity)


if __name__ == '__main__':
    unittest.main()
