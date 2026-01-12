import type { Movie } from "@/types/movie";

const API_BASE_URL = "http://localhost:5000/api";

interface ChatResponse {
  reply: string;
  movies: Movie[];
  intent: string;
  entities: Record<string, any>;
}

interface RatingResponse {
  success: boolean;
  message: string;
}

export const api = {
  /**
   * Send a chat message and get movie recommendations
   */
  async sendMessage(message: string, userId?: number): Promise<ChatResponse> {
    try {
      console.log(`API: Sending POST to ${API_BASE_URL}/chat with message:`, message);
      
      // Create abort controller for timeout
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 30000); // 30 second timeout
      
      const response = await fetch(`${API_BASE_URL}/chat`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          message,
          user_id: userId || 1,
        }),
        signal: controller.signal,
      });

      clearTimeout(timeoutId);
      console.log("API: Response status:", response.status, response.statusText);

      if (!response.ok) {
        const errorText = await response.text();
        console.error("API: Error response:", errorText);
        throw new Error(`Failed to send message: ${response.status} ${errorText}`);
      }

      const data = await response.json();
      console.log("API: Response data:", data);
      return data;
    } catch (error) {
      if (error.name === 'AbortError') {
        console.error("API: Request timed out after 30 seconds");
        throw new Error("Request timed out. The server might be slow or unresponsive.");
      }
      console.error("API: Fetch error:", error);
      throw error;
    }
  },

  /**
   * Get trending movies
   */
  async getTrendingMovies(): Promise<Movie[]> {
    console.log("API: Fetching trending movies...");
    const response = await this.sendMessage("trending movies");
    console.log("API: Received response:", response);
    console.log("API: Movies array:", response.movies);
    return response.movies;
  },

  /**
   * Get popular movies
   */
  async getPopularMovies(page: number = 1): Promise<Movie[]> {
    const response = await fetch(`${API_BASE_URL}/movies/popular?page=${page}`);
    if (!response.ok) throw new Error("Failed to fetch popular movies");
    const data = await response.json();
    return data.movies;
  },

  /**
   * Get top rated movies
   */
  async getTopRatedMovies(page: number = 1): Promise<Movie[]> {
    const response = await fetch(`${API_BASE_URL}/movies/top-rated?page=${page}`);
    if (!response.ok) throw new Error("Failed to fetch top rated movies");
    const data = await response.json();
    return data.movies;
  },

  /**
   * Get now playing movies
   */
  async getNowPlayingMovies(page: number = 1): Promise<Movie[]> {
    const response = await fetch(`${API_BASE_URL}/movies/now-playing?page=${page}`);
    if (!response.ok) throw new Error("Failed to fetch now playing movies");
    const data = await response.json();
    return data.movies;
  },

  /**
   * Get upcoming movies
   */
  async getUpcomingMovies(page: number = 1): Promise<Movie[]> {
    const response = await fetch(`${API_BASE_URL}/movies/upcoming?page=${page}`);
    if (!response.ok) throw new Error("Failed to fetch upcoming movies");
    const data = await response.json();
    return data.movies;
  },

  /**
   * Get movies by year
   */
  async getMoviesByYear(year: number, page: number = 1): Promise<Movie[]> {
    const response = await fetch(`${API_BASE_URL}/movies/by-year/${year}?page=${page}`);
    if (!response.ok) throw new Error("Failed to fetch movies by year");
    const data = await response.json();
    return data.movies;
  },

  /**
   * Rate a movie
   */
  async rateMovie(
    movieId: number,
    rating: number,
    userId?: number
  ): Promise<RatingResponse> {
    const response = await fetch(`${API_BASE_URL}/rate`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        movie_id: movieId,
        rating,
        user_id: userId,
      }),
    });

    if (!response.ok) {
      throw new Error("Failed to rate movie");
    }

    return response.json();
  },

  /**
   * Get detailed movie information
   */
  async getMovieDetails(movieId: number): Promise<Movie> {
    const response = await fetch(`${API_BASE_URL}/movie/${movieId}`);

    if (!response.ok) {
      throw new Error("Failed to get movie details");
    }

    return response.json();
  },

  /**
   * Search for movies
   */
  async searchMovies(query: string): Promise<Movie[]> {
    const response = await this.sendMessage(query);
    return response.movies;
  },

  /**
   * Get personalized recommendations
   */
  async getRecommendations(userId: number, limit: number = 10): Promise<Movie[]> {
    const response = await fetch(
      `${API_BASE_URL}/recommendations/${userId}?limit=${limit}`
    );

    if (!response.ok) {
      throw new Error("Failed to get recommendations");
    }

    const data = await response.json();
    return data.movies || [];
  },

  /**
   * Get genres list
   */
  async getGenres(): Promise<{ id: number; name: string }[]> {
    const response = await fetch(`${API_BASE_URL}/genres`);

    if (!response.ok) {
      throw new Error("Failed to get genres");
    }

    const data = await response.json();
    return data.genres || [];
  },

  /**
   * Get personalized recommendations based on user's viewing history
   */
  async getPersonalizedRecommendations(userId: number, page: number = 1, limit: number = 10): Promise<Movie[]> {
    const response = await fetch(`${API_BASE_URL}/personalized-recommendations?user_id=${userId}&page=${page}&limit=${limit}`);
    if (!response.ok) throw new Error("Failed to fetch personalized recommendations");
    const data = await response.json();
    return data.movies;
  },
};

