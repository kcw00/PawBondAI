// Mock data removed - this page was for testing component display only
// Components are now tested in the main chat interface with real API data

export default function CardShowcase() {
  return (
    <div className="min-h-screen bg-background p-8 flex items-center justify-center">
      <div className="max-w-2xl mx-auto text-center">
        <h1 className="text-4xl font-bold mb-4 text-foreground">Card Components Showcase</h1>
        <p className="text-muted-foreground mb-8">
          This page previously displayed card components with mock data.
          All components are now integrated into the main chat interface and use real API data.
        </p>
        <a href="/" className="text-primary hover:underline">
          ← Go to Main Chat Interface
        </a>
      </div>
    </div>
  );
}
