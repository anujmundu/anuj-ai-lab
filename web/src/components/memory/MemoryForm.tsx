import { useForm } from "react-hook-form";

import { useCreateMemory } from "@/hooks";

import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";

type FormData = {
    content: string;
    category: string;
    importance: number;
};

export default function MemoryForm() {
    const createMemory =
        useCreateMemory();

    const {
        register,
        handleSubmit,
        reset,
    } = useForm<FormData>({
        defaultValues: {
            content: "",
            category: "general",
            importance: 1,
        },
    });

    async function onSubmit(
        values: FormData,
    ) {
        await createMemory.mutateAsync(
            values,
        );

        reset();
    }

    return (
        <Card className="p-5">
            <form
                onSubmit={handleSubmit(
                    onSubmit,
                )}
                className="space-y-4"
            >
                <Input
                    placeholder="Memory..."
                    {...register(
                        "content",
                        {
                            required: true,
                        },
                    )}
                />

                <Input
                    placeholder="Category"
                    {...register(
                        "category",
                    )}
                />

                <Input
                    type="number"
                    min={1}
                    max={5}
                    {...register(
                        "importance",
                        {
                            valueAsNumber: true,
                        },
                    )}
                />

                <Button
                    type="submit"
                    disabled={
                        createMemory.isPending
                    }
                >
                    {createMemory.isPending
                        ? "Saving..."
                        : "Add Memory"}
                </Button>
            </form>
        </Card>
    );
}