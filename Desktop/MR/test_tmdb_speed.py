import requests
import time

api_key = '70e59dae010cc7621e9a04aca108103f'

print("Testing TMDb API speed...")
start = time.time()
try:
    r = requests.get(
        'https://api.themoviedb.org/3/trending/movie/week',
        params={'api_key': api_key},
        timeout=10
    )
    elapsed = time.time() - start
    print(f"✓ Response time: {elapsed:.2f}s")
    print(f"✓ Status: {r.status_code}")
    print(f"✓ Results: {len(r.json().get('results', []))} movies")
except Exception as e:
    print(f"✗ Error: {e}")
