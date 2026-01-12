import { useState, useEffect } from "react";
import { User, Star, Film, Heart, Bookmark, Settings } from "lucide-react";
import Header from "@/components/Header";
import Starfield from "@/components/Starfield";

const Profile = () => {
  const [username, setUsername] = useState("Movie Enthusiast");
  const [isEditing, setIsEditing] = useState(false);
  const [tempUsername, setTempUsername] = useState("");

  useEffect(() => {
    // Load username from localStorage
    const stored = localStorage.getItem("username");
    if (stored) {
      setUsername(stored);
    }
  }, []);

  const handleSaveUsername = () => {
    if (tempUsername.trim()) {
      setUsername(tempUsername.trim());
      localStorage.setItem("username", tempUsername.trim());
      setIsEditing(false);
    }
  };

  const stats = [
    {
      icon: Star,
      label: "Movies Rated",
      value: localStorage.getItem("totalRatings") || "0",
      color: "text-yellow-500"
    },
    {
      icon: Heart,
      label: "Favorites",
      value: JSON.parse(localStorage.getItem("favorites") || "[]").length,
      color: "text-red-500"
    },
    {
      icon: Bookmark,
      label: "Watchlist",
      value: JSON.parse(localStorage.getItem("watchlist") || "[]").length,
      color: "text-blue-500"
    },
    {
      icon: Film,
      label: "Conversations",
      value: JSON.parse(localStorage.getItem("chatHistory") || "[]").length,
      color: "text-purple-500"
    }
  ];

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

      <main className="flex-1 container mx-auto px-4 py-6 max-w-4xl relative z-10">
        <div className="mb-8">
          <h1 className="font-display text-3xl font-bold text-gradient flex items-center gap-3 mb-6">
            <User className="w-8 h-8 text-primary" />
            My Profile
          </h1>

          {/* Profile Card */}
          <div className="glass p-8 rounded-2xl border border-white/10">
            <div className="flex flex-col sm:flex-row items-center gap-6 mb-8">
              <div className="w-24 h-24 rounded-full gradient-primary flex items-center justify-center text-4xl font-bold text-white">
                {username.charAt(0).toUpperCase()}
              </div>
              
              <div className="flex-1 text-center sm:text-left">
                {isEditing ? (
                  <div className="flex gap-2">
                    <input
                      type="text"
                      value={tempUsername}
                      onChange={(e) => setTempUsername(e.target.value)}
                      placeholder="Enter your name"
                      className="flex-1 px-4 py-2 glass rounded-lg border border-white/10 focus:border-primary focus:outline-none"
                      autoFocus
                    />
                    <button
                      onClick={handleSaveUsername}
                      className="px-4 py-2 gradient-primary rounded-lg font-semibold"
                    >
                      Save
                    </button>
                    <button
                      onClick={() => setIsEditing(false)}
                      className="px-4 py-2 glass rounded-lg border border-white/10"
                    >
                      Cancel
                    </button>
                  </div>
                ) : (
                  <>
                    <h2 className="text-2xl font-bold mb-1">{username}</h2>
                    <button
                      onClick={() => {
                        setTempUsername(username);
                        setIsEditing(true);
                      }}
                      className="text-sm text-primary hover:underline"
                    >
                      Edit Name
                    </button>
                  </>
                )}
              </div>
            </div>

            {/* Stats Grid */}
            <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
              {stats.map((stat) => (
                <div
                  key={stat.label}
                  className="glass-strong p-4 rounded-xl text-center hover:scale-105 transition-transform"
                >
                  <stat.icon className={`w-8 h-8 mx-auto mb-2 ${stat.color}`} />
                  <p className="text-2xl font-bold mb-1">{stat.value}</p>
                  <p className="text-sm text-muted-foreground">{stat.label}</p>
                </div>
              ))}
            </div>
          </div>

          {/* Preferences Section */}
          <div className="mt-6 glass p-6 rounded-2xl border border-white/10">
            <h3 className="font-semibold text-lg mb-4 flex items-center gap-2">
              <Settings className="w-5 h-5 text-primary" />
              Preferences
            </h3>
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="font-medium">Email Notifications</p>
                  <p className="text-sm text-muted-foreground">Get recommendations via email</p>
                </div>
                <label className="relative inline-block w-12 h-6">
                  <input type="checkbox" className="sr-only peer" />
                  <div className="w-full h-full bg-muted rounded-full peer-checked:bg-primary transition-colors cursor-pointer"></div>
                  <div className="absolute top-0.5 left-0.5 w-5 h-5 bg-white rounded-full transition-transform peer-checked:translate-x-6"></div>
                </label>
              </div>
              
              <div className="flex items-center justify-between">
                <div>
                  <p className="font-medium">Show Adult Content</p>
                  <p className="text-sm text-muted-foreground">Include mature-rated movies</p>
                </div>
                <label className="relative inline-block w-12 h-6">
                  <input type="checkbox" className="sr-only peer" />
                  <div className="w-full h-full bg-muted rounded-full peer-checked:bg-primary transition-colors cursor-pointer"></div>
                  <div className="absolute top-0.5 left-0.5 w-5 h-5 bg-white rounded-full transition-transform peer-checked:translate-x-6"></div>
                </label>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
};

export default Profile;
