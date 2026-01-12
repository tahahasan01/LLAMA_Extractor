import unittest
from services.tmdb_service import TMDbService
from config import Config


class TestTMDbService(unittest.TestCase):
    """Test TMDb API integration"""
    
    @classmethod
    def setUpClass(cls):
        """Set up test fixtures"""
        cls.tmdb = TMDbService()
    
    def test_search_movies(self):
        """Test movie search"""
        # Skip if no API key
        if Config.TMDB_API_KEY == 'your_key_here':
            self.skipTest("TMDb API key not configured")
        
        result = self.tmdb.search_movies('Inception')
        
        self.assertIsNotNone(result)
        self.assertIn('results', result)
        self.assertTrue(len(result['results']) > 0)
        
        # Check first result
        movie = result['results'][0]
        self.assertIn('id', movie)
        self.assertIn('title', movie)
    
    def test_get_movie_details(self):
        """Test getting movie details"""
        # Skip if no API key
        if Config.TMDB_API_KEY == 'your_key_here':
            self.skipTest("TMDb API key not configured")
        
        # Fight Club movie ID
        movie_id = 550
        movie = self.tmdb.get_movie_details(movie_id)
        
        self.assertIsNotNone(movie)
        self.assertEqual(movie['id'], movie_id)
        self.assertIn('title', movie)
        self.assertIn('overview', movie)
    
    def test_get_trending_movies(self):
        """Test getting trending movies"""
        # Skip if no API key
        if Config.TMDB_API_KEY == 'your_key_here':
            self.skipTest("TMDb API key not configured")
        
        result = self.tmdb.get_trending_movies('week')
        
        self.assertIsNotNone(result)
        self.assertIn('results', result)
        self.assertTrue(len(result['results']) > 0)
    
    def test_get_genres(self):
        """Test getting genre list"""
        # Skip if no API key
        if Config.TMDB_API_KEY == 'your_key_here':
            self.skipTest("TMDb API key not configured")
        
        result = self.tmdb.get_genres()
        
        self.assertIsNotNone(result)
        self.assertIn('genres', result)
        self.assertTrue(len(result['genres']) > 0)
        
        # Check genre structure
        genre = result['genres'][0]
        self.assertIn('id', genre)
        self.assertIn('name', genre)
    
    def test_get_genre_id(self):
        """Test getting genre ID by name"""
        # Skip if no API key
        if Config.TMDB_API_KEY == 'your_key_here':
            self.skipTest("TMDb API key not configured")
        
        genre_id = self.tmdb.get_genre_id('Action')
        
        self.assertIsNotNone(genre_id)
        self.assertEqual(genre_id, 28)  # Action genre ID
    
    def test_discover_movies(self):
        """Test movie discovery with filters"""
        # Skip if no API key
        if Config.TMDB_API_KEY == 'your_key_here':
            self.skipTest("TMDb API key not configured")
        
        # Discover action movies from 2020
        result = self.tmdb.discover_movies(genre=28, year=2020)
        
        self.assertIsNotNone(result)
        self.assertIn('results', result)
    
    def test_get_providers(self):
        """Test getting streaming providers"""
        # Skip if no API key
        if Config.TMDB_API_KEY == 'your_key_here':
            self.skipTest("TMDb API key not configured")
        
        # Fight Club movie ID
        movie_id = 550
        providers = self.tmdb.get_watch_providers(movie_id, region='US')
        
        # May or may not have providers, just check it doesn't error
        self.assertIsInstance(providers, (dict, type(None)))
    
    def test_format_movie_data(self):
        """Test movie data formatting"""
        raw_movie = {
            'id': 550,
            'title': 'Fight Club',
            'overview': 'A ticking-time-bomb insomniac...',
            'poster_path': '/pB8BM7pdSp6B6Ih7QZ4DrQ3PmJK.jpg',
            'release_date': '1999-10-15',
            'vote_average': 8.4,
            'vote_count': 26000,
            'popularity': 61.416,
            'genre_ids': [18]
        }
        
        formatted = self.tmdb.format_movie_data(raw_movie)
        
        self.assertEqual(formatted['movie_id'], 550)
        self.assertEqual(formatted['title'], 'Fight Club')
        self.assertIn('poster_url', formatted)


if __name__ == '__main__':
    unittest.main()
