import { useState, useEffect } from "react";
import { Plus, PawPrint, FileText, Heart, BarChart3, PanelLeftClose, MessageSquare, RefreshCw, Pencil, Trash2, Check, X } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useNavigate } from "react-router-dom";
import { api } from "@/services/api";
import { useSearch } from "@/contexts/SearchContext";
import { toast } from "sonner";
import { DeleteChatModal } from "@/components/DeleteChatModal";

interface LeftSidebarProps {
  onCollapse: () => void;
}

interface ChatSession {
  session_id: string;
  created_at: string;
  updated_at: string;
  message_count: number;
  preview: string;
  name?: string;
}

export const LeftSidebar = ({ onCollapse }: LeftSidebarProps) => {
  const navigate = useNavigate();
  const { setLoadedSessionId, setLoadedMessages } = useSearch();
  const [recentChats, setRecentChats] = useState<ChatSession[]>([]);
  const [loading, setLoading] = useState(false);
  const [isInitialLoad, setIsInitialLoad] = useState(true);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [editingName, setEditingName] = useState("");
  const [deleteModalOpen, setDeleteModalOpen] = useState(false);
  const [chatToDelete, setChatToDelete] = useState<ChatSession | null>(null);

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

  const handleLoadSession = async (sessionId: string) => {
    try {
      const response = await api.chatHistory.getSession(sessionId);
      setLoadedMessages(response.messages || []);
      setLoadedSessionId(sessionId);
      toast.success("Conversation loaded");
    } catch (error) {
      console.error("Error loading session:", error);
      toast.error("Failed to load conversation");
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

  const handleStartEdit = (chat: ChatSession) => {
    setEditingId(chat.session_id);
    setEditingName(chat.name || chat.preview || 'Conversation');
  };

  const handleSaveEdit = async (sessionId: string) => {
    if (!editingName.trim()) {
      toast.error("Chat name cannot be empty");
      return;
    }

    try {
      await api.chatHistory.updateChatName(sessionId, editingName.trim());
      toast.success("Chat name updated");
      setEditingId(null);
      fetchRecentChats(false);
    } catch (error) {
      console.error("Error updating chat name:", error);
      toast.error("Failed to update chat name");
    }
  };

  const handleCancelEdit = () => {
    setEditingId(null);
    setEditingName("");
  };

  const handleDeleteClick = (chat: ChatSession) => {
    setChatToDelete(chat);
    setDeleteModalOpen(true);
  };

  const handleDeleteConfirm = async () => {
    if (!chatToDelete) return;

    try {
      await api.chatHistory.deleteSession(chatToDelete.session_id);
      toast.success("Conversation deleted");
      fetchRecentChats(false);
      setDeleteModalOpen(false);
      setChatToDelete(null);
    } catch (error) {
      console.error("Error deleting session:", error);
      toast.error("Failed to delete conversation");
    }
  };

  return (
    <div className="h-full flex flex-col bg-background overflow-y-auto custom-scrollbar">
      {/* Header */}
      <div className="border-b border-border bg-primary/5 px-4 py-4 flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <Heart className="h-6 w-6 text-[#6a994e] fill-[#6a994e]" />
          <h2 className="text-lg font-bold text-foreground">PawBondAI</h2>
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
        onClick={() => {
          setLoadedSessionId(null);
          setLoadedMessages([]);
          window.location.reload();
        }}
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
              <div
                key={chat.session_id}
                className="w-full px-3 py-2 rounded-lg hover:bg-muted/50 transition-colors group relative"
              >
                {editingId === chat.session_id ? (
                  <div className="flex items-center gap-2">
                    <input
                      type="text"
                      value={editingName}
                      onChange={(e) => setEditingName(e.target.value)}
                      className="flex-1 px-2 py-1 text-sm bg-background border border-border rounded focus:outline-none focus:ring-2 focus:ring-primary"
                      autoFocus
                      onKeyDown={(e) => {
                        if (e.key === 'Enter') handleSaveEdit(chat.session_id);
                        if (e.key === 'Escape') handleCancelEdit();
                      }}
                    />
                    <Button
                      variant="ghost"
                      size="icon"
                      className="h-6 w-6"
                      onClick={() => handleSaveEdit(chat.session_id)}
                    >
                      <Check className="h-3 w-3 text-green-600" />
                    </Button>
                    <Button
                      variant="ghost"
                      size="icon"
                      className="h-6 w-6"
                      onClick={handleCancelEdit}
                    >
                      <X className="h-3 w-3 text-red-600" />
                    </Button>
                  </div>
                ) : (
                  <div className="flex items-start gap-2">
                    <button
                      className="flex-1 text-left min-w-0"
                      onClick={() => handleLoadSession(chat.session_id)}
                    >
                      <p className="text-sm text-foreground mb-1 break-words line-clamp-2">
                        {chat.name || chat.preview || 'Conversation'}
                      </p>
                      <div className="flex items-center gap-2 text-xs text-muted-foreground">
                        <span>{formatTime(chat.updated_at)}</span>
                        <span className="flex items-center">
                          <MessageSquare className="h-3 w-3 mr-1" />
                          {chat.message_count}
                        </span>
                      </div>
                    </button>
                    <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity flex-shrink-0">
                      <Button
                        variant="ghost"
                        size="icon"
                        className="h-6 w-6"
                        onClick={(e) => {
                          e.stopPropagation();
                          handleStartEdit(chat);
                        }}
                        title="Edit name"
                      >
                        <Pencil className="h-3 w-3" />
                      </Button>
                      <Button
                        variant="ghost"
                        size="icon"
                        className="h-6 w-6 hover:text-red-600"
                        onClick={(e) => {
                          e.stopPropagation();
                          handleDeleteClick(chat);
                        }}
                        title="Delete"
                      >
                        <Trash2 className="h-3 w-3" />
                      </Button>
                    </div>
                  </div>
                )}
              </div>
            ))
          )}
        </div>
        </div>
      </div>

      {/* Delete Confirmation Modal */}
      <DeleteChatModal
        open={deleteModalOpen}
        onOpenChange={setDeleteModalOpen}
        onConfirm={handleDeleteConfirm}
        chatName={chatToDelete?.name || chatToDelete?.preview}
      />
    </div>
  );
};
