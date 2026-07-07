import { Search } from "lucide-react";

import { Input } from "@/components/ui/input";

interface MemorySearchProps {
    value: string;
    onChange(
        value: string,
    ): void;
}

export default function MemorySearch({
    value,
    onChange,
}: MemorySearchProps) {
    return (
        <div className="relative">
            <Search className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />

            <Input
                value={value}
                onChange={(e) =>
                    onChange(
                        e.target.value,
                    )
                }
                placeholder="Search memories..."
                className="pl-9"
            />
        </div>
    );
}