import { Badge } from "@/components/ui/badge";

interface Props {
    risk: number;
}

export function HallucinationBadge({
    risk,
}: Props) {
    if (risk < 0.25) {
        return (
            <Badge variant="success">
                Low Risk
            </Badge>
        );
    }

    if (risk < 0.5) {
        return (
            <Badge variant="warning">
                Medium Risk
            </Badge>
        );
    }

    return (
        <Badge variant="destructive">
            High Risk
        </Badge>
    );
}