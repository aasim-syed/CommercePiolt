import { MessageCircleMore } from "lucide-react";

import { ChatPage } from "./pages/ChatPage";

export default function App() {
  return (
    <div className="app-shell">
      <header className="topbar">
        <div className="brand">
          <div className="brand-icon">
            <MessageCircleMore size={18} />
          </div>
          <div>
            <h1>CommercePilot</h1>
            <p>Conversational payments agent</p>
          </div>
        </div>
      </header>
      <main className="main-content">
        <ChatPage />
      </main>
    </div>
  );
}
