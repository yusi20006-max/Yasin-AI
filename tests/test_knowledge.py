"""Unit and integration tests for YasinAI Knowledge Platform."""

import os
import pytest
from unittest.mock import patch, MagicMock

from yasinai.knowledge_platform.short_term_memory import ShortTermMemory
from yasinai.knowledge_platform.long_term_memory import LongTermMemory
from yasinai.knowledge_platform.manager import MemoryManager
from yasinai.knowledge_platform.entity import Entity
from yasinai.knowledge_platform.relation import Relation
from yasinai.knowledge_platform.graph import KnowledgeGraph
from yasinai.knowledge_platform.query_engine import QueryEngine
from yasinai.knowledge_platform.search import LocalSemanticRetriever
from yasinai.knowledge_platform.context import FormattedContext
from yasinai.knowledge_platform.builder import ContextBuilder
from yasinai.cli.main import main


# Test files cleanup helper
@pytest.fixture
def temp_storage_path():
    path = "tests/temp_long_term_memory.json"
    if os.path.exists(path):
        os.remove(path)
    yield path
    if os.path.exists(path):
        os.remove(path)


def test_short_term_memory():
    stm = ShortTermMemory()
    assert len(stm.get_messages()) == 0

    stm.add_message("user", "Hello, YasinAI!")
    stm.add_message("assistant", "Hello! How can I assist you today?")

    msgs = stm.get_messages()
    assert len(msgs) == 2
    assert msgs[0]["role"] == "user"
    assert msgs[0]["content"] == "Hello, YasinAI!"
    assert msgs[1]["role"] == "assistant"

    stm.clear()
    assert len(stm.get_messages()) == 0


def test_long_term_memory(temp_storage_path):
    ltm = LongTermMemory(storage_path=temp_storage_path)
    assert len(ltm.list_keys()) == 0

    ltm.store("user_profile", {"name": "Alice", "role": "Developer"})
    assert ltm.retrieve("user_profile") == {"name": "Alice", "role": "Developer"}
    assert "user_profile" in ltm.list_keys()

    # Re-initialize to test persistence
    ltm2 = LongTermMemory(storage_path=temp_storage_path)
    assert ltm2.retrieve("user_profile") == {"name": "Alice", "role": "Developer"}

    # Test deletion
    assert ltm2.delete("user_profile") is True
    assert ltm2.retrieve("user_profile") is None
    assert ltm2.delete("non_existent") is False

    ltm2.store("temp_key", "temp_value")
    ltm2.clear()
    assert len(ltm2.list_keys()) == 0


def test_memory_manager(temp_storage_path):
    mgr = MemoryManager(long_term_storage_path=temp_storage_path)

    # Short term check
    mgr.add_conversation_message("user", "Hello")
    assert len(mgr.get_conversation_history()) == 1
    assert mgr.get_conversation_history()[0]["content"] == "Hello"

    # Long term check
    mgr.persist_to_long_term("fact1", "YasinAI is modular")
    assert mgr.fetch_from_long_term("fact1") == "YasinAI is modular"

    # Clear all
    mgr.clear_all()
    assert len(mgr.get_conversation_history()) == 0
    assert mgr.fetch_from_long_term("fact1") is None


def test_knowledge_graph():
    kg = KnowledgeGraph()

    # Entities
    e1 = Entity(id="1", name="YasinAI", type="Platform", properties={"version": "1.0.0"})
    e2 = Entity(id="2", name="Alice", type="Developer")

    kg.add_entity(e1)
    kg.add_entity(e2)

    assert kg.get_entity("1").name == "YasinAI"
    assert kg.get_entity("1").get_property("version") == "1.0.0"

    # Relations
    r1 = Relation(type="developed_by", source_id="1", target_id="2", properties={"since": "2026"})
    kg.add_relation(r1)

    triples = kg.get_triples()
    assert len(triples) == 1
    assert triples[0] == ("1", "developed_by", "2")

    # Neighbors
    neighbors = kg.get_neighbors("1", direction="out")
    assert len(neighbors) == 1
    assert neighbors[0][0].id == "2"
    assert neighbors[0][1].type == "developed_by"
    assert neighbors[0][1].get_property("since") == "2026"

    # Remove entity
    assert kg.remove_entity("2") is True
    assert kg.get_entity("2") is None
    assert len(kg.get_triples()) == 0


def test_query_engine():
    kg = KnowledgeGraph()
    e1 = Entity(id="1", name="YasinAI", type="Platform", properties={"lang": "Python"})
    e2 = Entity(id="2", name="Alice", type="Developer")
    e3 = Entity(id="3", name="Bob", type="Manager")

    kg.add_entity(e1)
    kg.add_entity(e2)
    kg.add_entity(e3)

    kg.add_relation(Relation(type="created_by", source_id="1", target_id="2"))
    kg.add_relation(Relation(type="reports_to", source_id="2", target_id="3"))

    qe = QueryEngine(kg)

    # Pattern matching
    matches = qe.match_triple(predicate="created_by")
    assert len(matches) == 1
    assert matches[0] == ("1", "created_by", "2")

    # BFS traversal
    path = qe.find_path("1", "3")
    assert path == ["1", "2", "3"]

    # Search by property
    lang_matches = qe.search_by_property("lang", "Python")
    assert len(lang_matches) == 1
    assert lang_matches[0].id == "1"


def test_semantic_search():
    retriever = LocalSemanticRetriever()

    retriever.add_document("doc1", "YasinAI is a highly modular platform for artificial intelligence.")
    retriever.add_document("doc2", "Alice is a software development engineer working on various core frameworks.")
    retriever.add_document("doc3", "Python is the primary language used to build the AI orchestration layers.")

    results = retriever.search("modular platform")
    assert len(results) > 0
    # Top result should be doc1 because of exact/high match
    assert results[0][0]["id"] == "doc1"
    assert results[0][1] > 0.0

    # Ensure search with empty / unrelated queries is handled
    assert len(retriever.search("")) == 0
    assert len(retriever.search("xyzqrs")) == 0


def test_context_building(temp_storage_path):
    mgr = MemoryManager(long_term_storage_path=temp_storage_path)
    kg = KnowledgeGraph()
    retriever = LocalSemanticRetriever()

    mgr.add_conversation_message("user", "Who built you?")
    mgr.add_conversation_message("assistant", "I was built by Alice.")

    kg.add_entity(Entity(id="YasinAI", name="YasinAI"))
    kg.add_entity(Entity(id="Alice", name="Alice"))
    kg.add_relation(Relation(type="created_by", source_id="YasinAI", target_id="Alice"))

    retriever.add_document("mem1", "YasinAI utilizes a highly optimized localized memory platform.")

    builder = ContextBuilder(mgr, kg, retriever)
    builder.set_system_context("Always be helpful and concise.")

    context = builder.build_context(query="memory platform")

    assert isinstance(context, FormattedContext)
    prompt_str = context.to_prompt_string()

    assert "Always be helpful and concise." in prompt_str
    assert "YasinAI --(created_by)--> Alice" in prompt_str
    assert "YasinAI utilizes a highly optimized localized memory platform." in prompt_str
    assert "User: Who built you?" in prompt_str
    assert "Assistant: I was built by Alice." in prompt_str


def test_cli_memory_search_integration(temp_storage_path):
    # Setup standard MemoryManager to write some dummy long term data
    mgr = MemoryManager(long_term_storage_path=temp_storage_path)
    mgr.persist_to_long_term("secret_project", "Project Pegasus is a highly classified AI project.")
    mgr.persist_to_long_term("common_fact", "This is an unrelated document.")

    # We patch MemoryManager directly where it's defined
    with patch("yasinai.knowledge_platform.manager.MemoryManager", return_value=mgr):
        with patch("sys.stdout") as mock_stdout:
            exit_code = main(["memory", "search", "Pegasus"])
            assert exit_code == 0

            # Extract print outputs
            printed_calls = [call[0][0] for call in mock_stdout.write.call_args_list if call[0]]
            full_output = "".join(printed_calls)

            assert "Searching memory for 'Pegasus'..." in full_output
            assert "Ranked Results:" in full_output
            assert "Project Pegasus" in full_output
