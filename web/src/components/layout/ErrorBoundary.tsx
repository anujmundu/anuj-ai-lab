import { useRouteError, isRouteErrorResponse, Link } from "react-router-dom";
import { AlertTriangle, RefreshCw, Home } from "lucide-react";
import { Button } from "@/components/ui/button";

export function ErrorBoundary() {
    const error = useRouteError();

    let errorMessage = "An unexpected error occurred.";
    if (isRouteErrorResponse(error)) {
        errorMessage = `${error.status} ${error.statusText}: ${error.data || "Page not found"}`;
    } else if (error instanceof Error) {
        errorMessage = error.message;
    }

    return (
        <div className="flex min-h-screen flex-col items-center justify-center bg-slate-50 p-6 dark:bg-slate-950">
            <div className="w-full max-w-md rounded-2xl border border-slate-200 bg-white p-8 shadow-xl dark:border-slate-800 dark:bg-slate-900 text-center">
                <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-2xl bg-amber-50 text-amber-600 dark:bg-amber-950/50 dark:text-amber-400 mb-4">
                    <AlertTriangle className="h-7 w-7" />
                </div>
                
                <h2 className="text-xl font-bold text-slate-900 dark:text-white">
                    Something went wrong
                </h2>
                
                <p className="mt-2 text-xs font-mono text-slate-500 bg-slate-100 dark:bg-slate-800 p-3 rounded-lg text-left overflow-auto max-h-32">
                    {errorMessage}
                </p>

                <div className="mt-6 flex items-center justify-center gap-3">
                    <Button 
                        onClick={() => window.location.reload()} 
                        variant="outline"
                        className="flex items-center gap-2 text-xs"
                    >
                        <RefreshCw className="h-4 w-4" /> Reload
                    </Button>

                    <Button asChild className="bg-indigo-600 hover:bg-indigo-700 text-white text-xs">
                        <Link to="/" className="flex items-center gap-2">
                            <Home className="h-4 w-4" /> Go to Chat
                        </Link>
                    </Button>
                </div>
            </div>
        </div>
    );
}

export default ErrorBoundary;
