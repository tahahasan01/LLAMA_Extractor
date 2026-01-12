import { useState, useRef, useEffect } from "react";
import { TrendingUp, Flame, Heart, Popcorn, Clapperboard, MessageCircle, X, Minimize2, ArrowUp, ArrowDown } from "lucide-react";
import Header from "@/components/Header";
import ChatMessage from "@/components/ChatMessage";
import ChatInput from "@/components/ChatInput";
import TypingIndicator from "@/components/TypingIndicator";
import MovieCard from "@/components/MovieCard";
import MovieCardSkeleton from "@/components/MovieCardSkeleton";
import QuickSuggestion from "@/components/QuickSuggestion";
import RatingModal from "@/components/RatingModal";
import MovieDetailsModal from "@/components/MovieDetailsModal";
import Starfield from "@/components/Starfield";
import { api } from "@/services/api";
import type { Movie } from "@/types/movie";

interface Message {
  id: number;
  text: string;
  isBot: boolean;
  timestamp: string;
}

const suggestions = [
  { label: "Trending Now", icon: TrendingUp },
  { label: "Action Movies", icon: Flame },
  { label: "Romantic Comedies", icon: Heart },
  { label: "Family Friendly", icon: Popcorn },
  { label: "Award Winners", icon: Clapperboard },
];

const Index = () => {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: 1,
      text: "Hey there! I'm CineMatch, your AI movie companion. Tell me what kind of movie you're in the mood for, and I'll find the perfect match!",
      isBot: true,
      timestamp: "Just now",
    },
  ]);
  const [isTyping, setIsTyping] = useState(false);
  const [movies, setMovies] = useState<Movie[]>([]);
  const [isLoadingMovies, setIsLoadingMovies] = useState(false);
  const [selectedMovie, setSelectedMovie] = useState<Movie | null>(null);
  const [ratingMovieId, setRatingMovieId] = useState<number | null>(null);
  const [isChatOpen, setIsChatOpen] = useState(false);
  const [activeFilter, setActiveFilter] = useState<string>("trending");
  const [currentPage, setCurrentPage] = useState<number>(1);
  const [isLoadingDetails, setIsLoadingDetails] = useState(false);
  const [selectedYear, setSelectedYear] = useState<number | null>(null);
  const [personalizedMovies, setPersonalizedMovies] = useState<Movie[]>([]);
  const [isLoadingPersonalized, setIsLoadingPersonalized] = useState(false);
  const [chatPosition, setChatPosition] = useState({ x: 0, y: 0 });
  const [isDragging, setIsDragging] = useState(false);
  const [dragOffset, setDragOffset] = useState({ x: 0, y: 0 });
  const [sortOrder, setSortOrder] = useState<'desc' | 'asc'>('desc');
  const chatRef = useRef<HTMLDivElement>(null);
  const chatHeaderRef = useRef<HTMLDivElement>(null);

  // Load initial trending movies and personalized recommendations
  useEffect(() => {
    loadTrendingMovies();
    loadPersonalizedRecommendations();
  }, []);

  const loadTrendingMovies = async () => {
    try {
      setIsLoadingMovies(true);
      console.log("Index: Loading trending movies...");
      const trendingMovies = await api.getTrendingMovies();
      console.log("Index: Trending movies loaded:", trendingMovies);
      setMovies(trendingMovies);
      setActiveFilter("trending");
    } catch (error) {
      console.error("Index: Failed to load trending movies:", error);
      alert("Failed to load movies. Check console for details.");
    } finally {
      setIsLoadingMovies(false);
    }
  };

  const loadPersonalizedRecommendations = async () => {
    try {
      setIsLoadingPersonalized(true);
      console.log("Index: Loading personalized recommendations...");
      // Using user_id 1 (default user for localStorage tracking)
      const recommendations = await api.getPersonalizedRecommendations(1, 1, 10);
      console.log("Index: Personalized recommendations loaded:", recommendations);
      setPersonalizedMovies(recommendations);
    } catch (error) {
      console.error("Index: Failed to load personalized recommendations:", error);
    } finally {
      setIsLoadingPersonalized(false);
    }
  };

  const loadMoviesByFilter = async (filter: string, page: number = 1) => {
    try {
      setIsLoadingMovies(true);
      setActiveFilter(filter);
      setCurrentPage(page);
      setSelectedYear(null); // Clear year filter when changing category
      
      console.log(`Loading ${filter} movies, page ${page}`);
      
      let movieData: Movie[] = [];
      switch (filter) {
        case "popular":
          movieData = await api.getPopularMovies(page);
          break;
        case "top-rated":
          movieData = await api.getTopRatedMovies(page);
          break;
        case "now-playing":
          movieData = await api.getNowPlayingMovies(page);
          break;
        case "upcoming":
          movieData = await api.getUpcomingMovies(page);
          break;
        default:
          movieData = await api.getTrendingMovies();
      }
      
      console.log(`Received ${movieData.length} movies for ${filter}, page ${page}`);
      setMovies(movieData);
      window.scrollTo({ top: 0, behavior: 'smooth' });
    } catch (error) {
      console.error(`Failed to load ${filter} movies:`, error);
      alert(`Failed to load ${filter} movies. Please try again.`);
    } finally {
      setIsLoadingMovies(false);
    }
  };

  const loadMoviesByYear = async (year: number, page: number = 1) => {
    try {
      setIsLoadingMovies(true);
      setSelectedYear(year);
      setCurrentPage(page);
      setActiveFilter("year-filter");
      
      console.log(`Loading movies from year ${year}, page ${page}`);
      const movieData = await api.getMoviesByYear(year, page);
      console.log(`Received ${movieData.length} movies from year ${year}`);
      
      setMovies(movieData);
      window.scrollTo({ top: 0, behavior: 'smooth' });
    } catch (error) {
      console.error(`Failed to load movies from year ${year}:`, error);
      alert(`Failed to load movies from ${year}. Please try again.`);
    } finally {
      setIsLoadingMovies(false);
    }
  };

  const loadFilterWithYear = async (filter: string, page: number = 1, yearOverride?: number | null) => {
    try {
      setIsLoadingMovies(true);
      setActiveFilter(filter);
      setCurrentPage(page);
      
      // Use the year override if provided, otherwise use state
      const yearToUse = yearOverride !== undefined ? yearOverride : selectedYear;
      
      // Upcoming movies should never be filtered by year (only show 2026)
      const shouldApplyYear = yearToUse && filter !== "upcoming";
      
      console.log(`Loading ${filter} movies with year ${yearToUse}, page ${page}`);
      
      let movieData: Movie[] = [];
      
      // If a year is selected (and not for upcoming), apply year filter instead
      if (shouldApplyYear) {
        movieData = await api.getMoviesByYear(yearToUse, page);
      } else {
        // Otherwise load by category filter
        switch (filter) {
          case "popular":
            movieData = await api.getPopularMovies(page);
            break;
          case "top-rated":
            movieData = await api.getTopRatedMovies(page);
            break;
          case "now-playing":
            movieData = await api.getNowPlayingMovies(page);
            break;
          case "upcoming":
            movieData = await api.getUpcomingMovies(page);
            break;
          default:
            movieData = await api.getTrendingMovies();
        }
      }
      
      console.log(`Received ${movieData.length} movies for ${filter}${shouldApplyYear ? ` from ${yearToUse}` : ""}, page ${page}`);
      setMovies(movieData);
      window.scrollTo({ top: 0, behavior: 'smooth' });
    } catch (error) {
      console.error(`Failed to load ${filter} movies:`, error);
      alert(`Failed to load ${filter} movies. Please try again.`);
    } finally {
      setIsLoadingMovies(false);
    }
  };

  useEffect(() => {
    if (chatRef.current) {
      chatRef.current.scrollTop = chatRef.current.scrollHeight;
    }
  }, [messages, isTyping]);

  const handleMouseDown = (e: React.MouseEvent<HTMLDivElement>) => {
    if (!chatHeaderRef.current?.contains(e.currentTarget)) return;
    
    setIsDragging(true);
    const rect = chatRef.current?.getBoundingClientRect();
    if (rect) {
      setDragOffset({
        x: e.clientX - rect.left,
        y: e.clientY - rect.top,
      });
    }
  };

  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      if (!isDragging) return;
      
      setChatPosition({
        x: e.clientX - dragOffset.x,
        y: e.clientY - dragOffset.y,
      });
    };

    const handleMouseUp = () => {
      setIsDragging(false);
    };

    if (isDragging) {
      document.addEventListener('mousemove', handleMouseMove);
      document.addEventListener('mouseup', handleMouseUp);
    }

    return () => {
      document.removeEventListener('mousemove', handleMouseMove);
      document.removeEventListener('mouseup', handleMouseUp);
    };
  }, [isDragging, dragOffset]);

  const handleSendMessage = async (text: string) => {
    const newMessage: Message = {
      id: messages.length + 1,
      text,
      isBot: false,
      timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
    };
    
    setMessages((prev) => [...prev, newMessage]);
    setIsTyping(true);
    
    try {
      // Call the actual API
      const response = await api.sendMessage(text);
      
      setIsTyping(false);
      const botResponse: Message = {
        id: messages.length + 2,
        text: response.reply,
        isBot: true,
        timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
      };
      setMessages((prev) => [...prev, botResponse]);
      
      // Update movies with response
      if (response.movies && response.movies.length > 0) {
        setMovies(response.movies);
      }
      
      // Save to chat history
      const chatHistory = JSON.parse(localStorage.getItem("chatHistory") || "[]");
      chatHistory.push({
        id: Date.now(),
        message: text,
        reply: response.reply,
        intent: response.intent,
        timestamp: new Date().toISOString(),
        movieCount: response.movies?.length || 0
      });
      localStorage.setItem("chatHistory", JSON.stringify(chatHistory));
    } catch (error) {
      setIsTyping(false);
      const errorMessage: Message = {
        id: messages.length + 2,
        text: "Sorry, I'm having trouble connecting. Please make sure the backend server is running on http://localhost:5000",
        isBot: true,
        timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
      };
      setMessages((prev) => [...prev, errorMessage]);
      console.error("Failed to send message:", error);
    }
  };

  const handleSortByRating = (order: 'asc' | 'desc') => {
    setSortOrder(order);
    const sortedMovies = [...movies].sort((a, b) => {
      if (order === 'desc') {
        return (b.rating || 0) - (a.rating || 0);
      } else {
        return (a.rating || 0) - (b.rating || 0);
      }
    });
    setMovies(sortedMovies);
  };

  const handleSuggestionClick = (label: string) => {
    handleSendMessage(label);
  };

  const handleRateMovie = async (rating: number) => {
    if (!ratingMovieId) return;
    
    try {
      await api.rateMovie(ratingMovieId, rating);
      console.log(`Successfully rated movie ${ratingMovieId}: ${rating} stars`);
      setRatingMovieId(null);
    } catch (error) {
      console.error("Failed to rate movie:", error);
      alert("Failed to save rating. Please try again.");
    }
  };

  const handleMovieClick = async (movie: Movie) => {
    try {
      setIsLoadingDetails(true);
      // Fetch full movie details including trailer
      const fullDetails = await api.getMovieDetails(movie.id);
      setSelectedMovie(fullDetails);
    } catch (error) {
      console.error("Failed to load movie details:", error);
      // Fall back to basic movie data if details fetch fails
      setSelectedMovie(movie);
    } finally {
      setIsLoadingDetails(false);
    }
  };

  const ratingMovie = movies.find(m => m.id === ratingMovieId);

  return (
    <div className="min-h-screen bg-gradient-animated bg-grid vignette flex flex-col overflow-hidden">
      {/* Starfield Background */}
      <Starfield />

      {/* Floating Orbs */}
      <div className="orb orb-1" />
      <div className="orb orb-2" />
      <div className="orb orb-3" />

      {/* Aurora Effect */}
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

      <main className="flex-1 container mx-auto px-4 py-6 max-w-6xl relative z-10">
        {/* Movie Recommendations Grid - Main Content */}
        <div className="mb-6">
          <div className="flex items-center justify-between mb-6">
            <h2 className="font-display text-2xl font-semibold flex items-center gap-2">
              <span className="text-gradient">
                {selectedYear && `${selectedYear} - `}
                {activeFilter === "trending" && "Trending Now"}
                {activeFilter === "popular" && "Popular Movies"}
                {activeFilter === "top-rated" && "Top Rated"}
                {activeFilter === "now-playing" && "Now Playing"}
                {activeFilter === "upcoming" && "Upcoming"}
              </span>
            </h2>
            
            {/* Filter Buttons */}
            <div className="flex gap-2 flex-wrap">
              <button
                onClick={() => { setCurrentPage(1); loadFilterWithYear("trending", 1); }}
                className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${
                  activeFilter === "trending"
                    ? "bg-primary text-primary-foreground shadow-lg"
                    : "bg-card/50 backdrop-blur-sm hover:bg-card border border-border"
                }`}
              >
                Trending
              </button>
              <button
                onClick={() => { setCurrentPage(1); loadFilterWithYear("popular", 1); }}
                className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${
                  activeFilter === "popular"
                    ? "bg-primary text-primary-foreground shadow-lg"
                    : "bg-card/50 backdrop-blur-sm hover:bg-card border border-border"
                }`}
              >
                Popular
              </button>
              <button
                onClick={() => { setCurrentPage(1); loadFilterWithYear("top-rated", 1); }}
                className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${
                  activeFilter === "top-rated"
                    ? "bg-primary text-primary-foreground shadow-lg"
                    : "bg-card/50 backdrop-blur-sm hover:bg-card border border-border"
                }`}
              >
                Top Rated
              </button>
              <button
                onClick={() => { setCurrentPage(1); loadFilterWithYear("now-playing", 1); }}
                className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${
                  activeFilter === "now-playing"
                    ? "bg-primary text-primary-foreground shadow-lg"
                    : "bg-card/50 backdrop-blur-sm hover:bg-card border border-border"
                }`}
              >
                Now Playing
              </button>
              <button
                onClick={() => { setCurrentPage(1); loadFilterWithYear("upcoming", 1); }}
                className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${
                  activeFilter === "upcoming"
                    ? "bg-primary text-primary-foreground shadow-lg"
                    : "bg-card/50 backdrop-blur-sm hover:bg-card border border-border"
                }`}
              >
                Upcoming
              </button>
            </div>

            {/* Year Filter */}
            <div className="mt-6 flex flex-col gap-2">
              <label className="text-sm font-medium text-muted-foreground">Filter by Year:</label>
              <select
                value={selectedYear || ""}
                onChange={(e) => {
                  const year = e.target.value ? parseInt(e.target.value) : null;
                  if (year) {
                    setSelectedYear(year);
                    setCurrentPage(1);
                    // Apply year to current active filter, passing year directly
                    loadFilterWithYear(activeFilter, 1, year);
                  } else {
                    setSelectedYear(null);
                    setCurrentPage(1);
                    // Clear year and reload current filter
                    loadFilterWithYear(activeFilter, 1, null);
                  }
                }}
                className="px-4 py-2 rounded-lg bg-card border border-border text-foreground focus:outline-none focus:ring-2 focus:ring-primary transition-all"
              >
                <option value="">All Years</option>
                {[...Array(30)].map((_, i) => {
                  const year = new Date().getFullYear() - i;
                  return (
                    <option key={year} value={year}>
                      {year}
                    </option>
                  );
                })}
              </select>
            </div>

            {/* Sort by Rating - Icon Buttons */}
            <div className="mt-6 flex items-center gap-2">
              <button
                onClick={() => handleSortByRating('asc')}
                title="Sort: Lowest Rated First"
                className={`w-8 h-8 rounded flex items-center justify-center transition-all ${
                  sortOrder === 'asc'
                    ? "bg-primary text-primary-foreground shadow-lg"
                    : "bg-card border border-border hover:bg-primary/20 text-muted-foreground"
                }`}
              >
                <ArrowDown className="w-4 h-4" />
              </button>
              <button
                onClick={() => handleSortByRating('desc')}
                title="Sort: Highest Rated First"
                className={`w-8 h-8 rounded flex items-center justify-center transition-all ${
                  sortOrder === 'desc'
                    ? "bg-primary text-primary-foreground shadow-lg"
                    : "bg-card border border-border hover:bg-primary/20 text-muted-foreground"
                }`}
              >
                <ArrowUp className="w-4 h-4" />
              </button>
            </div>
          </div>
          
          {isLoadingMovies ? (
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
              {[...Array(6)].map((_, i) => (
                <MovieCardSkeleton key={i} />
              ))}
            </div>
          ) : movies.length === 0 ? (
            <div className="flex items-center justify-center py-20">
              <div className="text-center">
                <p className="text-muted-foreground mb-2">No movies found</p>
                <p className="text-sm text-muted-foreground">{selectedYear ? `No movies from ${selectedYear}` : "Start chatting to get personalized recommendations!"}</p>
              </div>
            </div>
          ) : (
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
              {movies.map((movie, index) => (
                <MovieCard
                  key={movie.id}
                  {...movie}
                  index={index}
                  onClick={() => handleMovieClick(movie)}
                  onFavoriteChange={() => {}}
                />
              ))}
            </div>
          )}
          
          {/* Pagination */}
          {!isLoadingMovies && movies.length > 0 && (activeFilter !== "trending" || selectedYear) && (
            <div className="flex justify-center items-center gap-2 mt-8">
              <button
                onClick={() => {
                  if (selectedYear) {
                    loadMoviesByYear(selectedYear, Math.max(1, currentPage - 1));
                  } else {
                    loadMoviesByFilter(activeFilter, Math.max(1, currentPage - 1));
                  }
                }}
                disabled={currentPage === 1}
                className={`px-4 py-2 rounded-lg font-medium transition-all ${
                  currentPage === 1
                    ? "bg-muted text-muted-foreground cursor-not-allowed"
                    : "bg-card border border-border hover:bg-primary hover:text-primary-foreground"
                }`}
              >
                Previous
              </button>
              
              <div className="flex gap-1">
                {[...Array(5)].map((_, i) => {
                  const pageNum = Math.max(1, currentPage - 2) + i;
                  return (
                    <button
                      key={pageNum}
                      onClick={() => {
                        loadFilterWithYear(activeFilter, pageNum);
                      }}
                      className={`w-10 h-10 rounded-lg font-medium transition-all ${
                        currentPage === pageNum
                          ? "bg-primary text-primary-foreground shadow-lg"
                          : "bg-card border border-border hover:bg-primary/20"
                      }`}
                    >
                      {pageNum}
                    </button>
                  );
                })}
              </div>
              
              <button
                onClick={() => {
                  loadFilterWithYear(activeFilter, currentPage + 1);
                }}
                className="px-4 py-2 rounded-lg font-medium bg-card border border-border hover:bg-primary hover:text-primary-foreground transition-all"
              >
                Next
              </button>
            </div>
          )}
        </div>

        {/* Personalized Recommendations Section */}
        {personalizedMovies.length > 0 && (
          <div className="mb-12">
            <h2 className="font-display text-2xl font-semibold mb-6 flex items-center gap-2">
              <span className="text-gradient">
                🎯 Recommended For You
              </span>
            </h2>
            
            {isLoadingPersonalized ? (
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                {[...Array(6)].map((_, i) => (
                  <MovieCardSkeleton key={i} />
                ))}
              </div>
            ) : personalizedMovies.length === 0 ? (
              <div className="flex items-center justify-center py-12">
                <p className="text-muted-foreground">No recommendations yet. Start watching movies to get personalized suggestions!</p>
              </div>
            ) : (
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                {personalizedMovies.slice(0, 6).map((movie) => (
                  <MovieCard
                    key={movie.id}
                    movie={movie}
                    onMovieClick={() => handleMovieClick(movie)}
                    isSelected={selectedMovie?.id === movie.id}
                  />
                ))}
              </div>
            )}
          </div>
        )}
      </main>

      {/* Floating Chat Button */}
      {!isChatOpen && (
        <button
          onClick={() => setIsChatOpen(true)}
          className="fixed bottom-6 right-6 w-16 h-16 gradient-primary rounded-full flex items-center justify-center shadow-2xl animate-pulse-glow hover:scale-110 transition-transform z-50"
          aria-label="Open chat"
        >
          <MessageCircle className="w-7 h-7 text-white" />
        </button>
      )}

      {/* Floating Chat Window */}
      {isChatOpen && (
        <div 
          ref={chatRef}
          onMouseDown={handleMouseDown}
          className="fixed w-[400px] h-[600px] glass-strong rounded-2xl shadow-2xl flex flex-col z-50 animate-scale-in"
          style={{
            left: `${chatPosition.x}px`,
            top: `${chatPosition.y}px`,
            cursor: isDragging ? 'grabbing' : 'grab',
          }}
        >
          {/* Chat Header */}
          <div 
            ref={chatHeaderRef}
            className="gradient-primary p-4 rounded-t-2xl flex items-center justify-between cursor-grab active:cursor-grabbing select-none"
          >
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-white/20 rounded-full flex items-center justify-center">
                <MessageCircle className="w-5 h-5 text-white" />
              </div>
              <div>
                <h3 className="font-semibold text-white">CineMatch AI</h3>
                <p className="text-xs text-white/80">Your movie companion</p>
              </div>
            </div>
            <button
              onClick={() => setIsChatOpen(false)}
              className="w-8 h-8 hover:bg-white/20 rounded-lg flex items-center justify-center transition-colors"
              aria-label="Close chat"
            >
              <Minimize2 className="w-5 h-5 text-white" />
            </button>
          </div>

          {/* Chat Messages */}
          <div
            ref={chatRef}
            className="flex-1 overflow-y-auto custom-scrollbar p-4 space-y-4"
          >
            {messages.map((message, index) => (
              <ChatMessage
                key={message.id}
                message={message.text}
                isBot={message.isBot}
                timestamp={message.timestamp}
                index={index}
              />
            ))}
            {isTyping && <TypingIndicator />}
          </div>

          {/* Quick Suggestions */}
          <div className="px-4 pb-2">
            <div className="flex flex-wrap gap-2">
              {suggestions.slice(0, 3).map((suggestion, index) => (
                <button
                  key={suggestion.label}
                  onClick={() => handleSuggestionClick(suggestion.label)}
                  className="glass px-3 py-1.5 rounded-full flex items-center gap-1.5 text-xs text-muted-foreground hover:text-foreground hover:bg-primary/20 transition-all hover:scale-105"
                >
                  <suggestion.icon className="w-3 h-3" />
                  {suggestion.label}
                </button>
              ))}
            </div>
          </div>

          {/* Chat Input */}
          <div className="p-4 border-t border-white/10">
            <ChatInput onSend={handleSendMessage} disabled={isTyping} />
          </div>
        </div>
      )}

      {/* Movie Details Modal */}
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

      {/* Rating Modal */}
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

export default Index;
