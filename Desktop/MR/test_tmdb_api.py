import os
from dotenv import load_dotenv
load_dotenv()

from services.tmdb_service import get_tmdb_service

print("Testing TMDb API...")
print(f"API Key configured: {'Yes' if os.getenv('TMDB_API_KEY') and os.getenv('TMDB_API_KEY') != 'your_key_here' else 'No'}")
print(f"API Key: {os.getenv('TMDB_API_KEY')[:10]}..." if os.getenv('TMDB_API_KEY') else "Not found")

tmdb = get_tmdb_service()

# Test search
print("\n1. Testing search...")
result = tmdb.search_movies('Inception')
if result and 'results' in result:
    print(f"✅ Search working! Found {len(result.get('results', []))} movies")
    if result['results']:
        print(f"   First result: {result['results'][0]['title']}")
else:
    print("❌ Search failed")

# Test trending
print("\n2. Testing trending...")
trending = tmdb.get_trending_movies('week')
if trending and 'results' in trending:
    print(f"✅ Trending working! Found {len(trending.get('results', []))} movies")
else:
    print("❌ Trending failed")

# Test genres
print("\n3. Testing genres...")
genres = tmdb.get_genres()
if genres and 'genres' in genres:
    print(f"✅ Genres working! Found {len(genres.get('genres', []))} genres")
else:
    print("❌ Genres failed")

print("\n✅ TMDb API is working correctly!" if result and trending and genres else "\n⚠️ Some API calls failed")
