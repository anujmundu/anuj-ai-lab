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
        <div className="flex gap-2">
            <input
                className="flex-1 rounded-md border bg-background px-3 py-2"
                placeholder="Ask anything..."
                value={value}
                onChange={(event) =>
                    onChange(event.target.value)
                }
            />

            <button
                className="rounded-md border px-4 py-2"
                disabled={disabled}
                onClick={onSubmit}
            >
                Ask
            </button>
        </div>
    );
}