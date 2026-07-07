import {
    Pin,
    Star,
} from "lucide-react";

import type { Memory } from "@/types/memory";

import { Badge } from "@/components/ui/badge";
import { Card } from "@/components/ui/card";

import DeleteMemoryDialog from "./DeleteMemoryDialog";
import EditMemoryDialog from "./EditMemoryDialog";

interface MemoryCardProps {
    memory: Memory;
}

export default function MemoryCard({
    memory,
}: MemoryCardProps) {
    return (
        <Card className="p-5 transition-shadow hover:shadow-md">
            <div className="flex items-start justify-between gap-6">
                <div className="flex-1 space-y-3">
                    <p className="text-base font-medium">
                        {memory.content}
                    </p>

                    <div className="flex flex-wrap items-center gap-2">
                        <Badge variant="secondary">
                            {memory.category}
                        </Badge>

                        <Badge
                            variant="outline"
                            className="gap-1"
                        >
                            {Array.from({
                                length: 5,
                            }).map(
                                (
                                    _,
                                    index,
                                ) => (
                                    <Star
                                        key={
                                            index
                                        }
                                        className={`h-3.5 w-3.5 ${
                                            index <
                                            memory.importance
                                                ? "fill-current"
                                                : "opacity-30"
                                        }`}
                                    />
                                ),
                            )}
                        </Badge>

                        {memory.pinned && (
                            <Badge className="gap-1">
                                <Pin className="h-3 w-3" />
                                Pinned
                            </Badge>
                        )}
                    </div>
                </div>

                <div className="flex items-center gap-2">
                    <EditMemoryDialog
                        memory={memory}
                    />

                    <DeleteMemoryDialog
                        id={memory.id}
                    />
                </div>
            </div>
        </Card>
    );
}