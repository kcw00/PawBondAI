import { User, Sparkles } from "lucide-react";

interface Message {
  id: number;
  role: "user" | "assistant";
  content: string;
  timestamp: Date;
  attachedImage?: string;
  attachedDocument?: string;
}

interface MessageBubbleProps {
  message: Message;
}

const formatMarkdown = (text: string) => {
  // Simple markdown formatting
  let formatted = text
    // Bold
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    // Italic
    .replace(/\*(.*?)\*/g, '<em>$1</em>')
    // Code blocks
    .replace(/```(.*?)```/gs, '<pre class="bg-muted p-2 rounded my-2 overflow-x-auto"><code>$1</code></pre>')
    // Inline code
    .replace(/`(.*?)`/g, '<code class="bg-muted px-1 py-0.5 rounded text-sm">$1</code>')
    // Links
    .replace(/\[(.*?)\]\((.*?)\)/g, '<a href="$2" class="text-primary underline" target="_blank">$1</a>');

  // Handle lists
  const lines = formatted.split('\n');
  let inList = false;
  let result: string[] = [];
  
  lines.forEach((line) => {
    if (line.trim().startsWith('•') || line.trim().startsWith('-')) {
      if (!inList) {
        result.push('<ul class="list-disc list-inside my-2 space-y-1">');
        inList = true;
      }
      result.push(`<li class="ml-4">${line.trim().substring(1).trim()}</li>`);
    } else {
      if (inList) {
        result.push('</ul>');
        inList = false;
      }
      result.push(line);
    }
  });
  
  if (inList) {
    result.push('</ul>');
  }
  
  return result.join('\n');
};

export const MessageBubble = ({ message }: MessageBubbleProps) => {
  const isUser = message.role === "user";

  return (
    <div className={`flex justify-start py-6 px-4 ${isUser ? "bg-muted/20" : ""}`}>
      <div className={`flex items-start space-x-4 max-w-3xl w-full`}>
        {/* Avatar */}
        <div
          className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center ${
            isUser ? "bg-chat-user" : "bg-primary"
          }`}
        >
          {isUser ? (
            <User className="h-4 w-4 text-white" />
          ) : (
            <Sparkles className="h-4 w-4 text-primary-foreground" />
          )}
        </div>

        {/* Message Content */}
        <div className="flex-1 space-y-2">
          {message.attachedImage && (
            <div className="rounded-lg overflow-hidden border border-border">
              <img 
                src={message.attachedImage} 
                alt="Uploaded" 
                className="max-w-full h-auto max-h-64 object-cover"
              />
            </div>
          )}
          {message.attachedDocument && (
            <div className="p-2 bg-muted border border-border rounded-lg flex items-center space-x-2 inline-flex">
              <div className="w-8 h-8 bg-primary/20 rounded flex items-center justify-center">
                <span className="text-xs font-bold text-primary">DOC</span>
              </div>
              <span className="text-xs text-foreground">Medical document attached</span>
            </div>
          )}
          <div 
            className="prose prose-sm max-w-none text-foreground leading-relaxed"
            dangerouslySetInnerHTML={{ __html: formatMarkdown(message.content) }}
          />
        </div>
      </div>
    </div>
  );
};
