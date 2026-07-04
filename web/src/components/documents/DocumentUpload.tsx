import { useState } from "react";

import { toast } from "sonner";

import { useIngestDocument } from "@/hooks";

import { Button } from "@/components/ui/button";
import {
    Card,
    CardContent,
} from "@/components/ui/card";

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
                toast.success(
                    "Document uploaded successfully.",
                );

                setFile(null);
            },

            onError(error) {
                toast.error(
                    error.message ||
                        "Document upload failed.",
                );
            },
        });
    }

    return (
        <Card>
            <CardContent className="space-y-6 pt-6">
                <UploadDropzone
                    selectedFile={file}
                    onFileSelect={setFile}
                    disabled={
                        ingestMutation.isPending
                    }
                />

                <div className="flex flex-wrap items-center gap-3">
                    <Button
                        onClick={handleUpload}
                        disabled={
                            !file ||
                            ingestMutation.isPending
                        }
                    >
                        {ingestMutation.isPending
                            ? "Uploading..."
                            : "Upload Document"}
                    </Button>
                </div>
            </CardContent>
        </Card>
    );
}