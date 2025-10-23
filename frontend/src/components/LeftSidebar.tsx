import { Plus, PawPrint, FileText, Heart, BarChart3, PanelLeftClose, LineChart } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useNavigate } from "react-router-dom";

interface LeftSidebarProps {
  onCollapse: () => void;
}

const recentChats = [
  { id: 1, title: "Anxious senior dog matches", time: "2 min ago", dog: "Luna" },
  { id: 2, title: "Translation: Medical records", time: "15 min ago", applicant: "Kim Min-ji" },
  { id: 3, title: "Photo analysis: Health check", time: "1 hour ago", dog: "Max" },
  { id: 4, title: "High-energy dog adopters", time: "2 hours ago", dog: "Zeus" },
  { id: 5, title: "First-time adopter guidance", time: "3 hours ago", applicant: "Sarah Chen" },
  { id: 6, title: "Senior dogs for seniors", time: "Yesterday", dog: "Buddy" },
  { id: 7, title: "Behavior assessment help", time: "Yesterday", dog: "Bella" },
  { id: 8, title: "Application review", time: "2 days ago", applicant: "James Park" },
];

export const LeftSidebar = ({ onCollapse }: LeftSidebarProps) => {
  const navigate = useNavigate();

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
        <h3 className="text-xs font-semibold text-muted-foreground mb-2 px-2">
          Recent
        </h3>
        <div className="space-y-1">
          {recentChats.map((chat) => (
            <button
              key={chat.id}
              className="w-full text-left px-3 py-2 rounded-lg hover:bg-muted/50 cursor-pointer transition-colors group"
            >
              <p className="text-sm text-foreground truncate mb-1">
                {chat.title}
              </p>
              <div className="flex items-center gap-2 text-xs text-muted-foreground">
                <span>{chat.time}</span>
                {chat.dog && (
                  <span className="flex items-center">
                    <PawPrint className="h-3 w-3 mr-1" />
                    {chat.dog}
                  </span>
                )}
                {chat.applicant && (
                  <span className="flex items-center">
                    <FileText className="h-3 w-3 mr-1" />
                    {chat.applicant}
                  </span>
                )}
              </div>
            </button>
          ))}
        </div>
        </div>
      </div>
    </div>
  );
};
