import { Bot, User } from "lucide-react";

interface ChatMessageProps {
  message: string;
  isBot: boolean;
  timestamp: string;
  index: number;
}

const ChatMessage = ({ message, isBot, timestamp, index }: ChatMessageProps) => {
  return (
    <div
      className={`flex gap-3 ${isBot ? "justify-start" : "justify-end"} opacity-0 ${
        isBot ? "animate-slide-in-left" : "animate-slide-in-right"
      }`}
      style={{ animationDelay: `${index * 0.1}s`, animationFillMode: "forwards" }}
    >
      {isBot && (
        <div className="flex-shrink-0 w-10 h-10 gradient-primary rounded-full flex items-center justify-center shadow-lg">
          <Bot className="w-5 h-5 text-white" />
        </div>
      )}
      
      <div className={`max-w-[75%] ${isBot ? "" : "order-first"}`}>
        <div
          className={`px-4 py-3 rounded-2xl ${
            isBot
              ? "glass rounded-tl-sm"
              : "gradient-primary rounded-tr-sm"
          }`}
        >
          <p className="text-sm leading-relaxed">{message}</p>
        </div>
        <span className={`text-xs text-muted-foreground mt-1 block ${isBot ? "" : "text-right"}`}>
          {timestamp}
        </span>
      </div>
      
      {!isBot && (
        <div className="flex-shrink-0 w-10 h-10 bg-accent rounded-full flex items-center justify-center shadow-lg">
          <User className="w-5 h-5 text-white" />
        </div>
      )}
    </div>
  );
};

export default ChatMessage;
