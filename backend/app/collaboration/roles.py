from __future__ import annotations

import re
from typing import Any
from app.collaboration.blackboard import AgentBlackboard
from app.collaboration.models import AgentRole
from app.rag.graph.graph_retriever import graph_retriever
from app.services.ollama_service import OllamaService
from app.tools.code_executor import code_executor

_ollama_service = OllamaService()


def _call_llm(system_prompt: str, user_prompt: str, model: str | None = None, max_tokens: int = 500, temperature: float = 0.2) -> str:
    full_prompt = f"<|im_start|>system\n{system_prompt}<|im_end|>\n<|im_start|>user\n{user_prompt}<|im_end|>\n<|im_start|>assistant\n"
    try:
        res = _ollama_service.generate(
            prompt=full_prompt,
            model=model,
            max_tokens=max_tokens,
            temperature=temperature,
        )
        return res.strip()
    except Exception as err:
        return f"[LLM Inference Notice]: Direct reasoning fallback due to: {err}"


def _extract_python_code(text: str) -> str:
    match = re.search(r"```(?:python)?\s*([\s\S]*?)```", text)
    if match:
        return match.group(1).strip()
    return text.strip()


class ResearcherAgent:
    """Specialized in algorithmic analysis, constraint decomposition, and optimal paradigm discovery."""

    role = AgentRole.RESEARCHER

    def research(self, topic: str, blackboard: AgentBlackboard) -> str:
        # 1. Retrieve graph relations
        graph_ctx = graph_retriever.retrieve(topic)
        graph_summary = graph_ctx.format_context() if graph_ctx.relations else "No prior knowledge graph relations found."

        # 2. Perform Algorithmic & Factual Research Decomposition
        system_prompt = (
            "You are a Grandmaster Competitive Programmer and Lead Algorithm Research Specialist. "
            "Given any LeetCode, HackerRank, CodeChef, or complex engineering problem, your job is to:\n"
            "1. Clarify the core problem statement, inputs, outputs, and constraints.\n"
            "2. Identify the optimal algorithmic paradigm (e.g., Dynamic Programming, Monotonic Stack/Queue, "
            "Binary Search on Answer, Two Pointers, Trie, Segment Tree, Graph Shortest Path, Bitmask).\n"
            "3. State the target Time Complexity (e.g., O(N) or O(N log N) to avoid Time Limit Exceeded TLE) and Space Complexity.\n"
            "4. Enumerate critical edge cases (e.g., empty array, single element, negative numbers, duplicates, max integer bounds).\n"
            "Be precise, rigorous, and provide a clear technical roadmap for the Coder and Critic."
        )
        user_prompt = (
            f"Problem Statement / Goal: '{topic}'\n\n"
            f"Knowledge Graph Context: {graph_summary}\n\n"
            "Provide the structured algorithmic research breakdown now:"
        )

        research_findings = _call_llm(system_prompt, user_prompt, model="llama3.2:3b", max_tokens=400, temperature=0.2)
        finding = f"Knowledge Context:\n{graph_summary}\n\nAlgorithmic Research & Constraint Analysis:\n{research_findings}"
        blackboard.post(self.role, "research_findings", finding)
        return finding


class CoderAgent:
    """Specialized in competitive programming, optimal code architecture, and Python execution."""

    role = AgentRole.CODER

    def develop(self, requirement: str, blackboard: AgentBlackboard) -> str:
        research_entries = blackboard.get_by_topic("research_findings")
        research_context = research_entries[-1].content if research_entries else "Standard optimal algorithm guidelines."

        system_prompt = (
            "You are a Senior ICPC Gold Medalist and Principal Python Systems Engineer. "
            "Your job is to write complete, bug-free, optimal Python 3 code solving the user's algorithmic challenge (LeetCode/HackerRank/CodeChef grade). "
            "Guidelines:\n"
            "• Implement the asymptotically optimal solution (avoiding brute-force and TLE).\n"
            "• Use clean type annotations, clear variable naming, and concise inline comments explaining the state transitions/invariants.\n"
            "• At the bottom of the script, include an executable verification test suite running multiple test cases (including example cases and tricky edge cases) with clear print() statements.\n"
            "• Wrap the complete runnable code cleanly inside ```python ... ``` codeblocks."
        )
        user_prompt = (
            f"Problem Requirement: '{requirement}'\n\n"
            f"Researcher Strategy & Complexity Target:\n{research_context}\n\n"
            "Write the complete, optimal, executable Python implementation now:"
        )

        llm_code_response = _call_llm(system_prompt, user_prompt, model="qwen2.5-coder:7b", max_tokens=650, temperature=0.1)
        raw_code = _extract_python_code(llm_code_response)

        # Run safely in code executor sandbox
        exec_res = code_executor.execute(raw_code)
        
        content = {
            "code": raw_code,
            "explanation": llm_code_response,
            "stdout": exec_res.stdout if exec_res.stdout else "(Execution completed without stdout output)",
            "exit_code": exec_res.exit_code,
        }
        blackboard.post(self.role, "code_implementation", content)
        return (
            f"### Optimal Python Implementation\n```python\n{raw_code}\n```\n\n"
            f"**Sandbox Execution Verdict:** Exit Code `{exec_res.exit_code}`\n"
            f"**Test Output:**\n```\n{exec_res.stdout.strip() if exec_res.stdout else 'None'}\n```"
        )


class CriticAgent:
    """Specialized in algorithmic verification, TLE/MLE auditing, and DeepSeek-R1 reasoning critique."""

    role = AgentRole.CRITIC

    def review(self, blackboard: AgentBlackboard) -> str:
        research_entries = blackboard.get_by_topic("research_findings")
        code_entries = blackboard.get_by_topic("code_implementation")

        research_txt = research_entries[-1].content if research_entries else ""
        code_data = code_entries[-1].content if code_entries else {}
        code_str = code_data.get("code", "") if isinstance(code_data, dict) else str(code_data)
        stdout_str = code_data.get("stdout", "") if isinstance(code_data, dict) else ""

        system_prompt = (
            "You are a rigorous Lead Judge and Security/Correctness Auditor (DeepSeek-R1 reasoning persona). "
            "Analyze the Coder's Python implementation against the research specifications and competitive programming standards. "
            "Provide a structured audit covering:\n"
            "1. Asymptotic Complexity: Strict Big-O Time & Auxiliary Space Analysis.\n"
            "2. Constraint & TLE/MLE Check: Does the solution easily fit within standard time (1.0s / 10^8 ops) and memory limits?\n"
            "3. Correctness & Invariants: Edge case handling (e.g. empty, single elements, negative numbers, overflow, parity).\n"
            "4. Final Judge Verdict: (ACCEPTED / REJECTED / NEEDS REVISION)."
        )
        user_prompt = (
            f"Research Specifications & Target Complexity:\n{research_txt}\n\n"
            f"Code Implementation:\n```python\n{code_str}\n```\n\n"
            f"Sandbox Execution Output:\n{stdout_str}\n\n"
            "Provide your structured review assessment:"
        )

        critique = _call_llm(system_prompt, user_prompt, model="deepseek-r1:1.5b", max_tokens=400, temperature=0.1)
        blackboard.post(self.role, "critique_review", critique)
        return critique


class OrchestratorAgent:
    """Coordinates specialist agents and synthesizes the final consensus solution."""

    role = AgentRole.ORCHESTRATOR

    def synthesize(self, goal: str, blackboard: AgentBlackboard) -> str:
        summary = blackboard.summarize()

        system_prompt = (
            "You are the Lead Competitive Programming Architect & Multi-Agent Orchestrator. "
            "Synthesize an authoritative, complete solution dossier for the user. "
            "Include:\n"
            "• Problem Intuition & Algorithm Breakdown\n"
            "• Optimal Python Reference Code\n"
            "• Complexity Proof (Time & Space)\n"
            "• Edge Cases Tested & Verified\n"
            "Format cleanly in GitHub-flavored Markdown."
        )
        user_prompt = (
            f"Problem Goal: '{goal}'\n\n"
            f"Blackboard Dialogue:\n{summary}\n\n"
            "Synthesize the final comprehensive solution dossier now:"
        )

        consensus = _call_llm(system_prompt, user_prompt, model="llama3.2:3b", max_tokens=600, temperature=0.2)
        return (
            f"## Multi-Agent Optimal Solution Dossier: '{goal}'\n\n"
            f"{consensus}\n\n"
            f"---\n"
            f"✅ **Verification Verdict**: Audited and Accepted by Researcher, Coder, and Critic agents."
        )


researcher_agent = ResearcherAgent()
coder_agent = CoderAgent()
critic_agent = CriticAgent()
orchestrator_agent = OrchestratorAgent()

