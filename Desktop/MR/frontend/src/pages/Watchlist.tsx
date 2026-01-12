import { useState, useEffect } from "react";
import { Bookmark, Trash2, Play } from "lucide-react";
import Header from "@/components/Header";
import MovieCard from "@/components/MovieCard";
import MovieDetailsModal from "@/components/MovieDetailsModal";
import RatingModal from "@/components/RatingModal";
import Starfield from "@/components/Starfield";
import type { Movie } from "@/types/movie";

const Watchlist = () => {
  const [watchlist, setWatchlist] = useState<Movie[]>([]);
  const [selectedMovie, setSelectedMovie] = useState<Movie | null>(null);
  const [ratingMovieId, setRatingMovieId] = useState<number | null>(null);

  useEffect(() => {
    loadWatchlist();
  }, []);

  const loadWatchlist = () => {
    // Load from localStorage
    const stored = localStorage.getItem("watchlist");
    if (stored) {
      setWatchlist(JSON.parse(stored));
    }
  };

  const removeFromWatchlist = (movieId: number) => {
    const updated = watchlist.filter(m => m.id !== movieId);
    setWatchlist(updated);
    localStorage.setItem("watchlist", JSON.stringify(updated));
  };

  const markAsWatched = (movieId: number) => {
    // Remove from watchlist when watched
    removeFromWatchlist(movieId);
    // Could also add to "watched history" here
  };

  const handleRateMovie = async (rating: number) => {
    if (!ratingMovieId) return;
    setRatingMovieId(null);
  };

  const ratingMovie = watchlist.find(m => m.id === ratingMovieId);

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
        <div className="mb-8">
          <h1 className="font-display text-3xl font-bold text-gradient flex items-center gap-3 mb-2">
            <Bookmark className="w-8 h-8 fill-primary text-primary" />
            My Watchlist
          </h1>
          <p className="text-muted-foreground">
            {watchlist.length} {watchlist.length === 1 ? "movie" : "movies"} to watch
          </p>
        </div>

        {watchlist.length === 0 ? (
          <div className="flex items-center justify-center py-20">
            <div className="text-center">
              <Bookmark className="w-16 h-16 text-muted-foreground mx-auto mb-4 opacity-20" />
              <p className="text-muted-foreground mb-2">Your watchlist is empty</p>
              <p className="text-sm text-muted-foreground">
                Add movies you want to watch later!
              </p>
            </div>
          </div>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            {watchlist.map((movie, index) => (
              <div key={movie.id} className="relative group">
                <MovieCard
                  {...movie}
                  index={index}
                  onClick={() => setSelectedMovie(movie)}
                  onFavoriteChange={() => {}}
                />
                <div className="absolute top-2 left-2 z-10 flex gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      markAsWatched(movie.id);
                    }}
                    className="p-2 bg-primary/90 backdrop-blur-sm rounded-lg hover:scale-110 transition-transform"
                    title="Mark as watched"
                  >
                    <Play className="w-4 h-4 text-white" fill="white" />
                  </button>
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      removeFromWatchlist(movie.id);
                    }}
                    className="p-2 bg-destructive/90 backdrop-blur-sm rounded-lg hover:scale-110 transition-transform"
                    title="Remove from watchlist"
                  >
                    <Trash2 className="w-4 h-4 text-white" />
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
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

export default Watchlist;
