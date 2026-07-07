import { useState } from "react";

import {
    useMemories,
    useSearchMemories,
} from "@/hooks";

import MemoryForm from "@/components/memory/MemoryForm";
import MemoryList from "@/components/memory/MemoryList";
import MemorySearch from "@/components/memory/MemorySearch";

export default function MemoryPage() {
    const [search, setSearch] =
        useState("");

    const {
        data: memories = [],
        isLoading,
    } = useMemories();

    const {
        data: searchedMemories = [],
    } = useSearchMemories(search);

    const displayedMemories =
        search.trim().length > 0
            ? searchedMemories
            : memories;

    return (
        <section className="flex flex-1 flex-col gap-6 p-6">
            <div>
                <h1 className="text-3xl font-bold tracking-tight">
                    Memory
                </h1>

                <p className="mt-2 text-muted-foreground">
                    Persistent knowledge base for your AI
                    assistant.
                </p>
            </div>

            <MemoryForm />

            <MemorySearch
                value={search}
                onChange={setSearch}
            />

            {isLoading ? (
                <div className="rounded-xl border p-8 text-center text-muted-foreground">
                    Loading memories...
                </div>
            ) : (
                <MemoryList
                    memories={displayedMemories}
                />
            )}
        </section>
    );
}