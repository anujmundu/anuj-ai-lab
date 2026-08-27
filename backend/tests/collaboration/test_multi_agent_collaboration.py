from app.collaboration.blackboard import AgentBlackboard
from app.collaboration.hitl import HumanInTheLoopGate
from app.collaboration.models import AgentRole, CollaborationStatus
from app.collaboration.orchestrator import MultiAgentOrchestrator
from app.collaboration.roles import coder_agent, critic_agent, orchestrator_agent, researcher_agent


def test_blackboard_posting_and_retrieval():
    blackboard = AgentBlackboard()
    entry = blackboard.post(AgentRole.RESEARCHER, "research_findings", "Vector search is optimized.")

    assert entry.author_role == AgentRole.RESEARCHER
    assert len(blackboard.list_entries()) == 1
    assert len(blackboard.get_by_topic("research_findings")) == 1
    assert "Vector search is optimized" in blackboard.summarize()


def test_specialized_roles_execution():
    blackboard = AgentBlackboard()

    # Researcher
    research_res = researcher_agent.research("ChromaDB vector store", blackboard)
    assert "Research Findings" in research_res

    # Coder
    code_res = coder_agent.develop("FastAPI query endpoint", blackboard)
    assert "Code written" in code_res

    # Critic
    critique_res = critic_agent.review(blackboard)
    assert "Review Assessment" in critique_res
    assert "Consensus: Approved" in critique_res

    # Orchestrator
    synthesis = orchestrator_agent.synthesize("Build vector search", blackboard)
    assert "Multi-Agent Collaboration Consensus" in synthesis


def test_multi_agent_orchestrator_dialogue():
    orchestrator = MultiAgentOrchestrator()
    session = orchestrator.run_collaboration("Architect an agentic RAG system")

    assert session.status == CollaborationStatus.COMPLETED
    assert len(session.messages) >= 5
    assert session.final_synthesis is not None
    assert "Multi-Agent Collaboration Consensus" in session.final_synthesis
    assert len(session.blackboard) >= 3


def test_hitl_approval_gate():
    gate = HumanInTheLoopGate()
    req = gate.request_approval("session_123", "Execute high-privilege shell command")

    assert not req.is_decided
    assert not gate.is_approved("session_123")

    gate.submit_decision("session_123", approved=True)
    assert gate.is_approved("session_123")
