interface ConfidenceCardProps {
    confidence: number;
}

export function ConfidenceCard({
    confidence,
}: ConfidenceCardProps) {
    return (
        <div className="rounded-lg border bg-card p-4 shadow-sm">
            <h3 className="text-sm font-medium text-muted-foreground">
                Confidence
            </h3>

            <p className="mt-2 text-2xl font-bold">
                {(confidence * 100).toFixed(0)}%
            </p>
        </div>
    );
}