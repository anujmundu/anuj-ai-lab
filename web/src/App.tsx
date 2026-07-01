import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Separator } from "@/components/ui/separator";

export default function App() {
  return (
    <main className="flex min-h-screen items-center justify-center bg-slate-950 p-8">
      <Card className="w-full max-w-md">
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle>Anuj AI Lab</CardTitle>

            <Badge variant="success">
              Online
            </Badge>
          </div>

          <CardDescription>
            Production-ready AI Engineering Platform
          </CardDescription>
        </CardHeader>

        <Separator />

        <CardContent className="space-y-4 pt-6">
          <p className="text-sm text-slate-500 dark:text-slate-400">
            Stage 3.5 — Modern Web Client
          </p>

          <Button className="w-full">
            Get Started
          </Button>
        </CardContent>
      </Card>
    </main>
  );
}