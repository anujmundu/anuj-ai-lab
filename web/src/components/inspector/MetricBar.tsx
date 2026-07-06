interface MetricBarProps {
    value: number;
    max?: number;
}

export function MetricBar({
    value,
    max = 100,
}: MetricBarProps) {
    const width = Math.max(
        0,
        Math.min((value / max) * 100, 100),
    );

    return (
        <div className="mt-2 h-2 w-full overflow-hidden rounded-full bg-slate-200 dark:bg-slate-800">
            <div
                className="h-full rounded-full bg-slate-900 transition-all dark:bg-slate-100"
                style={{
                    width: `${width}%`,
                }}
            />
        </div>
    );
}