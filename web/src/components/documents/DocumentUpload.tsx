import { useState } from "react";

import { useIngestDocument } from "@/hooks";

import { UploadDropzone } from "./UploadDropzone";

export function DocumentUpload() {
    const [file, setFile] =
        useState<File | null>(null);

    const ingestMutation =
        useIngestDocument();

    function handleUpload() {
        if (!file) {
            return;
        }

        ingestMutation.mutate(file, {
            onSuccess() {
                setFile(null);
            },
        });
    }

    return (
        <div className="rounded-xl border bg-card p-6 shadow-sm">
            <UploadDropzone
                selectedFile={file}
                onFileSelect={setFile}
                disabled={
                    ingestMutation.isPending
                }
            />

            <div className="mt-4 flex items-center gap-3">
                <button
                    className="rounded-md border px-4 py-2 text-sm font-medium"
                    disabled={
                        !file ||
                        ingestMutation.isPending
                    }
                    onClick={handleUpload}
                >
                    {ingestMutation.isPending
                        ? "Uploading..."
                        : "Upload"}
                </button>

                {ingestMutation.isError && (
                    <span className="text-sm text-red-600">
                        Upload failed.
                    </span>
                )}

                {ingestMutation.isSuccess && (
                    <span className="text-sm text-green-600">
                        Upload completed.
                    </span>
                )}
            </div>
        </div>
    );
}