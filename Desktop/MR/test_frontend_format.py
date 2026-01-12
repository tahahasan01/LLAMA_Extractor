import os
from dotenv import load_dotenv
load_dotenv()

from services.chat_service import get_chat_service

print("Testing updated chat service with frontend format...")

chat = get_chat_service()

# Test chat message
print("\n1. Testing chat with 'action movies'")
response = chat.process_message(1, "action movies")

print(f"\nReply: {response['reply']}")
print(f"Intent: {response['intent']}")
print(f"Movies found: {len(response['movies'])}")

if response['movies']:
    movie = response['movies'][0]
    print(f"\nFirst movie:")
    print(f"  Title: {movie.get('title')}")
    print(f"  ID: {movie.get('id')}")
    print(f"  Rating: {movie.get('rating')}/10")
    print(f"  Year: {movie.get('year')}")
    print(f"  Genres: {movie.get('genres')}")
    print(f"  Platforms: {len(movie.get('platforms', []))} streaming services")
    print(f"  Poster: {movie.get('poster')[:50] if movie.get('poster') else 'None'}...")
    print(f"  Overview: {movie.get('overview')[:100] if movie.get('overview') else 'None'}...")

print("\n✅ Frontend format test complete!")
