import { useState } from "react";

import {
    AlertTriangle,
    Trash2,
} from "lucide-react";

import { useDeleteMemory } from "@/hooks";

import { Button } from "@/components/ui/button";
import {
    Dialog,
    DialogContent,
    DialogDescription,
    DialogFooter,
    DialogHeader,
    DialogTitle,
    DialogTrigger,
} from "@/components/ui/dialog";

interface DeleteMemoryDialogProps {
    id: number;
}

export default function DeleteMemoryDialog({
    id,
}: DeleteMemoryDialogProps) {
    const [open, setOpen] =
        useState(false);

    const deleteMemory =
        useDeleteMemory();

    async function handleDelete() {
        await deleteMemory.mutateAsync(id);

        setOpen(false);
    }

    return (
        <Dialog
            open={open}
            onOpenChange={setOpen}
        >
            <DialogTrigger asChild>
                <Button
                    variant="ghost"
                    size="icon"
                    aria-label="Delete Memory"
                    title="Delete Memory"
                >
                    <Trash2 className="h-4 w-4" />
                </Button>
            </DialogTrigger>

            <DialogContent>
                <DialogHeader>
                    <DialogTitle className="flex items-center gap-2">
                        <AlertTriangle className="h-5 w-5 text-destructive" />
                        Delete Memory
                    </DialogTitle>

                    <DialogDescription>
                        Are you sure you want to delete this memory?
                        This action cannot be undone.
                    </DialogDescription>
                </DialogHeader>

                <DialogFooter>
                    <Button
                        variant="outline"
                        onClick={() =>
                            setOpen(false)
                        }
                    >
                        Cancel
                    </Button>

                    <Button
                        variant="destructive"
                        onClick={handleDelete}
                        disabled={
                            deleteMemory.isPending
                        }
                    >
                        {deleteMemory.isPending
                            ? "Deleting..."
                            : "Delete"}
                    </Button>
                </DialogFooter>
            </DialogContent>
        </Dialog>
    );
}