import { useState, useEffect } from "react";
import { Plus, PawPrint, FileText, Heart, BarChart3, PanelLeftClose, LineChart, MessageSquare, RefreshCw } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useNavigate } from "react-router-dom";
import { api } from "@/services/api";

interface LeftSidebarProps {
  onCollapse: () => void;
}

interface ChatSession {
  session_id: string;
  created_at: string;
  updated_at: string;
  message_count: number;
  preview: string;
}

export const LeftSidebar = ({ onCollapse }: LeftSidebarProps) => {
  const navigate = useNavigate();
  const [recentChats, setRecentChats] = useState<ChatSession[]>([]);
  const [loading, setLoading] = useState(false);
  const [isInitialLoad, setIsInitialLoad] = useState(true);

  useEffect(() => {
    fetchRecentChats(true); // Initial load with loading state
    
    // Auto-refresh every 10 seconds
    const interval = setInterval(() => {
      fetchRecentChats(false); // Background refresh without loading state
    }, 10000); // 10 seconds
    
    // Cleanup interval on unmount
    return () => clearInterval(interval);
  }, []);

  const fetchRecentChats = async (showLoading = true) => {
    if (showLoading) {
      setLoading(true);
    }
    try {
      const response = await api.chatHistory.getSessions(8); // Get 8 most recent
      setRecentChats(response.sessions || []);
      if (isInitialLoad) {
        setIsInitialLoad(false);
      }
    } catch (error) {
      console.error("Error fetching recent chats:", error);
      // Silently fail - just show empty list
    } finally {
      if (showLoading) {
        setLoading(false);
      }
    }
  };

  const formatTime = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 1) return "Just now";
    if (diffMins < 60) return `${diffMins} min ago`;
    if (diffHours < 24) return `${diffHours} hour${diffHours > 1 ? 's' : ''} ago`;
    if (diffDays === 1) return "Yesterday";
    if (diffDays < 7) return `${diffDays} days ago`;
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
  };

  return (
    <div className="h-full flex flex-col bg-background overflow-y-auto">
      {/* Header */}
      <div className="border-b border-border bg-primary/5 px-4 py-4 flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <Heart className="h-6 w-6 text-[#6a994e] fill-[#6a994e]" />
          <h2 className="text-lg font-bold text-foreground">RescueAI</h2>
        </div>
        <Button
          variant="ghost"
          size="icon"
          className="h-9 w-9 hover:bg-muted/50"
          title="Close sidebar"
          onClick={onCollapse}
        >
          <PanelLeftClose className="h-5 w-5" />
        </Button>
      </div>

      <div className="p-4">
      {/* New Conversation Button */}
      <Button
        className="w-full mb-3 bg-button hover:bg-button/90 text-button-foreground"
        size="lg"
      >
        <Plus className="h-5 w-5 mr-2" />
        New Conversation
      </Button>

      {/* Navigation Buttons */}
      <div className="space-y-2 mb-6">
        <Button
          variant="outline"
          className="w-full hover:bg-muted/50"
          size="lg"
          onClick={() => navigate("/data-management")}
        >
          <BarChart3 className="h-5 w-5 mr-2" />
          Data Management
        </Button>
        
        <Button
          variant="outline"
          className="w-full hover:bg-muted/50"
          size="lg"
          onClick={() => navigate("/analytics")}
        >
          <LineChart className="h-5 w-5 mr-2" />
          Analytics Dashboard
        </Button>
      </div>

      {/* Recent Conversations */}
      <div className="flex-1">
        <div className="flex items-center justify-between mb-2 px-2">
          <h3 className="text-xs font-semibold text-muted-foreground">
            Recent
          </h3>
          <Button
            variant="ghost"
            size="icon"
            className="h-6 w-6"
            onClick={() => fetchRecentChats(true)}
            disabled={loading}
            title="Refresh"
          >
            <RefreshCw className={`h-3 w-3 ${loading ? 'animate-spin' : ''}`} />
          </Button>
        </div>
        <div className="space-y-1">
          {loading ? (
            <div className="flex items-center justify-center py-8">
              <RefreshCw className="h-5 w-5 animate-spin text-muted-foreground" />
            </div>
          ) : recentChats.length === 0 ? (
            <div className="text-center py-8 px-4">
              <MessageSquare className="h-8 w-8 mx-auto mb-2 text-muted-foreground opacity-50" />
              <p className="text-xs text-muted-foreground">No recent chats</p>
              <p className="text-xs text-muted-foreground mt-1">Start a conversation!</p>
            </div>
          ) : (
            recentChats.map((chat) => (
              <button
                key={chat.session_id}
                className="w-full text-left px-3 py-2 rounded-lg hover:bg-muted/50 cursor-pointer transition-colors group"
                onClick={() => {
                  // TODO: Load this conversation in the chat interface
                  console.log('Load session:', chat.session_id);
                }}
              >
                <p className="text-sm text-foreground truncate mb-1">
                  {chat.preview || 'Conversation'}
                </p>
                <div className="flex items-center gap-2 text-xs text-muted-foreground">
                  <span>{formatTime(chat.updated_at)}</span>
                  <span className="flex items-center">
                    <MessageSquare className="h-3 w-3 mr-1" />
                    {chat.message_count}
                  </span>
                </div>
              </button>
            ))
          )}
        </div>
        </div>
      </div>
    </div>
  );
};
