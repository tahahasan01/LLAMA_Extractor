import { LucideIcon } from "lucide-react";

interface QuickSuggestionProps {
  label: string;
  icon: LucideIcon;
  onClick: () => void;
  index: number;
}

const QuickSuggestion = ({ label, icon: Icon, onClick, index }: QuickSuggestionProps) => {
  return (
    <button
      onClick={onClick}
      className="glass px-4 py-2 rounded-full flex items-center gap-2 text-sm text-muted-foreground hover:text-foreground hover:bg-primary/20 hover:border-primary/30 transition-all duration-200 hover:scale-105 active:scale-95 opacity-0 animate-fade-in-up"
      style={{ animationDelay: `${0.6 + index * 0.1}s`, animationFillMode: "forwards" }}
    >
      <Icon className="w-4 h-4" />
      {label}
    </button>
  );
};

export default QuickSuggestion;
