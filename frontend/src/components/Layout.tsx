import { useState } from "react";
import { ChevronRight, Brain } from "lucide-react";
import { Button } from "@/components/ui/button";
import { LeftSidebar } from "./LeftSidebar";
import { ChatInterface } from "./ChatInterface";
import { AITraceDrawer } from "./AITraceDrawer";
import { useSearch } from "@/contexts/SearchContext";
import { Badge } from "@/components/ui/badge";

export const Layout = () => {
  const [leftCollapsed, setLeftCollapsed] = useState(false);
  const { showTrace, setShowTrace, searchType, currentQuery, traceData } = useSearch();

  return (
    <div className="flex flex-col h-screen bg-background overflow-hidden">
      <div className="flex flex-1 overflow-hidden">
        {/* Left Sidebar - Stats & History */}
        <div
          className={`transition-all duration-300 border-r border-border flex-shrink-0 ${leftCollapsed ? "w-0" : "w-80"
            }`}
        >
          {!leftCollapsed && <LeftSidebar onCollapse={() => setLeftCollapsed(true)} />}
        </div>

        {/* Left Open Sidebar Button - Top Left Corner */}
        {leftCollapsed && (
          <Button
            variant="ghost"
            size="icon"
            onClick={() => setLeftCollapsed(false)}
            className="absolute top-4 left-4 z-10 h-10 w-10 rounded-lg bg-background hover:bg-muted/50 border border-border shadow-sm"
            title="Show sidebar"
          >
            <ChevronRight className="h-5 w-5" />
          </Button>
        )}

        {/* Center Panel - Chat Interface */}
        <div className="flex-1 flex flex-col min-w-0">
          <ChatInterface />
        </div>

        {/* AI Trace Button - Bottom Right */}
        <Button
          onClick={() => setShowTrace(true)}
          className="fixed bottom-6 right-6 rounded-full shadow-lg h-10 px-4 gap-2 z-10"
          title="View AI Trace"
        >
          <Brain className="h-4 w-4" />
          <span className="text-sm font-medium">AI Trace</span>
          {traceData && (
            <Badge variant="secondary" className="ml-1 h-5 px-1.5 text-xs">
              {traceData.steps.length}
            </Badge>
          )}
        </Button>

        {/* AI Trace Drawer */}
        <AITraceDrawer
          open={showTrace}
          onOpenChange={setShowTrace}
          traceData={traceData}
        />
      </div>
    </div>
  );
};