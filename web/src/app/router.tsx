import { createBrowserRouter } from "react-router-dom";

import AppLayout from "@/components/layout/AppLayout";

import ChatPage from "@/pages/ChatPage";
import DocumentsPage from "@/pages/DocumentsPage";
import MemoryPage from "@/pages/MemoryPage";
import PipelinePage from "@/pages/PipelinePage";
import SettingsPage from "@/pages/SettingsPage";
import ToolsPage from "@/pages/ToolsPage";

export const router = createBrowserRouter([
  {
    path: "/",
    element: <AppLayout />,
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