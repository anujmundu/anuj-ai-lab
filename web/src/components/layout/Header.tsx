import { useState } from "react";

import {
    Cpu,
    Menu,
    Moon,
    Settings,
    Sun,
} from "lucide-react";

import { useTheme } from "next-themes";
import { useNavigate } from "react-router-dom";

import { useHealth } from "@/hooks/system/useHealth";

import { MobileSidebar } from "@/components/navigation/MobileSidebar";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";

export function Header() {
    const navigate = useNavigate();

    const [mobileMenuOpen, setMobileMenuOpen] =
        useState(false);

    const {
        resolvedTheme,
        setTheme,
    } = useTheme();

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
        <>
            <header className="flex h-16 items-center justify-between border-b border-slate-200 bg-white px-4 lg:px-6 dark:border-slate-800 dark:bg-slate-950">
                <div className="flex items-center gap-3">
                    <Button
                        variant="ghost"
                        size="icon"
                        className="lg:hidden"
                        onClick={() =>
                            setMobileMenuOpen(true)
                        }
                        aria-label="Open navigation"
                    >
                        <Menu className="h-5 w-5" />
                    </Button>

                    <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-slate-900 text-white dark:bg-white dark:text-slate-900">
                        <Cpu className="h-5 w-5" />
                    </div>

                    <div>
                        <h1 className="text-lg font-semibold">
                            Anuj AI Lab
                        </h1>

                        <p className="hidden text-sm text-muted-foreground sm:block">
                            Local AI Engineering Platform
                        </p>
                    </div>
                </div>

                <div className="flex items-center gap-2 lg:gap-3">
                    <div className="hidden md:flex items-center gap-2">
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
                            {data?.version ??
                                "1.2.0"}
                        </Badge>
                    </div>

                    <Button
                        variant="ghost"
                        size="icon"
                        onClick={toggleTheme}
                        aria-label="Toggle theme"
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
                        aria-label="Open settings"
                    >
                        <Settings className="h-4 w-4" />
                    </Button>
                </div>
            </header>

            <MobileSidebar
                open={mobileMenuOpen}
                onOpenChange={
                    setMobileMenuOpen
                }
            />
        </>
    );
}

export default Header;