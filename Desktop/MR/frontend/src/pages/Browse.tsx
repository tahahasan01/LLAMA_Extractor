import { useState, useEffect } from "react";
import { Search, Filter, X } from "lucide-react";
import Header from "@/components/Header";
import MovieCard from "@/components/MovieCard";
import MovieCardSkeleton from "@/components/MovieCardSkeleton";
import MovieDetailsModal from "@/components/MovieDetailsModal";
import RatingModal from "@/components/RatingModal";
import Starfield from "@/components/Starfield";
import { api } from "@/services/api";
import type { Movie } from "@/types/movie";

const Browse = () => {
  const [movies, setMovies] = useState<Movie[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedGenre, setSelectedGenre] = useState<string>("");
  const [selectedYear, setSelectedYear] = useState<string>("");
  const [selectedMovie, setSelectedMovie] = useState<Movie | null>(null);
  const [ratingMovieId, setRatingMovieId] = useState<number | null>(null);
  const [genres, setGenres] = useState<{ id: number; name: string }[]>([]);

  useEffect(() => {
    loadGenres();
    loadMovies();
  }, []);

  const loadGenres = async () => {
    try {
      const genreList = await api.getGenres();
      setGenres(genreList);
    } catch (error) {
      console.error("Failed to load genres:", error);
    }
  };

  const loadMovies = async () => {
    try {
      setIsLoading(true);
      console.log("Loading trending movies...");
      const trendingMovies = await api.getTrendingMovies();
      console.log("Trending movies loaded:", trendingMovies);
      setMovies(trendingMovies);
    } catch (error) {
      console.error("Failed to load movies:", error);
      alert("Failed to load movies. Check console for details.");
    } finally {
      setIsLoading(false);
    }
  };

  const handleSearch = async () => {
    if (!searchQuery.trim() && !selectedGenre && !selectedYear) {
      loadMovies();
      return;
    }

    try {
      setIsLoading(true);
      let query = searchQuery.trim();
      
      if (selectedGenre) {
        query = `${selectedGenre} movies`;
      }
      
      if (selectedYear) {
        query = `${query} from ${selectedYear}`.trim();
      }

      const results = await api.searchMovies(query || "trending");
      setMovies(results);
    } catch (error) {
      console.error("Failed to search movies:", error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleClearFilters = () => {
    setSearchQuery("");
    setSelectedGenre("");
    setSelectedYear("");
    loadMovies();
  };

  const handleRateMovie = async (rating: number) => {
    if (!ratingMovieId) return;
    
    try {
      await api.rateMovie(ratingMovieId, rating);
      setRatingMovieId(null);
    } catch (error) {
      console.error("Failed to rate movie:", error);
      alert("Failed to save rating. Please try again.");
    }
  };

  const ratingMovie = movies.find(m => m.id === ratingMovieId);
  const currentYear = new Date().getFullYear();
  const years = Array.from({ length: 30 }, (_, i) => currentYear - i);

  return (
    <div className="min-h-screen bg-gradient-animated bg-grid vignette flex flex-col overflow-hidden">
      <Starfield />
      
      <div className="orb orb-1" />
      <div className="orb orb-2" />
      <div className="orb orb-3" />
      <div className="aurora" />

      {/* Shooting Stars */}
      <div className="shooting-star" />
      <div className="shooting-star" />
      <div className="shooting-star" />

      {/* Meteors */}
      <div className="meteor meteor-1" />
      <div className="meteor meteor-2" />
      <div className="meteor meteor-3" />

      <Header />

      <main className="flex-1 container mx-auto px-4 py-6 max-w-7xl relative z-10">
        {/* Search & Filter Section */}
        <div className="mb-8 space-y-4">
          <h1 className="font-display text-3xl font-bold text-gradient">Browse Movies</h1>
          
          {/* Search Bar */}
          <div className="flex flex-col sm:flex-row gap-3">
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-muted-foreground" />
              <input
                type="text"
                placeholder="Search movies..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && handleSearch()}
                className="w-full pl-10 pr-4 py-3 glass rounded-lg border border-white/10 focus:border-primary focus:outline-none focus:ring-2 focus:ring-primary/20 transition-all"
              />
            </div>
            <button
              onClick={handleSearch}
              className="px-6 py-3 gradient-primary rounded-lg font-semibold hover:scale-105 transition-transform whitespace-nowrap"
            >
              Search
            </button>
          </div>

          {/* Filters */}
          <div className="flex flex-wrap gap-3">
            <div className="flex items-center gap-2">
              <Filter className="w-4 h-4 text-muted-foreground" />
              <span className="text-sm font-semibold text-muted-foreground">Filters:</span>
            </div>
            
            <select
              value={selectedGenre}
              onChange={(e) => setSelectedGenre(e.target.value)}
              className="px-4 py-2 glass rounded-lg border border-white/10 focus:border-primary focus:outline-none text-sm"
            >
              <option value="">All Genres</option>
              {genres.map((genre) => (
                <option key={genre.id} value={genre.name}>
                  {genre.name}
                </option>
              ))}
            </select>

            <select
              value={selectedYear}
              onChange={(e) => setSelectedYear(e.target.value)}
              className="px-4 py-2 glass rounded-lg border border-white/10 focus:border-primary focus:outline-none text-sm"
            >
              <option value="">All Years</option>
              {years.map((year) => (
                <option key={year} value={year}>
                  {year}
                </option>
              ))}
            </select>

            {(searchQuery || selectedGenre || selectedYear) && (
              <button
                onClick={handleClearFilters}
                className="px-4 py-2 glass rounded-lg border border-white/10 hover:bg-white/5 transition-colors text-sm flex items-center gap-2"
              >
                <X className="w-4 h-4" />
                Clear
              </button>
            )}
          </div>
        </div>

        {/* Results */}
        <div className="mb-6">
          <p className="text-muted-foreground mb-4">
            {isLoading ? "Searching..." : `${movies.length} movies found`}
          </p>
          
          {isLoading ? (
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
              {[...Array(8)].map((_, i) => (
                <MovieCardSkeleton key={i} />
              ))}
            </div>
          ) : movies.length === 0 ? (
            <div className="flex items-center justify-center py-20">
              <div className="text-center">
                <p className="text-muted-foreground mb-2">No movies found</p>
                <p className="text-sm text-muted-foreground">Try adjusting your search or filters</p>
              </div>
            </div>
          ) : (
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
              {movies.map((movie, index) => (
                <MovieCard
                  key={movie.id}
                  {...movie}
                  index={index}
                  onClick={() => setSelectedMovie(movie)}
                  onFavoriteChange={() => {}}
                />
              ))}
            </div>
          )}
        </div>
      </main>

      {selectedMovie && (
        <MovieDetailsModal
          movie={selectedMovie}
          onClose={() => setSelectedMovie(null)}
          onRate={(movieId) => {
            setSelectedMovie(null);
            setRatingMovieId(movieId);
          }}
        />
      )}

      {ratingMovie && (
        <RatingModal
          movieTitle={ratingMovie.title}
          onClose={() => setRatingMovieId(null)}
          onRate={handleRateMovie}
        />
      )}
    </div>
  );
};

export default Browse;
