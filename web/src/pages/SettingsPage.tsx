import { useTheme } from "next-themes";

import { useHealth } from "@/hooks/system/useHealth";

import { Badge } from "@/components/ui/badge";
import {
    Card,
    CardContent,
    CardDescription,
    CardHeader,
    CardTitle,
} from "@/components/ui/card";
import { Separator } from "@/components/ui/separator";

export default function SettingsPage() {
    const {
        resolvedTheme,
        theme,
    } = useTheme();

    const {
        data,
        isError,
    } = useHealth();

    const backendOnline =
        !isError &&
        data?.status === "running";

    return (
        <section className="flex flex-1 flex-col gap-6 p-6">
            <div>
                <h1 className="text-3xl font-bold tracking-tight">
                    Settings
                </h1>

                <p className="mt-2 text-muted-foreground">
                    Configure your local AI engineering
                    platform.
                </p>
            </div>

            <div className="grid gap-6 lg:grid-cols-2">
                <Card>
                    <CardHeader>
                        <CardTitle>
                            Appearance
                        </CardTitle>

                        <CardDescription>
                            User interface preferences.
                        </CardDescription>
                    </CardHeader>

                    <CardContent className="space-y-4">
                        <div className="flex items-center justify-between">
                            <span className="text-sm font-medium">
                                Theme
                            </span>

                            <Badge variant="secondary">
                                {resolvedTheme ??
                                    theme ??
                                    "system"}
                            </Badge>
                        </div>

                        <Separator />

                        <div className="flex items-center justify-between">
                            <span className="text-sm font-medium">
                                Accent Color
                            </span>

                            <Badge variant="outline">
                                Coming Soon
                            </Badge>
                        </div>
                    </CardContent>
                </Card>

                <Card>
                    <CardHeader>
                        <CardTitle>
                            Backend
                        </CardTitle>

                        <CardDescription>
                            Local backend connection.
                        </CardDescription>
                    </CardHeader>

                    <CardContent className="space-y-4">
                        <div className="flex items-center justify-between">
                            <span className="text-sm font-medium">
                                Status
                            </span>

                            <Badge
                                variant={
                                    backendOnline
                                        ? "success"
                                        : "destructive"
                                }
                            >
                                {backendOnline
                                    ? "Online"
                                    : "Offline"}
                            </Badge>
                        </div>

                        <Separator />

                        <div className="flex items-center justify-between">
                            <span className="text-sm font-medium">
                                Version
                            </span>

                            <Badge variant="outline">
                                {data?.version ??
                                    "Unknown"}
                            </Badge>
                        </div>

                        <Separator />

                        <div className="flex items-center justify-between">
                            <span className="text-sm font-medium">
                                API URL
                            </span>

                            <code className="rounded bg-muted px-2 py-1 text-xs">
                                http://127.0.0.1:8000
                            </code>
                        </div>
                    </CardContent>
                </Card>

                <Card>
                    <CardHeader>
                        <CardTitle>
                            AI Model
                        </CardTitle>

                        <CardDescription>
                            Current inference configuration.
                        </CardDescription>
                    </CardHeader>

                    <CardContent className="space-y-4">
                        <div className="flex items-center justify-between">
                            <span className="text-sm font-medium">
                                Model
                            </span>

                            <Badge variant="secondary">
                                qwen2.5:1.5b
                            </Badge>
                        </div>

                        <Separator />

                        <div className="flex items-center justify-between">
                            <span className="text-sm font-medium">
                                Temperature
                            </span>

                            <span className="text-sm">
                                0.2
                            </span>
                        </div>

                        <Separator />

                        <div className="flex items-center justify-between">
                            <span className="text-sm font-medium">
                                Top P
                            </span>

                            <span className="text-sm">
                                0.9
                            </span>
                        </div>
                    </CardContent>
                </Card>

                <Card>
                    <CardHeader>
                        <CardTitle>
                            Application
                        </CardTitle>

                        <CardDescription>
                            Frontend information.
                        </CardDescription>
                    </CardHeader>

                    <CardContent className="space-y-4">
                        <div className="flex items-center justify-between">
                            <span className="text-sm font-medium">
                                Platform
                            </span>

                            <Badge variant="secondary">
                                React + Vite
                            </Badge>
                        </div>

                        <Separator />

                        <div className="flex items-center justify-between">
                            <span className="text-sm font-medium">
                                Frontend
                            </span>

                            <span className="text-sm">
                                v0.4
                            </span>
                        </div>

                        <Separator />

                        <div className="flex items-center justify-between">
                            <span className="text-sm font-medium">
                                Status
                            </span>

                            <Badge variant="success">
                                Stable
                            </Badge>
                        </div>
                    </CardContent>
                </Card>
            </div>
        </section>
    );
}