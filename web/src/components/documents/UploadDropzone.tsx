import type { ChangeEvent } from "react";

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
    }

    return (
        <div className="rounded-lg border border-dashed bg-card p-6">
            <div className="flex flex-col gap-4">
                <div>
                    <h3 className="text-lg font-semibold">
                        Upload Document
                    </h3>

                    <p className="text-sm text-muted-foreground">
                        Supported formats include
                        TXT, Markdown, PDF and other
                        supported document types.
                    </p>
                </div>

                <input
                    type="file"
                    disabled={disabled}
                    onChange={handleChange}
                />

                <div className="rounded-md bg-muted p-3 text-sm">
                    {selectedFile ? (
                        <>
                            <span className="font-medium">
                                Selected:
                            </span>{" "}
                            {selectedFile.name}
                        </>
                    ) : (
                        "No file selected."
                    )}
                </div>
            </div>
        </div>
    );
}