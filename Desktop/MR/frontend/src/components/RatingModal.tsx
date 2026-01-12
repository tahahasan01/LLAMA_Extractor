import { Star, X, Check } from "lucide-react";
import { useState } from "react";

interface RatingModalProps {
  movieTitle: string;
  onClose: () => void;
  onRate: (rating: number) => void;
}

const RatingModal = ({ movieTitle, onClose, onRate }: RatingModalProps) => {
  const [hoveredStar, setHoveredStar] = useState(0);
  const [selectedRating, setSelectedRating] = useState(0);
  const [isSubmitted, setIsSubmitted] = useState(false);
  
  const handleSubmit = () => {
    if (selectedRating > 0) {
      onRate(selectedRating);
      setIsSubmitted(true);
      setTimeout(onClose, 1500);
    }
  };
  
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 animate-fade-in-up" style={{ animationDuration: "0.2s" }}>
      {/* Backdrop */}
      <div 
        className="absolute inset-0 bg-background/80 backdrop-blur-sm"
        onClick={onClose}
      />
      
      {/* Modal */}
      <div className="relative glass-strong rounded-2xl p-6 w-full max-w-sm animate-scale-in">
        {/* Close button */}
        <button
          onClick={onClose}
          className="absolute top-4 right-4 text-muted-foreground hover:text-foreground transition-colors"
        >
          <X className="w-5 h-5" />
        </button>
        
        {isSubmitted ? (
          <div className="text-center py-8">
            <div className="w-16 h-16 gradient-primary rounded-full flex items-center justify-center mx-auto mb-4">
              <Check className="w-8 h-8 text-white" />
            </div>
            <h3 className="font-display text-xl font-semibold mb-2">Thanks!</h3>
            <p className="text-muted-foreground text-sm">Your rating has been saved</p>
          </div>
        ) : (
          <>
            <h3 className="font-display text-xl font-semibold mb-2 pr-8">Rate this movie</h3>
            <p className="text-muted-foreground text-sm mb-6">{movieTitle}</p>
            
            {/* Star Rating */}
            <div className="flex justify-center gap-2 mb-6">
              {[1, 2, 3, 4, 5].map((star) => (
                <button
                  key={star}
                  onMouseEnter={() => setHoveredStar(star)}
                  onMouseLeave={() => setHoveredStar(0)}
                  onClick={() => setSelectedRating(star)}
                  className="transition-transform hover:scale-110"
                >
                  <Star
                    className={`w-10 h-10 transition-colors ${
                      star <= (hoveredStar || selectedRating)
                        ? "fill-gold text-gold"
                        : "text-muted-foreground"
                    }`}
                  />
                </button>
              ))}
            </div>
            
            <p className="text-center text-sm text-muted-foreground mb-6">
              {selectedRating > 0 
                ? ["", "Poor", "Fair", "Good", "Great", "Amazing!"][selectedRating]
                : "Select your rating"}
            </p>
            
            <button
              onClick={handleSubmit}
              disabled={selectedRating === 0}
              className="w-full gradient-primary py-3 rounded-xl font-medium transition-all hover:opacity-90 active:scale-98 disabled:opacity-50"
            >
              Submit Rating
            </button>
          </>
        )}
      </div>
    </div>
  );
};

export default RatingModal;
