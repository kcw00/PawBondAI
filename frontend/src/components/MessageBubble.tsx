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
  // First, handle lists line by line (before inline formatting)
  const lines = text.split('\n');
  let inUnorderedList = false;
  let inOrderedList = false;
  let processedLines: string[] = [];

  lines.forEach((line) => {
    const trimmed = line.trim();

    // Check for unordered list items (*, -, •)
    if (trimmed.match(/^[\*\-•]\s/)) {
      if (!inUnorderedList) {
        if (inOrderedList) {
          processedLines.push('</ol>');
          inOrderedList = false;
        }
        processedLines.push('<ul class="list-disc list-inside my-2 space-y-1">');
        inUnorderedList = true;
      }
      // Remove the bullet marker and add list item
      const content = trimmed.substring(1).trim();
      processedLines.push(`<li class="ml-4">${content}</li>`);
    }
    // Check for ordered list items (1., 2., etc.)
    else if (trimmed.match(/^\d+\.\s/)) {
      if (!inOrderedList) {
        if (inUnorderedList) {
          processedLines.push('</ul>');
          inUnorderedList = false;
        }
        processedLines.push('<ol class="list-decimal list-inside my-2 space-y-1">');
        inOrderedList = true;
      }
      // Remove the number marker and add list item
      const content = trimmed.replace(/^\d+\.\s/, '');
      processedLines.push(`<li class="ml-4">${content}</li>`);
    }
    // Regular line
    else {
      if (inUnorderedList) {
        processedLines.push('</ul>');
        inUnorderedList = false;
      }
      if (inOrderedList) {
        processedLines.push('</ol>');
        inOrderedList = false;
      }
      processedLines.push(line);
    }
  });

  // Close any open lists
  if (inUnorderedList) {
    processedLines.push('</ul>');
  }
  if (inOrderedList) {
    processedLines.push('</ol>');
  }

  // Join lines back together
  let formatted = processedLines.join('\n');

  // Now apply inline markdown formatting
  formatted = formatted
    // Code blocks (do this first to avoid processing their content)
    .replace(/```(.*?)```/gs, '<pre class="bg-muted p-2 rounded my-2 overflow-x-auto"><code>$1</code></pre>')
    // Inline code
    .replace(/`(.*?)`/g, '<code class="bg-muted px-1 py-0.5 rounded text-sm">$1</code>')
    // Headers (must be at start of line)
    .replace(/^### (.*$)/gm, '<h3 class="text-lg font-semibold mt-3 mb-0">$1</h3>')
    .replace(/^## (.*$)/gm, '<h2 class="text-xl font-bold mt-4 mb-0">$1</h2>')
    .replace(/^# (.*$)/gm, '<h1 class="text-2xl font-bold mt-5 mb-4">$1</h1>')
    // Bold (must come before italic)
    .replace(/\*\*(.*?)\*\*/g, '<strong class="font-semibold">$1</strong>')
    // Italic (now only matches single asterisks that aren't at line start)
    .replace(/\*([^\*\n]+?)\*/g, '<em>$1</em>')
    // Links
    .replace(/\[(.*?)\]\((.*?)\)/g, '<a href="$2" class="text-primary underline" target="_blank">$1</a>')
    // Line breaks (convert double line breaks to paragraphs)
    .replace(/\n\n/g, '<br/><br/>')
    // Remove extra breaks after headings
    .replace(/(<\/h[123]>)\s*<br\/>\s*<br\/>/g, '$1<br/>')
    .replace(/(<\/h[123]>)\s*<br\/>/g, '$1')
    // Remove extra breaks after lists (but keep one break before next heading)
    .replace(/(<\/ul>)\s*<br\/>\s*<br\/>\s*(?=<h[123])/g, '$1<br/>')
    .replace(/(<\/ul>)\s*<br\/>\s*<br\/>/g, '$1')
    .replace(/(<\/ul>)\s*<br\/>\s*(?!<h[123])/g, '$1')
    .replace(/(<\/ol>)\s*<br\/>\s*<br\/>\s*(?=<h[123])/g, '$1<br/>')
    .replace(/(<\/ol>)\s*<br\/>\s*<br\/>/g, '$1')
    .replace(/(<\/ol>)\s*<br\/>\s*(?!<h[123])/g, '$1');

  return formatted;
};

export const MessageBubble = ({ message }: MessageBubbleProps) => {
  const isUser = message.role === "user";

  return (
    <div className={`flex justify-start py-6 px-4 ${isUser ? "bg-muted/20" : ""}`}>
      <div className={`flex items-start space-x-4 max-w-3xl w-full`}>
        {/* Avatar */}
        <div
          className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center ${isUser ? "bg-chat-user" : "bg-primary"
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
