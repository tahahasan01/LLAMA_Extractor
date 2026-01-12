# Frontend - Removed Mock Data & Connected to Real API

## Changes Made

### 1. Created API Service (`frontend/src/services/api.ts`)
New file that handles all backend communication:

**Functions:**
- `sendMessage(message, userId?)` - Send chat message and get movie recommendations
- `getTrendingMovies()` - Get trending movies (uses sendMessage internally)
- `rateMovie(movieId, rating, userId?)` - Rate a movie (5-star scale)
- `getMovieDetails(movieId)` - Get full movie details with cast, director, trailer
- `searchMovies(query)` - Search for movies
- `getRecommendations(userId, limit)` - Get personalized recommendations
- `getGenres()` - Get list of available genres

**Configuration:**
- API Base URL: `http://localhost:5000/api`
- All requests use `fetch` API with proper error handling
- Returns typed responses matching TypeScript interfaces

### 2. Updated Index.tsx (`frontend/src/pages/Index.tsx`)

**Removed:**
- `import { mockMovies } from "@/data/mockMovies"` - No more mock data
- Hardcoded setTimeout simulations
- Static movie list

**Added:**
- `import { api } from "@/services/api"` - Real API integration
- `import MovieCardSkeleton` - Loading skeleton component
- State management for movies: `const [movies, setMovies] = useState<Movie[]>([])`
- Loading state: `const [isLoadingMovies, setIsLoadingMovies] = useState(false)`

**Changed:**

#### Initial Load
```tsx
// Load trending movies on mount
useEffect(() => {
  loadTrendingMovies();
}, []);

const loadTrendingMovies = async () => {
  try {
    setIsLoadingMovies(true);
    const trendingMovies = await api.getTrendingMovies();
    setMovies(trendingMovies);
  } catch (error) {
    console.error("Failed to load trending movies:", error);
  } finally {
    setIsLoadingMovies(false);
  }
};
```

#### Chat Message Handler
```tsx
const handleSendMessage = async (text: string) => {
  // Add user message to chat
  const newMessage: Message = { ... };
  setMessages((prev) => [...prev, newMessage]);
  setIsTyping(true);
  
  try {
    // Call real API
    const response = await api.sendMessage(text);
    
    // Add bot response
    const botResponse: Message = {
      text: response.reply,  // Use actual reply from backend
      ...
    };
    setMessages((prev) => [...prev, botResponse]);
    
    // Update movies with API results
    if (response.movies && response.movies.length > 0) {
      setMovies(response.movies);
    }
  } catch (error) {
    // Show error message if backend unavailable
    const errorMessage: Message = {
      text: "Sorry, I'm having trouble connecting. Please make sure the backend server is running on http://localhost:5000",
      ...
    };
    setMessages((prev) => [...prev, errorMessage]);
  }
};
```

#### Rating Handler
```tsx
const handleRateMovie = async (rating: number) => {
  if (!ratingMovieId) return;
  
  try {
    // Call real API with 5-star rating
    await api.rateMovie(ratingMovieId, rating);
    setRatingMovieId(null);
  } catch (error) {
    console.error("Failed to rate movie:", error);
    alert("Failed to save rating. Please try again.");
  }
};
```

#### Movie Display
```tsx
{isLoadingMovies ? (
  // Show 6 skeleton loaders while loading
  <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
    {[...Array(6)].map((_, i) => (
      <MovieCardSkeleton key={i} />
    ))}
  </div>
) : movies.length === 0 ? (
  // Show empty state
  <div>No movies yet. Start chatting!</div>
) : (
  // Show actual movies from API
  <div className="grid ...">
    {movies.map((movie, index) => (
      <MovieCard key={movie.id} {...movie} ... />
    ))}
  </div>
)}
```

## User Flow

### 1. Initial Page Load
1. Component mounts
2. `loadTrendingMovies()` called automatically
3. Shows skeleton loaders while fetching
4. Backend returns trending movies
5. Movies displayed in grid

### 2. Chat Interaction
1. User types message and clicks send
2. Message added to chat (user bubble)
3. Typing indicator appears
4. Backend processes message via `/api/chat`
5. Backend returns reply text + movie recommendations
6. Bot reply added to chat
7. Movie grid updates with new recommendations

### 3. Rating a Movie
1. User clicks movie card
2. Movie details modal opens
3. User clicks "Rate" button
4. Rating modal opens
5. User selects 1-5 stars
6. Frontend calls `api.rateMovie(id, stars)`
7. Backend saves rating (converts to 10-point scale)
8. Modal closes
9. Recommender retrains with new data

## API Endpoints Used

| Frontend Function | Backend Endpoint | Method |
|------------------|------------------|--------|
| `sendMessage()` | `/api/chat` | POST |
| `rateMovie()` | `/api/rate` | POST |
| `getMovieDetails()` | `/api/movie/{id}` | GET |
| `getRecommendations()` | `/api/recommendations/{user_id}` | GET |
| `getGenres()` | `/api/genres` | GET |

## Error Handling

### Network Errors
- Catches fetch errors
- Shows user-friendly error message in chat
- Logs error to console for debugging
- Doesn't crash the app

### Empty Results
- Shows "No movies yet" state
- Encourages user to start chatting
- Graceful handling of empty API responses

### Rating Failures
- Shows alert to user
- Logs error to console
- Doesn't close modal (user can retry)

## Backend Requirements

For frontend to work, backend must:
1. ✅ Be running on `http://localhost:5000`
2. ✅ Have CORS enabled (already configured)
3. ✅ Return movie data in correct format (already updated)
4. ✅ Handle optional `user_id` (already updated)
5. ✅ Accept 5-star ratings (already updated)

## Testing Checklist

Before connecting frontend:

**Backend:**
- [ ] Server running on port 5000
- [ ] TMDb API key configured
- [ ] Database connected
- [ ] Test endpoints with curl/Postman

**Frontend:**
- [ ] Install dependencies: `npm install`
- [ ] Start dev server: `npm run dev`
- [ ] Verify it connects to localhost:5000

**Integration:**
- [ ] Initial trending movies load
- [ ] Chat messages get real responses
- [ ] Movie grid updates with chat results
- [ ] Ratings save successfully
- [ ] Error messages show if backend down

## Migration from Mock Data

**Before:**
```tsx
import { mockMovies } from "@/data/mockMovies";
...
{mockMovies.map(movie => <MovieCard {...movie} />)}
```

**After:**
```tsx
import { api } from "@/services/api";
...
const [movies, setMovies] = useState<Movie[]>([]);
useEffect(() => {
  api.getTrendingMovies().then(setMovies);
}, []);
...
{movies.map(movie => <MovieCard {...movie} />)}
```

## Next Steps

1. **Start Backend Server**
   ```bash
   cd C:\Users\Syed Taha Hasan\Desktop\MR
   .\venv\Scripts\python.exe app.py
   ```

2. **Start Frontend Dev Server**
   ```bash
   cd frontend
   npm run dev
   ```

3. **Test the Integration**
   - Open browser to frontend URL (usually http://localhost:5173)
   - Verify trending movies load
   - Test chat functionality
   - Test rating movies

4. **Monitor Console**
   - Check browser console for errors
   - Check backend terminal for API requests
   - Verify data flowing correctly

## Troubleshooting

**Movies not loading:**
- Check backend is running on port 5000
- Check browser console for CORS errors
- Verify TMDb API key is valid

**Chat not responding:**
- Verify `/api/chat` endpoint works
- Check network tab for failed requests
- Ensure message format is correct

**Ratings not saving:**
- Check `/api/rate` endpoint
- Verify database connection
- Check rating is in 0-5 range
