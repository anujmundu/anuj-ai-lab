import { Cpu } from "lucide-react";

export default function ChatPage() {
  return (
    <section className="flex h-full flex-1 items-center justify-center p-8">
      <div className="flex max-w-2xl flex-col items-center text-center">
        <div className="mb-6 flex h-16 w-16 items-center justify-center rounded-2xl border bg-card shadow-sm">
          <Cpu className="h-8 w-8 text-primary" />
        </div>

        <h1 className="text-3xl font-semibold tracking-tight">
          Welcome to Anuj AI Lab
        </h1>

        <p className="mt-4 max-w-xl text-sm leading-7 text-muted-foreground">
          Build • RAG • Memory • Agents • Tools
        </p>
      </div>
    </section>
  );
}