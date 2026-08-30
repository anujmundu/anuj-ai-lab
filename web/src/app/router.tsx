import { createBrowserRouter } from "react-router-dom";

import AppLayout from "@/components/layout/AppLayout";
import ErrorBoundary from "@/components/layout/ErrorBoundary";

import ChatPage from "@/pages/ChatPage";
import DocumentsPage from "@/pages/DocumentsPage";
import AgentsPage from "@/pages/AgentsPage";
import CollaborationPage from "@/pages/CollaborationPage";
import MemoryPage from "@/pages/MemoryPage";
import PipelinePage from "@/pages/PipelinePage";
import SettingsPage from "@/pages/SettingsPage";
import ToolsPage from "@/pages/ToolsPage";

export const router = createBrowserRouter([
  {
    path: "/",
    element: <AppLayout />,
    errorElement: <ErrorBoundary />,
    children: [
      {
        index: true,
        element: <ChatPage />,
      },
      {
        path: "documents",
        element: <DocumentsPage />,
      },
      {
        path: "agents",
        element: <AgentsPage />,
      },
      {
        path: "collaboration",
        element: <CollaborationPage />,
      },
      {
        path: "memory",
        element: <MemoryPage />,
      },
      {
        path: "tools",
        element: <ToolsPage />,
      },
      {
        path: "pipeline",
        element: <PipelinePage />,
      },
      {
        path: "settings",
        element: <SettingsPage />,
      },
    ],
  },
]);