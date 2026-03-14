import { useState } from "react";
import { LayoutGrid, MessageCircleMore, MessagesSquare, ShieldCheck } from "lucide-react";

import ChatPage from "./pages/ChatPage";
import OverviewPage from "./pages/OverviewPage";
import SystemPage from "./pages/SystemPage";

type ViewId = "overview" | "console" | "system";

const navItems: Array<{
  id: ViewId;
  label: string;
  icon: typeof LayoutGrid;
}> = [
  { id: "overview", label: "Overview", icon: LayoutGrid },
  { id: "console", label: "Operator Console", icon: MessagesSquare },
  { id: "system", label: "System Status", icon: ShieldCheck },
];

export default function App() {
  const [activeView, setActiveView] = useState<ViewId>("overview");

  const content =
    activeView === "overview" ? (
      <OverviewPage />
    ) : activeView === "system" ? (
      <SystemPage />
    ) : (
      <ChatPage />
    );

  return (
    <div className="grid min-h-screen lg:grid-cols-[260px_1fr]">
      <aside className="border-r bg-card">
        <div className="border-b px-6 py-5">
          <div className="flex items-center gap-3">
            <div className="grid size-10 place-items-center rounded-md bg-primary text-primary-foreground">
              <MessageCircleMore size={18} />
            </div>
            <div>
              <h1 className="text-lg font-semibold tracking-[0.08em] uppercase">CommercePilot</h1>
              <p className="text-sm text-muted-foreground">Payments operations assistant</p>
            </div>
          </div>
        </div>

        <nav className="p-4">
          <div className="space-y-1">
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = item.id === activeView;

              return (
                <button
                  key={item.id}
                  type="button"
                  onClick={() => setActiveView(item.id)}
                  className={`flex w-full items-center gap-3 rounded-lg px-4 py-3 text-left text-sm transition ${
                    isActive
                      ? "bg-primary text-primary-foreground"
                      : "text-foreground hover:bg-muted"
                  }`}
                >
                  <Icon className="size-4" />
                  <span>{item.label}</span>
                </button>
              );
            })}
          </div>
        </nav>
      </aside>

      <div className="min-h-screen">
        <header className="border-b bg-background/95">
          <div className="px-6 py-4">
            <p className="text-xs font-semibold tracking-[0.22em] text-muted-foreground uppercase">
              {activeView === "overview"
                ? "Overview"
                : activeView === "system"
                  ? "System Status"
                  : "Operator Console"}
            </p>
          </div>
        </header>
        <main className="px-6 py-6">{content}</main>
      </div>
    </div>
  );
}
