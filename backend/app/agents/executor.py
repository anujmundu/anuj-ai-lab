from __future__ import annotations

import re
import time
from typing import Any
from app.agents.models import AgentStep, AgentTask, TaskStatus
from app.agents.planner import AgentPlanner, agent_planner
from app.agents.reflection import ReflectionEvaluator, reflection_evaluator
from app.agents.task_store import AgentTaskStore, agent_task_store
from app.services.ollama_service import OllamaService
from app.tools.registry import ToolRegistry, tool_registry

_ollama = OllamaService()


def _call_agent_llm(system_prompt: str, user_prompt: str, model: str = "llama3.2:3b", max_tokens: int = 350, temperature: float = 0.1) -> str:
    full_prompt = f"<|im_start|>system\n{system_prompt}<|im_end|>\n<|im_start|>user\n{user_prompt}<|im_end|>\n<|im_start|>assistant\n"
    try:
        res = _ollama.generate(prompt=full_prompt, model=model, max_tokens=max_tokens, temperature=temperature)
        return res.strip()
    except Exception as err:
        return f"[Agent LLM Inference Notice]: {err}"


class AgentExecutor:
    """
    Executes autonomous multi-step reasoning tasks through the Thought -> Action -> Observation -> Reflection loop.
    """

    def __init__(
        self,
        planner: AgentPlanner | None = None,
        evaluator: ReflectionEvaluator | None = None,
        registry: ToolRegistry | None = None,
        store: AgentTaskStore | None = None,
    ) -> None:
        self.planner = planner or agent_planner
        self.evaluator = evaluator or reflection_evaluator
        self.registry = registry or tool_registry
        self.store = store or agent_task_store

    def run_task(
        self,
        goal: str,
        task_id: str | None = None,
        max_steps: int = 8,
    ) -> AgentTask:
        """
        Executes a goal-driven multi-step agent workflow.
        """
        task = AgentTask(goal=goal)
        if task_id:
            task.task_id = task_id

        self.store.save(task)

        # 1. Planning Phase
        task.status = TaskStatus.PLANNING
        self.store.save(task)

        try:
            task.plan = self.planner.plan(goal)
            task.status = TaskStatus.RUNNING
            self.store.save(task)

            collected_outputs: list[str] = []

            # 2. Execution Phase
            for index, subtask in enumerate(task.plan.subtasks, start=1):
                if index > max_steps:
                    break

                thought = f"Executing subtask {subtask.id}: {subtask.description}"
                action_name = subtask.tool_name or "reasoning"
                action_input: dict[str, Any] = {}
                start_step_time = time.perf_counter()

                # Dispatch tool if specified
                if subtask.tool_name and subtask.tool_name in self.registry.list_tools():
                    if subtask.tool_name == "calculator":
                        calc_sys = (
                            "You are a mathematical parser. Extract the mathematical formula needed to solve the subtask as a single arithmetic expression. "
                            "Output ONLY the arithmetic expression (e.g. '15000 * (1 + 0.075)**5' or '15000 * ((1 + 0.075)**5 - 1)'). "
                            "Do NOT write words, explanations, or markdown."
                        )
                        raw_expr = _call_agent_llm(calc_sys, f"Goal: {goal}\nSubtask: {subtask.description}", model="llama3.2:3b", max_tokens=80)
                        clean_expr = raw_expr.strip().replace("`", "").replace("'", "").replace('"', "").replace(",", "")
                        if "\n" in clean_expr:
                            clean_expr = clean_expr.split("\n")[-1].strip()
                        action_input = {"expression": clean_expr}
                        tool_res = self.registry.execute("calculator", **action_input)

                    elif subtask.tool_name == "python_interpreter":
                        py_sys = (
                            "You are an autonomous Python code generator. Write concise, complete, runnable Python 3 code solving the user subtask with print() outputs. "
                            "Output ONLY the Python code inside ```python ... ``` codeblocks."
                        )
                        raw_code = _call_agent_llm(py_sys, f"Goal: {goal}\nSubtask: {subtask.description}", model="qwen2.5-coder:7b", max_tokens=400)
                        match = re.search(r"```(?:python)?\s*([\s\S]*?)```", raw_code)
                        extracted = match.group(1).strip() if match else raw_code.strip()
                        action_input = {"code": extracted}
                        tool_res = self.registry.execute("python_interpreter", **action_input)

                    elif subtask.tool_name == "file_system":
                        path_match = re.search(r"([\w\-\.\/\\\:]+\.(?:py|json|md|txt|ts|tsx|csv))", goal)
                        target_path = path_match.group(1).strip() if path_match else "backend/main.py"
                        action_input = {"action": "exists", "path": target_path}
                        tool_res = self.registry.execute("file_system", **action_input)

                    else:
                        action_input = {}
                        tool_res = self.registry.execute(subtask.tool_name, **action_input)

                    observation = tool_res.output if tool_res.success else tool_res.error
                    step_success = tool_res.success
                else:
                    # Pure reasoning step with local LLM
                    re_sys = "You are an autonomous analytical reasoning agent. Execute the reasoning subtask thoroughly and provide structured analytical deductions."
                    context_history = "\n".join(collected_outputs) if collected_outputs else "No previous steps."
                    observation = _call_agent_llm(re_sys, f"Goal: {goal}\nSubtask: {subtask.description}\nPrior Step Observations:\n{context_history}", model="llama3.2:3b", max_tokens=300)
                    step_success = True

                duration_ms = (time.perf_counter() - start_step_time) * 1000.0

                step = AgentStep(
                    step_number=index,
                    thought=thought,
                    action=action_name,
                    action_input=action_input,
                    observation=observation,
                    success=step_success,
                    execution_time_ms=round(duration_ms, 2),
                )

                # 3. Reflection Phase
                refl = self.evaluator.evaluate_step(step)
                step.reflection = refl.feedback

                task.steps.append(step)
                subtask.status = TaskStatus.COMPLETED if step_success else TaskStatus.FAILED
                subtask.result = observation
                collected_outputs.append(f"• Step {index} ({action_name}): {observation}")

                self.store.save(task)

            # 4. Final Comprehensive Synthesis
            synth_sys = (
                "You are the Lead Autonomous AI Agent. "
                "Synthesize an authoritative, highly comprehensive final solution answering the user's overall goal based on all executed steps and observations. "
                "Include numerical answers, key findings, and clear Markdown formatting."
            )
            synth_user = f"Overall Goal: '{goal}'\n\nExecuted Steps & Tool Observations:\n" + "\n".join(collected_outputs)
            task.result = _call_agent_llm(synth_sys, synth_user, model="llama3.2:3b", max_tokens=500, temperature=0.2)
            task.status = TaskStatus.COMPLETED
            task.updated_at = time.time()
            self.store.save(task)
            return task

        except Exception as exc:
            task.status = TaskStatus.FAILED
            task.error = str(exc)
            task.updated_at = time.time()
            self.store.save(task)
            return task


agent_executor = AgentExecutor()

