import { Cpu, Moon, Settings } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";

export function Header() {
  return (
    <header className="flex h-16 items-center justify-between border-b border-slate-200 bg-white px-6 dark:border-slate-800 dark:bg-slate-950">
      <div className="flex items-center gap-3">
        <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-slate-900 text-white dark:bg-white dark:text-slate-900">
          <Cpu className="h-5 w-5" />
        </div>

        <div>
          <h1 className="text-lg font-semibold text-slate-900 dark:text-white">
            Anuj AI Lab
          </h1>

          <p className="text-sm text-slate-500">
            Local AI Engineering Platform
          </p>
        </div>
      </div>

      <div className="flex items-center gap-3">
        <Badge variant="secondary">
          Backend Offline
        </Badge>

        <Badge variant="outline">
          v2.0.0
        </Badge>

        <Button
          variant="ghost"
          size="icon"
        >
          <Moon className="h-4 w-4" />
        </Button>

        <Button
          variant="ghost"
          size="icon"
        >
          <Settings className="h-4 w-4" />
        </Button>
      </div>
    </header>
  );
}