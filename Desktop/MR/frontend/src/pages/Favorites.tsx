import { useState, useEffect } from "react";
import { Heart, Trash2 } from "lucide-react";
import Header from "@/components/Header";
import MovieCard from "@/components/MovieCard";
import MovieDetailsModal from "@/components/MovieDetailsModal";
import RatingModal from "@/components/RatingModal";
import Starfield from "@/components/Starfield";
import type { Movie } from "@/types/movie";

const Favorites = () => {
  const [favorites, setFavorites] = useState<Movie[]>([]);
  const [selectedMovie, setSelectedMovie] = useState<Movie | null>(null);
  const [ratingMovieId, setRatingMovieId] = useState<number | null>(null);

  useEffect(() => {
    loadFavorites();
  }, []);

  const loadFavorites = () => {
    // Load from localStorage
    const stored = localStorage.getItem("favorites");
    if (stored) {
      setFavorites(JSON.parse(stored));
    }
  };

  const removeFavorite = (movieId: number) => {
    const updated = favorites.filter(m => m.id !== movieId);
    setFavorites(updated);
    localStorage.setItem("favorites", JSON.stringify(updated));
  };

  const handleRateMovie = async (rating: number) => {
    if (!ratingMovieId) return;
    setRatingMovieId(null);
  };

  const ratingMovie = favorites.find(m => m.id === ratingMovieId);

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
            <Heart className="w-8 h-8 fill-primary text-primary" />
            My Favorites
          </h1>
          <p className="text-muted-foreground">
            {favorites.length} {favorites.length === 1 ? "movie" : "movies"} in your collection
          </p>
        </div>

        {favorites.length === 0 ? (
          <div className="flex items-center justify-center py-20">
            <div className="text-center">
              <Heart className="w-16 h-16 text-muted-foreground mx-auto mb-4 opacity-20" />
              <p className="text-muted-foreground mb-2">No favorites yet</p>
              <p className="text-sm text-muted-foreground">
                Start adding movies to your favorites from the browse page!
              </p>
            </div>
          </div>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            {favorites.map((movie, index) => (
              <div key={movie.id} className="relative group">
                <MovieCard
                  {...movie}
                  index={index}
                  onClick={() => setSelectedMovie(movie)}
                  onFavoriteChange={loadFavorites}
                />
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    removeFavorite(movie.id);
                  }}
                  className="absolute top-2 left-2 z-10 p-2 bg-destructive/90 backdrop-blur-sm rounded-lg opacity-0 group-hover:opacity-100 transition-opacity hover:scale-110"
                  title="Remove from favorites"
                >
                  <Trash2 className="w-4 h-4 text-white" />
                </button>
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

export default Favorites;
