import { X, Star, Play, Clock, Calendar, Users, ExternalLink, Heart, Bookmark } from "lucide-react";
import { useState, useEffect } from "react";
import type { Movie } from "@/types/movie";

interface MovieDetailsModalProps {
  movie: Movie;
  onClose: () => void;
  onRate: (movieId: number) => void;
}

const MovieDetailsModal = ({ movie, onClose, onRate }: MovieDetailsModalProps) => {
  const [isFavorite, setIsFavorite] = useState(false);
  const [inWatchlist, setInWatchlist] = useState(false);
  const [showTrailer, setShowTrailer] = useState(false);
  const [backdropError, setBackdropError] = useState(false);
  const [posterError, setPosterError] = useState(false);
  
  useEffect(() => {
    // Check if movie is in favorites
    const favorites = JSON.parse(localStorage.getItem("favorites") || "[]");
    setIsFavorite(favorites.some((m: Movie) => m.id === movie.id));
    
    // Check if movie is in watchlist
    const watchlist = JSON.parse(localStorage.getItem("watchlist") || "[]");
    setInWatchlist(watchlist.some((m: Movie) => m.id === movie.id));
  }, [movie.id]);
  
  const toggleFavorite = () => {
    const favorites = JSON.parse(localStorage.getItem("favorites") || "[]");
    
    if (isFavorite) {
      const updated = favorites.filter((m: Movie) => m.id !== movie.id);
      localStorage.setItem("favorites", JSON.stringify(updated));
      setIsFavorite(false);
    } else {
      favorites.push(movie);
      localStorage.setItem("favorites", JSON.stringify(favorites));
      setIsFavorite(true);
    }
  };
  
  const toggleWatchlist = () => {
    const watchlist = JSON.parse(localStorage.getItem("watchlist") || "[]");
    
    if (inWatchlist) {
      const updated = watchlist.filter((m: Movie) => m.id !== movie.id);
      localStorage.setItem("watchlist", JSON.stringify(updated));
      setInWatchlist(false);
    } else {
      watchlist.push(movie);
      localStorage.setItem("watchlist", JSON.stringify(watchlist));
      setInWatchlist(true);
    }
  };
  
  const placeholderImage = "https://via.placeholder.com/500x750/1a1a2e/eee?text=No+Poster";
  const backdropImage = backdropError ? (movie.poster || placeholderImage) : (movie.backdrop || movie.poster || placeholderImage);
  const posterImage = posterError ? placeholderImage : (movie.poster || placeholderImage);

  const renderStars = (rating: number) => {
    const stars = [];
    const fullStars = Math.floor(rating / 2);
    const hasHalf = rating % 2 >= 1;
    
    for (let i = 0; i < 5; i++) {
      if (i < fullStars) {
        stars.push(<Star key={i} className="w-4 h-4 fill-gold text-gold" />);
      } else if (i === fullStars && hasHalf) {
        stars.push(
          <div key={i} className="relative">
            <Star className="w-4 h-4 text-muted-foreground" />
            <div className="absolute inset-0 overflow-hidden w-1/2">
              <Star className="w-4 h-4 fill-gold text-gold" />
            </div>
          </div>
        );
      } else {
        stars.push(<Star key={i} className="w-4 h-4 text-muted-foreground" />);
      }
    }
    return stars;
  };

  return (
    <div 
      className="fixed inset-0 z-50 flex items-center justify-center p-4 animate-fade-in-up" 
      style={{ animationDuration: "0.2s" }}
    >
      {/* Backdrop with blur */}
      <div 
        className="absolute inset-0 bg-background/90 backdrop-blur-md"
        onClick={onClose}
      />
      
      {/* Modal Container */}
      <div className="relative w-full max-w-4xl max-h-[90vh] overflow-hidden rounded-2xl glass-strong animate-scale-in">
        {/* Close Button */}
        <button
          onClick={onClose}
          className="absolute top-4 right-4 z-20 p-2 rounded-full bg-background/50 backdrop-blur-sm text-foreground hover:bg-background/70 transition-colors"
        >
          <X className="w-5 h-5" />
        </button>

        {/* Scrollable Content */}
        <div className="overflow-y-auto max-h-[90vh] custom-scrollbar">
          {/* Hero Section with Backdrop */}
          <div className="relative h-64 sm:h-80 overflow-hidden bg-muted">
            {showTrailer && movie.trailer ? (
              <div className="w-full h-full">
                <iframe
                  src={movie.trailer.replace('watch?v=', 'embed/')}
                  className="w-full h-full"
                  allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                  allowFullScreen
                />
              </div>
            ) : (
              <>
                <img
                  src={backdropImage}
                  alt={movie.title}
                  className="w-full h-full object-cover"
                  onError={() => setBackdropError(true)}
                  loading="lazy"
                />
                <div className="absolute inset-0 bg-gradient-to-t from-card via-card/50 to-transparent" />
                
                {/* Floating Play Button */}
                {movie.trailer && (
                  <button
                    onClick={() => setShowTrailer(true)}
                    className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-20 h-20 gradient-primary rounded-full flex items-center justify-center shadow-2xl animate-pulse-glow hover:scale-110 transition-transform"
                  >
                    <Play className="w-8 h-8 text-white ml-1" fill="white" />
                  </button>
                )}
              </>
            )}
          </div>

          {/* Content Section */}
          <div className="p-6 sm:p-8 space-y-6">
            {/* Header */}
            <div className="flex flex-col sm:flex-row gap-6">
              {/* Poster Thumbnail */}
              <div className="hidden sm:block flex-shrink-0 -mt-24 relative z-10">
                <img
                  src={posterImage}
                  alt={movie.title}
                  className="w-32 h-48 object-cover rounded-xl shadow-2xl border-4 border-card"
                  onError={() => setPosterError(true)}
                  loading="lazy"
                />
              </div>

              {/* Title & Meta */}
              <div className="flex-1 space-y-3">
                <h2 className="font-display text-2xl sm:text-3xl font-bold leading-tight">
                  {movie.title}
                </h2>

                {/* Rating & Meta */}
                <div className="flex flex-wrap items-center gap-4 text-sm">
                  <div className="flex items-center gap-1.5">
                    {renderStars(movie.rating)}
                    <span className="font-semibold ml-1">{movie.rating.toFixed(1)}</span>
                  </div>
                  <div className="flex items-center gap-1.5 text-muted-foreground">
                    <Calendar className="w-4 h-4" />
                    <span>{movie.year}</span>
                  </div>
                  {movie.runtime && (
                    <div className="flex items-center gap-1.5 text-muted-foreground">
                      <Clock className="w-4 h-4" />
                      <span>{movie.runtime} min</span>
                    </div>
                  )}
                </div>

                {/* Genres */}
                <div className="flex flex-wrap gap-2">
                  {movie.genres.map((genre) => (
                    <span
                      key={genre}
                      className="px-3 py-1 text-xs font-medium rounded-full bg-primary/20 text-primary"
                    >
                      {genre}
                    </span>
                  ))}
                </div>
              </div>
            </div>

            {/* Overview */}
            {movie.overview && (
              <div className="space-y-2">
                <h3 className="font-semibold text-lg">Overview</h3>
                <p className="text-muted-foreground leading-relaxed">
                  {movie.overview}
                </p>
              </div>
            )}

            {/* Director & Cast */}
            <div className="grid sm:grid-cols-2 gap-6">
              {movie.director && (
                <div className="space-y-2">
                  <h4 className="font-semibold text-sm text-muted-foreground uppercase tracking-wider">
                    Director
                  </h4>
                  <p className="font-medium">{movie.director}</p>
                </div>
              )}
              {movie.cast && movie.cast.length > 0 && (
                <div className="space-y-2">
                  <h4 className="font-semibold text-sm text-muted-foreground uppercase tracking-wider flex items-center gap-2">
                    <Users className="w-4 h-4" />
                    Top Cast
                  </h4>
                  <p className="text-foreground">{movie.cast.join(", ")}</p>
                </div>
              )}
            </div>

            {/* Action Buttons */}
            <div className="flex flex-wrap gap-3 pt-4 border-t border-border">
              {/* Primary Actions */}
              <div className="flex flex-wrap gap-3 w-full">
                <button
                  onClick={toggleFavorite}
                  className={`flex items-center gap-2 px-5 py-2.5 rounded-lg font-medium transition-all hover:scale-105 ${
                    isFavorite 
                      ? "bg-red-500/20 text-red-500 border border-red-500/30" 
                      : "bg-muted text-muted-foreground hover:bg-red-500/10 hover:text-red-500 border border-border"
                  }`}
                >
                  <Heart className={`w-5 h-5 ${isFavorite ? "fill-current" : ""}`} />
                  {isFavorite ? "Favorited" : "Favorite"}
                </button>
                
                <button
                  onClick={toggleWatchlist}
                  className={`flex items-center gap-2 px-5 py-2.5 rounded-lg font-medium transition-all hover:scale-105 ${
                    inWatchlist 
                      ? "bg-primary/20 text-primary border border-primary/30" 
                      : "bg-muted text-muted-foreground hover:bg-primary/10 hover:text-primary border border-border"
                  }`}
                >
                  <Bookmark className={`w-5 h-5 ${inWatchlist ? "fill-current" : ""}`} />
                  {inWatchlist ? "In Watchlist" : "Add to Watchlist"}
                </button>

                {movie.trailer && (
                  <button
                    onClick={() => setShowTrailer(!showTrailer)}
                    className="flex items-center gap-2 px-5 py-2.5 rounded-lg font-medium gradient-primary text-white transition-all hover:opacity-90 hover:scale-105"
                  >
                    <Play className="w-5 h-5" fill="white" />
                    {showTrailer ? "Hide Trailer" : "Play Trailer"}
                  </button>
                )}

                <button
                  onClick={() => onRate(movie.id)}
                  className="flex items-center gap-2 px-5 py-2.5 rounded-lg font-medium bg-amber-500/20 text-amber-500 border border-amber-500/30 transition-all hover:bg-amber-500/30 hover:scale-105"
                >
                  <Star className="w-5 h-5" />
                  Rate Movie
                </button>
              </div>

              {/* Watch Platforms */}
              <div className="w-full mt-2">
                <p className="text-xs text-muted-foreground mb-2">Watch on:</p>
                <div className="flex flex-wrap gap-2">
                  {movie.platforms && movie.platforms.length > 0 ? (
                    movie.platforms.map((platform) => (
                      <a
                        key={platform.name}
                        href={platform.link || `https://www.themoviedb.org/movie/${movie.id}/watch`}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="flex items-center gap-1.5 px-4 py-2 rounded-lg text-sm font-medium text-white transition-all hover:scale-105 hover:shadow-lg"
                        style={{ backgroundColor: platform.color }}
                      >
                        <ExternalLink className="w-3.5 h-3.5" />
                        {platform.name}
                      </a>
                    ))
                  ) : (
                    <a
                      href={`https://www.themoviedb.org/movie/${movie.id}/watch`}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-sm text-muted-foreground hover:text-primary transition-colors flex items-center gap-2"
                    >
                      <ExternalLink className="w-4 h-4" />
                      Find where to watch
                    </a>
                  )}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default MovieDetailsModal;
