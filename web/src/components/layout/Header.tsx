import {
    Cpu,
    Moon,
    Settings,
    Sun,
} from "lucide-react";

import { useNavigate } from "react-router-dom";

import { useTheme } from "next-themes";

import { useHealth } from "@/hooks/system/useHealth";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";

export function Header() {
    const navigate = useNavigate();

    const { resolvedTheme, setTheme } =
        useTheme();

    const {
        data,
        isError,
    } = useHealth();

    const backendOnline =
        !isError &&
        data?.status === "running";

    function toggleTheme() {
        setTheme(
            resolvedTheme === "dark"
                ? "light"
                : "dark",
        );
    }

    return (
        <header className="flex h-16 items-center justify-between border-b border-slate-200 bg-white px-6 dark:border-slate-800 dark:bg-slate-950">
            <div className="flex items-center gap-3">
                <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-slate-900 text-white dark:bg-white dark:text-slate-900">
                    <Cpu className="h-5 w-5" />
                </div>

                <div>
                    <h1 className="text-lg font-semibold">
                        Anuj AI Lab
                    </h1>

                    <p className="text-sm text-muted-foreground">
                        Local AI Engineering Platform
                    </p>
                </div>
            </div>

            <div className="flex items-center gap-3">
                <Badge
                    variant={
                        backendOnline
                            ? "default"
                            : "destructive"
                    }
                >
                    Backend{" "}
                    {backendOnline
                        ? "Online"
                        : "Offline"}
                </Badge>

                <Badge variant="outline">
                    {data?.version ?? "1.2.0"}
                </Badge>

                <Button
                    variant="ghost"
                    size="icon"
                    onClick={toggleTheme}
                    title="Toggle theme"
                >
                    {resolvedTheme === "dark" ? (
                        <Sun className="h-4 w-4" />
                    ) : (
                        <Moon className="h-4 w-4" />
                    )}
                </Button>

                <Button
                    variant="ghost"
                    size="icon"
                    onClick={() =>
                        navigate("/settings")
                    }
                    title="Settings"
                >
                    <Settings className="h-4 w-4" />
                </Button>
            </div>
        </header>
    );
}