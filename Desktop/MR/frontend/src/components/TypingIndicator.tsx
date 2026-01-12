import { Bot } from "lucide-react";

const TypingIndicator = () => {
  return (
    <div className="flex gap-3 justify-start animate-fade-in-up">
      <div className="flex-shrink-0 w-10 h-10 gradient-primary rounded-full flex items-center justify-center shadow-lg">
        <Bot className="w-5 h-5 text-white" />
      </div>
      
      <div className="glass px-5 py-4 rounded-2xl rounded-tl-sm">
        <div className="flex gap-1.5">
          <span className="w-2 h-2 bg-primary rounded-full typing-dot" />
          <span className="w-2 h-2 bg-primary rounded-full typing-dot" />
          <span className="w-2 h-2 bg-primary rounded-full typing-dot" />
        </div>
      </div>
    </div>
  );
};

export default TypingIndicator;
