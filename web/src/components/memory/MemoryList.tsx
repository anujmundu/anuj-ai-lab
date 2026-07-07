import type { Memory } from "@/types/memory";

import EmptyMemory from "./EmptyMemory";
import MemoryCard from "./MemoryCard";

interface MemoryListProps {
    memories: Memory[];
}

export default function MemoryList({
    memories,
}: MemoryListProps) {
    if (memories.length === 0) {
        return <EmptyMemory />;
    }

    return (
        <div className="space-y-4">
            {memories.map((memory) => (
                <MemoryCard
                    key={memory.id}
                    memory={memory}
                />
            ))}
        </div>
    );
}