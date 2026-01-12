import { Star, Play, ExternalLink, Heart } from "lucide-react";
import { useState, useEffect } from "react";
import type { Movie } from "@/types/movie";

interface MovieCardProps extends Movie {
  index: number;
  onClick?: () => void;
  onFavoriteChange?: () => void;
}

const MovieCard = (props: MovieCardProps) => {
  const { 
    id,
    title, 
    poster, 
    rating, 
    genres, 
    year, 
    platforms,
    overview,
    backdrop,
    runtime,
    director,
    cast,
    trailer,
    index,
    onClick,
    onFavoriteChange
  } = props;
  
  const [isHovered, setIsHovered] = useState(false);
  const [imageError, setImageError] = useState(false);
  const [imageLoading, setImageLoading] = useState(true);
  const [isFavorite, setIsFavorite] = useState(false);
  
  useEffect(() => {
    // Check if movie is in favorites
    const favorites = JSON.parse(localStorage.getItem("favorites") || "[]");
    setIsFavorite(favorites.some((m: Movie) => m.id === id));
  }, [id]);
  
  const toggleFavorite = (e: React.MouseEvent) => {
    e.stopPropagation();
    const favorites = JSON.parse(localStorage.getItem("favorites") || "[]");
    
    if (isFavorite) {
      // Remove from favorites
      const updated = favorites.filter((m: Movie) => m.id !== id);
      localStorage.setItem("favorites", JSON.stringify(updated));
      setIsFavorite(false);
    } else {
      // Add to favorites
      const movieData: Movie = {
        id, title, poster, rating, genres, year, platforms,
        overview, backdrop, runtime, director, cast, trailer
      };
      favorites.push(movieData);
      localStorage.setItem("favorites", JSON.stringify(favorites));
      setIsFavorite(true);
    }
    
    onFavoriteChange?.();
  };
  
  const placeholderImage = "https://via.placeholder.com/500x750/1a1a2e/eee?text=No+Poster";
  
  const handleImageError = () => {
    setImageError(true);
    setImageLoading(false);
  };
  
  const handleImageLoad = () => {
    setImageLoading(false);
  };
  
  const renderStars = (rating: number) => {
    const stars = [];
    const fullStars = Math.floor(rating / 2);
    const hasHalf = rating % 2 >= 1;
    
    for (let i = 0; i < 5; i++) {
      if (i < fullStars) {
        stars.push(
          <Star key={i} className="w-3.5 h-3.5 fill-gold text-gold" />
        );
      } else if (i === fullStars && hasHalf) {
        stars.push(
          <div key={i} className="relative">
            <Star className="w-3.5 h-3.5 text-muted-foreground" />
            <div className="absolute inset-0 overflow-hidden w-1/2">
              <Star className="w-3.5 h-3.5 fill-gold text-gold" />
            </div>
          </div>
        );
      } else {
        stars.push(
          <Star key={i} className="w-3.5 h-3.5 text-muted-foreground" />
        );
      }
    }
    return stars;
  };
  
  return (
    <div
      className="card-elevated overflow-hidden cursor-pointer group opacity-0 animate-scale-in"
      style={{ animationDelay: `${index * 0.1}s`, animationFillMode: "forwards" }}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      onClick={onClick}
    >
      {/* Poster Container */}
      <div className="relative aspect-[2/3] overflow-hidden bg-muted">
        {imageLoading && (
          <div className="absolute inset-0 flex items-center justify-center bg-muted animate-pulse">
            <div className="text-muted-foreground text-sm">Loading...</div>
          </div>
        )}
        <img
          src={imageError ? placeholderImage : (poster || placeholderImage)}
          alt={title}
          className="w-full h-full object-cover transition-transform duration-500 group-hover:scale-110"
          onError={handleImageError}
          onLoad={handleImageLoad}
          loading="lazy"
        />
        
        {/* Gradient Overlay */}
        <div className="absolute inset-0 bg-gradient-to-t from-background via-background/20 to-transparent opacity-60 group-hover:opacity-80 transition-opacity duration-300" />
        
        {/* Play Button - appears on hover */}
        <div className={`absolute inset-0 flex items-center justify-center transition-all duration-300 ${isHovered ? "opacity-100" : "opacity-0"}`}>
          <button className="w-16 h-16 gradient-primary rounded-full flex items-center justify-center shadow-xl animate-pulse-glow transform hover:scale-110 transition-transform">
            <Play className="w-7 h-7 text-white ml-1" fill="white" />
          </button>
        </div>
        
        {/* Rating Badge */}
        <div className="absolute top-3 right-3 glass-strong px-2 py-1 rounded-lg flex items-center gap-1">
          <Star className="w-3.5 h-3.5 fill-gold text-gold" />
          <span className="text-xs font-semibold">{rating.toFixed(1)}</span>
        </div>
        
        {/* Favorite Button */}
        <button
          onClick={toggleFavorite}
          className="absolute top-3 left-3 p-2 glass-strong rounded-full transition-all hover:scale-110"
        >
          <Heart 
            className={`w-4 h-4 transition-all ${isFavorite ? 'fill-red-500 text-red-500' : 'text-white'}`}
          />
        </button>
      </div>
      
      {/* Content */}
      <div className="p-4 space-y-3">
        <div>
          <h3 className="font-semibold text-lg leading-tight line-clamp-1 group-hover:text-primary transition-colors">
            {title}
          </h3>
          <p className="text-muted-foreground text-sm">{year}</p>
        </div>
        
        {/* Stars */}
        <div className="flex items-center gap-0.5">
          {renderStars(rating)}
        </div>
        
        {/* Genre Tags */}
        <div className="flex flex-wrap gap-1.5">
          {genres.slice(0, 3).map((genre) => (
            <span
              key={genre}
              className="px-2.5 py-1 text-xs rounded-full bg-muted text-muted-foreground"
            >
              {genre}
            </span>
          ))}
        </div>
        
        {/* Streaming Platforms */}
        <div className={`overflow-hidden transition-all duration-300 ${isHovered ? "max-h-20 opacity-100" : "max-h-0 opacity-0"}`}>
          <div className="pt-2 border-t border-border">
            <p className="text-xs text-muted-foreground mb-2">Watch on:</p>
            <div className="flex gap-2">
              {platforms.map((platform) => (
                <button
                  key={platform.name}
                  className="flex items-center gap-1 px-3 py-1.5 rounded-lg text-xs font-medium transition-all hover:scale-105"
                  style={{ backgroundColor: platform.color }}
                  onClick={(e) => e.stopPropagation()}
                >
                  <ExternalLink className="w-3 h-3" />
                  {platform.name}
                </button>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default MovieCard;
