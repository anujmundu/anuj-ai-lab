interface ChatInputProps {
    value: string;
    onChange: (value: string) => void;
    onSubmit: () => void;
    disabled?: boolean;
}

export function ChatInput({
    value,
    onChange,
    onSubmit,
    disabled = false,
}: ChatInputProps) {
    return (
        <div className="flex gap-3">
            <textarea
                className="min-h-24 flex-1 resize-none rounded-lg border bg-background px-4 py-3 text-sm outline-none"
                placeholder="Ask anything about your indexed documents..."
                value={value}
                disabled={disabled}
                onChange={(event) =>
                    onChange(event.target.value)
                }
                onKeyDown={(event) => {
                    if (
                        event.key === "Enter" &&
                        !event.shiftKey
                    ) {
                        event.preventDefault();
                        onSubmit();
                    }
                }}
            />

            <button
                className="rounded-lg border px-6 py-3"
                disabled={
                    disabled ||
                    value.trim().length === 0
                }
                onClick={onSubmit}
            >
                Ask
            </button>
        </div>
    );
}