import { X } from "lucide-react";

import {
    Dialog,
    DialogContent,
    DialogTitle,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";

import { NavigationContent } from "./NavigationContent";

interface MobileSidebarProps {
    open: boolean;
    onOpenChange: (open: boolean) => void;
}

export function MobileSidebar({
    open,
    onOpenChange,
}: MobileSidebarProps) {
    function handleNavigate() {
        onOpenChange(false);
    }

    return (
        <Dialog
            open={open}
            onOpenChange={onOpenChange}
        >
            <DialogContent
                className="left-0 top-0 h-screen w-72 max-w-none translate-x-0 translate-y-0 rounded-none border-r p-0 data-[state=open]:slide-in-from-left data-[state=closed]:slide-out-to-left"
            >
                <div className="flex h-16 items-center justify-between border-b border-slate-200 px-4 dark:border-slate-800">
                    <DialogTitle className="text-lg font-semibold">
                        Navigation
                    </DialogTitle>

                    <Button
                        variant="ghost"
                        size="icon"
                        onClick={() =>
                            onOpenChange(false)
                        }
                    >
                        <X className="h-5 w-5" />
                    </Button>
                </div>

                <div className="flex h-[calc(100vh-4rem)] flex-col">
                    <NavigationContent
                        onNavigate={
                            handleNavigate
                        }
                    />
                </div>
            </DialogContent>
        </Dialog>
    );
}

export default MobileSidebar;