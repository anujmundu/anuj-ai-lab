import { useEffect, useState } from "react";
import { Controller, useForm } from "react-hook-form";

import { Pencil } from "lucide-react";

import { useUpdateMemory } from "@/hooks";

import type {
    Memory,
    UpdateMemoryRequest,
} from "@/types/memory";

import { Button } from "@/components/ui/button";
import { Checkbox } from "@/components/ui/checkbox";
import {
    Dialog,
    DialogContent,
    DialogFooter,
    DialogHeader,
    DialogTitle,
    DialogTrigger,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";

interface EditMemoryDialogProps {
    memory: Memory;
}

export default function EditMemoryDialog({
    memory,
}: EditMemoryDialogProps) {
    const [open, setOpen] =
        useState(false);

    const updateMemory =
        useUpdateMemory();

    const {
        control,
        register,
        handleSubmit,
        reset,
    } =
        useForm<UpdateMemoryRequest>({
            defaultValues: {
                content: "",
                category: "general",
                importance: 1,
                pinned: false,
            },
        });

    useEffect(() => {
        if (!open) {
            return;
        }

        reset({
            content: memory.content,
            category: memory.category,
            importance:
                memory.importance,
            pinned: memory.pinned,
        });
    }, [
        open,
        memory,
        reset,
    ]);

    async function onSubmit(
        values: UpdateMemoryRequest,
    ) {
        await updateMemory.mutateAsync({
            id: memory.id,
            memory: values,
        });

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
                    title="Edit Memory"
                    aria-label="Edit Memory"
                >
                    <Pencil className="h-4 w-4" />
                </Button>
            </DialogTrigger>

            <DialogContent className="sm:max-w-lg">
                <DialogHeader>
                    <DialogTitle>
                        Edit Memory
                    </DialogTitle>
                </DialogHeader>

                <form
                    onSubmit={handleSubmit(
                        onSubmit,
                    )}
                    className="space-y-5"
                >
                    <div className="space-y-2">
                        <Label htmlFor="content">
                            Content
                        </Label>

                        <Input
                            id="content"
                            {...register(
                                "content",
                                {
                                    required:
                                        true,
                                },
                            )}
                        />
                    </div>

                    <div className="space-y-2">
                        <Label htmlFor="category">
                            Category
                        </Label>

                        <Input
                            id="category"
                            {...register(
                                "category",
                            )}
                        />
                    </div>

                    <div className="space-y-2">
                        <Label htmlFor="importance">
                            Importance
                        </Label>

                        <Input
                            id="importance"
                            type="number"
                            min={1}
                            max={5}
                            {...register(
                                "importance",
                                {
                                    valueAsNumber:
                                        true,
                                    min: 1,
                                    max: 5,
                                },
                            )}
                        />
                    </div>

                    <div className="flex items-center gap-3">
                        <Controller
                            control={control}
                            name="pinned"
                            render={({
                                field,
                            }) => (
                                <Checkbox
                                    checked={
                                        field.value
                                    }
                                    onCheckedChange={(
                                        checked,
                                    ) =>
                                        field.onChange(
                                            checked ===
                                                true,
                                        )
                                    }
                                />
                            )}
                        />

                        <Label>
                            Pin this memory
                        </Label>
                    </div>

                    <DialogFooter>
                        <Button
                            type="submit"
                            disabled={
                                updateMemory.isPending
                            }
                        >
                            {updateMemory.isPending
                                ? "Saving..."
                                : "Save Changes"}
                        </Button>
                    </DialogFooter>
                </form>
            </DialogContent>
        </Dialog>
    );
}