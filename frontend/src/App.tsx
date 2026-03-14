import { MessageCircleMore } from "lucide-react";

import ChatPage from "./pages/ChatPage";

export default function App() {
  return (
    <div className="min-h-screen">
      <header className="sticky top-0 z-10 border-b bg-background/80 backdrop-blur">
        <div className="mx-auto flex max-w-6xl items-center gap-3 px-5 py-4">
          <div className="grid size-10 place-items-center rounded-2xl bg-primary text-primary-foreground shadow-lg shadow-primary/25">
            <MessageCircleMore size={18} />
          </div>
          <div>
            <h1 className="text-lg font-semibold">CommercePilot</h1>
            <p className="text-sm text-muted-foreground">Conversational payments agent</p>
          </div>
        </div>
      </header>
      <main className="mx-auto max-w-6xl px-5 py-6">
        <ChatPage />
      </main>
    </div>
  );
}
