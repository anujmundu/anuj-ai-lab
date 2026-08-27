import uuid
from sqlmodel import Session
from app.db.database import create_db_and_tables, engine
from app.db.chat_models import ChatMessage, ChatSession
from app.memory.consolidation import MemoryConsolidationEngine


def setup_module():
    create_db_and_tables()


def test_fact_extraction():
    engine = MemoryConsolidationEngine()
    text = "I prefer Python 3.11 for backend services and I always use FastAPI for REST APIs."
    facts = engine.extract_facts_from_text(text)

    assert len(facts) >= 2
    categories = [cat for _, cat in facts]
    assert "preference" in categories or "technical_rule" in categories


def test_session_consolidation_db():
    engine_inst = MemoryConsolidationEngine()
    uid = uuid.uuid4().hex[:8]
    session_id = f"test_consolidation_sess_{uid}"
    unique_content = f"My stack is FastAPI and SQLite-{uid}."

    with Session(engine) as db_session:
        cs = ChatSession(session_id=session_id, title="Test Consolidation")
        db_session.add(cs)
        msg1 = ChatMessage(
            session_id=session_id,
            role="user",
            content=unique_content,
        )
        msg2 = ChatMessage(
            session_id=session_id,
            role="assistant",
            content="Understood! I will use that stack.",
        )
        db_session.add(msg1)
        db_session.add(msg2)
        db_session.commit()

    created = engine_inst.consolidate_session(session_id)
    assert len(created) >= 1
    assert any(uid in m.content for m in created)

