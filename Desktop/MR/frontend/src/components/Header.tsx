import { Film, Sparkles, Home, Search, Heart, Bookmark, MessageSquare, User } from "lucide-react";
import { Link, useLocation } from "react-router-dom";

const Header = () => {
  const location = useLocation();
  
  const navItems = [
    { path: "/", icon: Home, label: "Home" },
    { path: "/browse", icon: Search, label: "Browse" },
    { path: "/favorites", icon: Heart, label: "Favorites" },
    { path: "/watchlist", icon: Bookmark, label: "Watchlist" },
    { path: "/history", icon: MessageSquare, label: "History" },
    { path: "/profile", icon: User, label: "Profile" },
  ];

  return (
    <header className="glass-strong sticky top-0 z-50 px-6 py-4">
      <div className="container mx-auto flex items-center justify-between">
        <Link to="/" className="flex items-center gap-3 hover:scale-105 transition-transform">
          {/* Animated Logo */}
          <div className="relative">
            <div className="gradient-primary w-12 h-12 rounded-xl flex items-center justify-center animate-float">
              <Film className="w-6 h-6 text-white" />
            </div>
            <div className="absolute -top-1 -right-1 w-4 h-4 gradient-gold rounded-full flex items-center justify-center">
              <Sparkles className="w-2.5 h-2.5 text-background" />
            </div>
          </div>
          
          <div>
            <h1 className="font-display text-2xl font-bold text-gradient">
              CineMatch
            </h1>
            <p className="text-muted-foreground text-xs">
              Your AI-Powered Movie Companion
            </p>
          </div>
        </Link>
        
        {/* Navigation */}
        <nav className="hidden lg:flex items-center gap-2">
          {navItems.map((item) => {
            const isActive = location.pathname === item.path;
            return (
              <Link
                key={item.path}
                to={item.path}
                className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-all ${
                  isActive
                    ? "glass-strong text-primary"
                    : "text-muted-foreground hover:text-foreground hover:bg-white/5"
                }`}
              >
                <item.icon className="w-4 h-4" />
                <span className="text-sm font-medium">{item.label}</span>
              </Link>
            );
          })}
        </nav>

        {/* Mobile Menu Button - Future implementation */}
        <div className="lg:hidden">
          <div className="glass px-4 py-2 rounded-full text-sm text-muted-foreground">
            <span className="text-gold">●</span> Online
          </div>
        </div>
      </div>
    </header>
  );
};

export default Header;
