import { useState, useEffect } from "react";
import { MessageSquare, Calendar, Trash2, Search } from "lucide-react";
import Header from "@/components/Header";
import Starfield from "@/components/Starfield";

interface ChatHistoryItem {
  id: number;
  message: string;
  reply: string;
  intent: string;
  timestamp: string;
  movieCount: number;
}

const History = () => {
  const [history, setHistory] = useState<ChatHistoryItem[]>([]);
  const [searchQuery, setSearchQuery] = useState("");

  useEffect(() => {
    loadHistory();
  }, []);

  const loadHistory = () => {
    // Load from localStorage
    const stored = localStorage.getItem("chatHistory");
    if (stored) {
      setHistory(JSON.parse(stored));
    }
  };

  const clearHistory = () => {
    if (confirm("Are you sure you want to clear all chat history?")) {
      setHistory([]);
      localStorage.removeItem("chatHistory");
    }
  };

  const deleteItem = (id: number) => {
    const updated = history.filter(h => h.id !== id);
    setHistory(updated);
    localStorage.setItem("chatHistory", JSON.stringify(updated));
  };

  const filteredHistory = history.filter(item =>
    item.message.toLowerCase().includes(searchQuery.toLowerCase()) ||
    item.reply.toLowerCase().includes(searchQuery.toLowerCase())
  );

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
          <div className="flex items-center justify-between mb-4">
            <h1 className="font-display text-3xl font-bold text-gradient flex items-center gap-3">
              <MessageSquare className="w-8 h-8 text-primary" />
              Chat History
            </h1>
            {history.length > 0 && (
              <button
                onClick={clearHistory}
                className="px-4 py-2 glass rounded-lg border border-white/10 hover:bg-destructive/20 transition-colors text-sm flex items-center gap-2"
              >
                <Trash2 className="w-4 h-4" />
                Clear All
              </button>
            )}
          </div>
          
          {history.length > 0 && (
            <div className="relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-muted-foreground" />
              <input
                type="text"
                placeholder="Search chat history..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full pl-10 pr-4 py-3 glass rounded-lg border border-white/10 focus:border-primary focus:outline-none focus:ring-2 focus:ring-primary/20 transition-all"
              />
            </div>
          )}
        </div>

        {filteredHistory.length === 0 ? (
          <div className="flex items-center justify-center py-20">
            <div className="text-center">
              <MessageSquare className="w-16 h-16 text-muted-foreground mx-auto mb-4 opacity-20" />
              <p className="text-muted-foreground mb-2">
                {searchQuery ? "No matching conversations found" : "No chat history yet"}
              </p>
              <p className="text-sm text-muted-foreground">
                {searchQuery ? "Try a different search term" : "Start chatting to build your history!"}
              </p>
            </div>
          </div>
        ) : (
          <div className="space-y-4">
            {filteredHistory.map((item) => (
              <div key={item.id} className="glass p-6 rounded-xl border border-white/10 hover:border-white/20 transition-all group">
                <div className="flex items-start justify-between gap-4 mb-4">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-2">
                      <Calendar className="w-4 h-4 text-muted-foreground" />
                      <span className="text-sm text-muted-foreground">{item.timestamp}</span>
                      {item.intent && (
                        <span className="px-2 py-0.5 text-xs bg-primary/20 text-primary rounded-full">
                          {item.intent}
                        </span>
                      )}
                    </div>
                  </div>
                  <button
                    onClick={() => deleteItem(item.id)}
                    className="p-2 rounded-lg hover:bg-destructive/20 transition-colors opacity-0 group-hover:opacity-100"
                    title="Delete this conversation"
                  >
                    <Trash2 className="w-4 h-4 text-destructive" />
                  </button>
                </div>

                <div className="space-y-3">
                  <div className="flex gap-3">
                    <div className="w-8 h-8 rounded-full gradient-primary flex items-center justify-center flex-shrink-0">
                      <span className="text-sm font-semibold text-white">You</span>
                    </div>
                    <div className="flex-1">
                      <p className="text-foreground">{item.message}</p>
                    </div>
                  </div>

                  <div className="flex gap-3">
                    <div className="w-8 h-8 rounded-full bg-muted flex items-center justify-center flex-shrink-0">
                      <MessageSquare className="w-4 h-4 text-muted-foreground" />
                    </div>
                    <div className="flex-1">
                      <p className="text-muted-foreground">{item.reply}</p>
                      {item.movieCount > 0 && (
                        <p className="text-sm text-primary mt-2">
                          {item.movieCount} movies recommended
                        </p>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </main>
    </div>
  );
};

export default History;
