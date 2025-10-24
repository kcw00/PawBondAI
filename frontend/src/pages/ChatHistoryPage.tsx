import { useState, useEffect } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Input } from "@/components/ui/input";
import {
  ArrowLeft,
  MessageSquare,
  Trash2,
  Search,
  Calendar,
  User,
  Bot,
  RefreshCw,
  Pencil,
  Check,
  X
} from "lucide-react";
import { toast } from "sonner";
import { api } from "@/services/api";
import { DeleteChatModal } from "@/components/DeleteChatModal";

interface ChatSession {
  session_id: string;
  created_at: string;
  updated_at: string;
  message_count: number;
  preview: string;
  name?: string;
}

interface ChatMessage {
  role: "user" | "assistant";
  content: string;
  intent?: string;
  timestamp: string;
  metadata?: any;
}

export default function ChatHistoryPage() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const [sessions, setSessions] = useState<ChatSession[]>([]);
  const [selectedSession, setSelectedSession] = useState<string | null>(null);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [searchQuery, setSearchQuery] = useState("");
  const [loading, setLoading] = useState(false);
  const [loadingMessages, setLoadingMessages] = useState(false);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [editingName, setEditingName] = useState("");
  const [deleteModalOpen, setDeleteModalOpen] = useState(false);
  const [sessionToDelete, setSessionToDelete] = useState<ChatSession | null>(null);

  useEffect(() => {
    fetchSessions();
    
    // Check if there's a session parameter in the URL
    const sessionParam = searchParams.get('session');
    if (sessionParam) {
      fetchSessionMessages(sessionParam);
    }
  }, []);

  const fetchSessions = async () => {
    setLoading(true);
    try {
      const response = await api.chatHistory.getSessions(50);
      setSessions(response.sessions || []);
    } catch (error) {
      console.error("Error fetching sessions:", error);
      toast.error("Failed to load chat sessions");
    } finally {
      setLoading(false);
    }
  };

  const fetchSessionMessages = async (sessionId: string) => {
    setLoadingMessages(true);
    try {
      const response = await api.chatHistory.getSession(sessionId);
      setMessages(response.messages || []);
      setSelectedSession(sessionId);
    } catch (error) {
      console.error("Error fetching messages:", error);
      toast.error("Failed to load chat messages");
    } finally {
      setLoadingMessages(false);
    }
  };

  const handleDeleteClick = (session: ChatSession, e: React.MouseEvent) => {
    e.stopPropagation();
    setSessionToDelete(session);
    setDeleteModalOpen(true);
  };

  const handleDeleteConfirm = async () => {
    if (!sessionToDelete) return;

    try {
      await api.chatHistory.deleteSession(sessionToDelete.session_id);
      toast.success("Chat session deleted");

      // Remove from list
      setSessions(sessions.filter(s => s.session_id !== sessionToDelete.session_id));

      // Clear selected if it was deleted
      if (selectedSession === sessionToDelete.session_id) {
        setSelectedSession(null);
        setMessages([]);
      }

      setDeleteModalOpen(false);
      setSessionToDelete(null);
    } catch (error) {
      console.error("Error deleting session:", error);
      toast.error("Failed to delete session");
    }
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 1) return "Just now";
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    if (diffDays < 7) return `${diffDays}d ago`;

    return date.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: date.getFullYear() !== now.getFullYear() ? 'numeric' : undefined
    });
  };

  const handleStartEdit = (session: ChatSession) => {
    setEditingId(session.session_id);
    setEditingName(session.name || session.preview || 'Conversation');
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
      // Update the local state
      setSessions(sessions.map(s =>
        s.session_id === sessionId ? { ...s, name: editingName.trim() } : s
      ));
    } catch (error) {
      console.error("Error updating chat name:", error);
      toast.error("Failed to update chat name");
    }
  };

  const handleCancelEdit = () => {
    setEditingId(null);
    setEditingName("");
  };

  const filteredSessions = sessions.filter(session =>
    (session.name?.toLowerCase().includes(searchQuery.toLowerCase())) ||
    session.preview.toLowerCase().includes(searchQuery.toLowerCase()) ||
    session.session_id.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="min-h-screen bg-background p-6">
      {/* Header */}
      <div className="max-w-7xl mx-auto mb-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <Button
              variant="ghost"
              size="icon"
              onClick={() => navigate("/")}
            >
              <ArrowLeft className="h-5 w-5" />
            </Button>
            <div>
              <h1 className="text-3xl font-bold text-foreground flex items-center gap-2">
                <MessageSquare className="h-8 w-8 text-primary" />
                Chat History
              </h1>
              <p className="text-muted-foreground mt-1">
                View and manage your conversation history
              </p>
            </div>
          </div>
          <Button
            variant="outline"
            size="sm"
            onClick={fetchSessions}
            disabled={loading}
          >
            <RefreshCw className={`h-4 w-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
            Refresh
          </Button>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Sessions List */}
        <Card className="lg:col-span-1 p-4">
          <div className="mb-4">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Search conversations..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-10"
              />
            </div>
          </div>

          <ScrollArea className="h-[calc(100vh-280px)] custom-scrollbar">
            {loading ? (
              <div className="flex items-center justify-center py-8">
                <RefreshCw className="h-6 w-6 animate-spin text-muted-foreground" />
              </div>
            ) : filteredSessions.length === 0 ? (
              <div className="text-center py-8 text-muted-foreground">
                <MessageSquare className="h-12 w-12 mx-auto mb-2 opacity-50" />
                <p className="text-sm">No chat sessions found</p>
              </div>
            ) : (
              <div className="space-y-2">
                {filteredSessions.map((session) => (
                  <div
                    key={session.session_id}
                    className={`p-3 rounded-lg border transition-all ${
                      selectedSession === session.session_id
                        ? 'bg-primary/10 border-primary'
                        : 'bg-card border-border hover:bg-muted/50'
                    }`}
                  >
                    {editingId === session.session_id ? (
                      <div className="space-y-2">
                        <input
                          type="text"
                          value={editingName}
                          onChange={(e) => setEditingName(e.target.value)}
                          className="w-full px-2 py-1 text-sm bg-background border border-border rounded focus:outline-none focus:ring-2 focus:ring-primary"
                          autoFocus
                          onKeyDown={(e) => {
                            if (e.key === 'Enter') handleSaveEdit(session.session_id);
                            if (e.key === 'Escape') handleCancelEdit();
                          }}
                        />
                        <div className="flex items-center gap-2">
                          <Button
                            variant="outline"
                            size="sm"
                            className="flex-1"
                            onClick={() => handleSaveEdit(session.session_id)}
                          >
                            <Check className="h-3 w-3 mr-1 text-green-600" />
                            Save
                          </Button>
                          <Button
                            variant="outline"
                            size="sm"
                            className="flex-1"
                            onClick={handleCancelEdit}
                          >
                            <X className="h-3 w-3 mr-1 text-red-600" />
                            Cancel
                          </Button>
                        </div>
                      </div>
                    ) : (
                      <>
                        <div className="flex items-start justify-between mb-2">
                          <div className="flex items-center gap-2">
                            <Calendar className="h-3 w-3 text-muted-foreground" />
                            <span className="text-xs text-muted-foreground">
                              {formatDate(session.updated_at)}
                            </span>
                          </div>
                          <div className="flex items-center gap-1">
                            <Button
                              variant="ghost"
                              size="icon"
                              className="h-6 w-6"
                              onClick={(e) => {
                                e.stopPropagation();
                                handleStartEdit(session);
                              }}
                              title="Edit name"
                            >
                              <Pencil className="h-3 w-3" />
                            </Button>
                            <Button
                              variant="ghost"
                              size="icon"
                              className="h-6 w-6"
                              onClick={(e) => handleDeleteClick(session, e)}
                              title="Delete"
                            >
                              <Trash2 className="h-3 w-3 text-destructive" />
                            </Button>
                          </div>
                        </div>
                        <div
                          className="cursor-pointer"
                          onClick={() => fetchSessionMessages(session.session_id)}
                        >
                          <p className="text-sm text-foreground line-clamp-2 mb-2 font-medium">
                            {session.name || session.preview}
                          </p>
                          {session.name && (
                            <p className="text-xs text-muted-foreground line-clamp-1 mb-2">
                              {session.preview}
                            </p>
                          )}
                          <div className="flex items-center gap-2">
                            <Badge variant="secondary" className="text-xs">
                              {session.message_count} messages
                            </Badge>
                          </div>
                        </div>
                      </>
                    )}
                  </div>
                ))}
              </div>
            )}
          </ScrollArea>
        </Card>

        {/* Messages View */}
        <Card className="lg:col-span-2 p-6">
          {selectedSession ? (
            <>
              <div className="mb-4 pb-4 border-b border-border">
                <h2 className="text-lg font-semibold text-foreground">Conversation</h2>
                <p className="text-xs text-muted-foreground mt-1">
                  Session ID: {selectedSession}
                </p>
              </div>

              <ScrollArea className="h-[calc(100vh-320px)] custom-scrollbar">
                {loadingMessages ? (
                  <div className="flex items-center justify-center py-8">
                    <RefreshCw className="h-6 w-6 animate-spin text-muted-foreground" />
                  </div>
                ) : (
                  <div className="space-y-4">
                    {messages.map((message, index) => (
                      <div
                        key={index}
                        className={`flex gap-3 ${
                          message.role === 'user' ? 'justify-end' : 'justify-start'
                        }`}
                      >
                        {message.role === 'assistant' && (
                          <div className="flex-shrink-0">
                            <div className="h-8 w-8 rounded-full bg-primary/10 flex items-center justify-center">
                              <Bot className="h-4 w-4 text-primary" />
                            </div>
                          </div>
                        )}
                        
                        <div
                          className={`max-w-[80%] rounded-lg p-4 ${
                            message.role === 'user'
                              ? 'bg-primary text-primary-foreground'
                              : 'bg-muted text-foreground'
                          }`}
                        >
                          <p className="text-sm whitespace-pre-wrap">{message.content}</p>
                          <div className="flex items-center gap-2 mt-2">
                            <span className="text-xs opacity-70">
                              {new Date(message.timestamp).toLocaleTimeString('en-US', {
                                hour: 'numeric',
                                minute: '2-digit',
                              })}
                            </span>
                            {message.intent && (
                              <Badge variant="outline" className="text-xs">
                                {message.intent}
                              </Badge>
                            )}
                          </div>
                        </div>

                        {message.role === 'user' && (
                          <div className="flex-shrink-0">
                            <div className="h-8 w-8 rounded-full bg-secondary flex items-center justify-center">
                              <User className="h-4 w-4 text-secondary-foreground" />
                            </div>
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                )}
              </ScrollArea>
            </>
          ) : (
            <div className="flex flex-col items-center justify-center h-[calc(100vh-320px)] text-muted-foreground">
              <MessageSquare className="h-16 w-16 mb-4 opacity-50" />
              <p className="text-lg font-medium">Select a conversation</p>
              <p className="text-sm">Choose a chat session from the list to view messages</p>
            </div>
          )}
        </Card>
      </div>

      {/* Delete Confirmation Modal */}
      <DeleteChatModal
        open={deleteModalOpen}
        onOpenChange={setDeleteModalOpen}
        onConfirm={handleDeleteConfirm}
        chatName={sessionToDelete?.name || sessionToDelete?.preview}
      />
    </div>
  );
}
