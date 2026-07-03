interface TimingCardProps {
    label: string;
    seconds: number;
}

export function TimingCard({
    label,
    seconds,
}: TimingCardProps) {
    return (
        <div className="rounded-lg border bg-card p-4 shadow-sm">
            <h3 className="text-sm font-medium text-muted-foreground">
                {label}
            </h3>

            <p className="mt-2 text-2xl font-bold">
                {seconds.toFixed(3)} s
            </p>
        </div>
    );
}