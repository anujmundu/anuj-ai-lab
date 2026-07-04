import type { ChangeEvent } from "react";

import {
    FileText,
    Upload,
} from "lucide-react";

import { Button } from "@/components/ui/button";

interface UploadDropzoneProps {
    selectedFile: File | null;
    disabled?: boolean;

    onFileSelect: (
        file: File | null,
    ) => void;
}

export function UploadDropzone({
    selectedFile,
    disabled = false,
    onFileSelect,
}: UploadDropzoneProps) {
    function handleChange(
        event: ChangeEvent<HTMLInputElement>,
    ) {
        const file =
            event.target.files?.[0] ?? null;

        onFileSelect(file);

        event.target.value = "";
    }

    return (
        <div className="rounded-xl border-2 border-dashed border-slate-300 bg-slate-50 p-8 transition-colors dark:border-slate-700 dark:bg-slate-900/40">
            <div className="flex flex-col items-center gap-5 text-center">
                <div className="flex h-14 w-14 items-center justify-center rounded-full bg-slate-200 dark:bg-slate-800">
                    <Upload className="h-7 w-7" />
                </div>

                <div>
                    <h3 className="text-lg font-semibold">
                        Upload Document
                    </h3>

                    <p className="mt-2 text-sm text-muted-foreground">
                        Upload TXT, Markdown, PDF,
                        or other supported
                        document types for
                        indexing.
                    </p>
                </div>

                <label>
                    <input
                        type="file"
                        className="hidden"
                        disabled={disabled}
                        onChange={handleChange}
                    />

                    <Button
                        type="button"
                        variant="outline"
                        asChild
                    >
                        <span>
                            Choose File
                        </span>
                    </Button>
                </label>

                <div className="flex min-h-14 w-full items-center justify-center rounded-lg border bg-background px-4 py-3">
                    {selectedFile ? (
                        <div className="flex items-center gap-2 text-sm font-medium">
                            <FileText className="h-4 w-4" />

                            <span>
                                {selectedFile.name}
                            </span>
                        </div>
                    ) : (
                        <span className="text-sm text-muted-foreground">
                            No file selected
                        </span>
                    )}
                </div>

                <p className="text-xs text-muted-foreground">
                    Maximum file size depends on
                    your backend configuration.
                </p>
            </div>
        </div>
    );
}