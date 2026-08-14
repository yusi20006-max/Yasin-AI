"""
Unit Tests for YasinAI Knowledge Platform.
Covers Memory, Knowledge Graph, Semantic Search, Context Engine, and Reasoning.
"""

import time
import pytest
from knowledge_platform.memory import ShortTermMemory, LongTermMemory, MemoryManager
from knowledge_platform.entity import Entity
from knowledge_platform.relation import Relation
from knowledge_platform.triple_store import TripleStore
from knowledge_platform.query_engine import QueryEngine
from knowledge_platform.graph import KnowledgeGraph
from knowledge_platform.semantic_search import EmbeddingEngine, VectorStore, SemanticSearch, Retriever
from knowledge_platform.context import ConversationMemory, ContextBuilder, ReasoningEngine
from knowledge_platform.reasoning import KnowledgeReasoner, RuleEngine


# --- Memory Tests ---

def test_short_term_memory_lifecycle():
    stm = ShortTermMemory(capacity=3)

    e1 = stm.store("first msg", {"user": "alice"})
    e2 = stm.store("second msg", {"user": "bob"})
    e3 = stm.store("third msg")

    assert len(stm.memory) == 3
    assert stm.memory[0]["content"] == "first msg"

    # Check eviction (FIFO)
    e4 = stm.store("fourth msg")
    assert len(stm.memory) == 3
    assert "first msg" not in [m["content"] for m in stm.memory]
    assert stm.memory[0]["content"] == "second msg"

    # Retrieve sorted (timestamp descending)
    retrieved = stm.retrieve(limit=2)
    assert len(retrieved) == 2
    assert retrieved[0]["content"] == "fourth msg"
    assert retrieved[1]["content"] == "third msg"

    stm.clear()
    assert len(stm.memory) == 0


def test_long_term_memory_lifecycle():
    ltm = LongTermMemory()

    ltm.store("rules_1", "Always wear security key.", {"type": "policy"})
    ltm.store("api_key_spec", "Store keys encrypted.", {"module": "security"})

    assert len(ltm.list_all()) == 2

    entry = ltm.retrieve("rules_1")
    assert entry is not None
    assert entry["content"] == "Always wear security key."
    assert entry["metadata"]["type"] == "policy"

    assert ltm.delete("rules_1") is True
    assert ltm.retrieve("rules_1") is None
    assert ltm.delete("nonexistent") is False

    ltm.clear()
    assert len(ltm.list_all()) == 0


def test_memory_manager_orchestration():
    mgr = MemoryManager()

    mgr.add_short_term("short conversation info")
    mgr.add_long_term("concept_1", "long-term persistent concept specification")

    assert len(mgr.get_short_term()) == 1
    assert mgr.get_long_term("concept_1")["content"] == "long-term persistent concept specification"

    # Consolidation
    mgr.consolidate_short_to_long("consolidated_key", index=0, metadata={"source": "agent"})

    consolidated = mgr.get_long_term("consolidated_key")
    assert consolidated is not None
    assert consolidated["content"] == "short conversation info"
    assert consolidated["metadata"]["source"] == "agent"
    assert "consolidated_at" in consolidated["metadata"]

    mgr.clear_all()
    assert len(mgr.get_short_term()) == 0
    assert mgr.get_long_term("consolidated_key") is None


# --- Knowledge Graph Tests ---

def test_entity_properties():
    ent = Entity("YasinAI", "Platform", {"version": "1.0.0"})
    assert ent.name == "YasinAI"
    assert ent.entity_type == "Platform"
    assert ent.get_property("version") == "1.0.0"
    assert ent.get_property("unknown", "default") == "default"

    ent.set_property("author", "Developer")
    assert ent.get_property("author") == "Developer"


def test_triple_store_queries():
    store = TripleStore()

    store.add_triple("YasinAI", "created_by", "Developer")
    store.add_triple("YasinAI", "has_module", "Core Runtime")
    store.add_triple("Developer", "uses", "Python")

    assert len(store.list_all()) == 3

    # Specific queries
    res = store.query_triples(subject="YasinAI")
    assert len(res) == 2
    assert ("YasinAI", "created_by", "Developer") in res
    assert ("YasinAI", "has_module", "Core Runtime") in res

    res_wildcard = store.query_triples(predicate="uses")
    assert res_wildcard == [("Developer", "uses", "Python")]

    # Remove triple
    assert store.remove_triple("Developer", "uses", "Python") is True
    assert len(store.query_triples(predicate="uses")) == 0
    assert store.remove_triple("Developer", "uses", "Python") is False


def test_knowledge_graph_and_pathfinding():
    graph = KnowledgeGraph()

    graph.add_triple("A", "connects_to", "B")
    graph.add_triple("B", "connects_to", "C")
    graph.add_triple("C", "connects_to", "D")

    # Get Entity and Relation definitions
    assert graph.get_entity("A") is not None
    assert graph.get_relation("connects_to") is not None

    # Verify pathfinding
    path = graph.find_path("A", "D")
    assert path is not None
    assert len(path) == 3
    assert path == [("connects_to", "B"), ("connects_to", "C"), ("connects_to", "D")]

    # Pathfinding cycle or nonexistent path
    assert graph.find_path("A", "Z") is None

    # Delete entity clears triples
    assert graph.delete_entity("B") is True
    assert graph.get_entity("B") is None
    assert len(graph.query(subject="A")) == 0
    assert len(graph.query(obj="C")) == 0


# --- Semantic Search Tests ---

def test_embedding_and_similarity():
    engine = EmbeddingEngine()

    corpus = [
        "YasinAI configuration loading rules.",
        "How to register custom modules in Core Runtime.",
        "Security platform and identity management specs."
    ]
    engine.fit(corpus)

    assert "configuration" in engine.vocabulary
    assert "security" in engine.vocabulary

    vec1 = engine.get_embedding("configuration rules")
    vec2 = engine.get_embedding("YasinAI configuration rules")
    vec3 = engine.get_embedding("Security specs")

    # Cosine similarities
    search = SemanticSearch()
    sim_similar = search.cosine_similarity(vec1, vec2)
    sim_different = search.cosine_similarity(vec1, vec3)

    # Similarity to self is ~1.0
    assert search.cosine_similarity(vec1, vec1) == pytest.approx(1.0, rel=1e-5)
    # Vec1 and Vec2 should have high overlap, Vec1 and Vec3 have none
    assert sim_similar > 0.5
    assert sim_different == 0.0
    assert sim_similar > sim_different


def test_retriever_pipeline():
    retriever = Retriever()

    retriever.add_document("doc1", "YasinAI configuration loading rules.", {"topic": "core"})
    retriever.add_document("doc2", "How to register custom modules in Core Runtime.", {"topic": "core"})
    retriever.add_document("doc3", "Security platform and identity management specs.", {"topic": "security"})

    # Search core
    res_core = retriever.retrieve("configuration", limit=2)
    assert len(res_core) > 0
    assert res_core[0]["id"] == "doc1"
    assert res_core[0]["metadata"]["topic"] == "core"

    # Search security with threshold
    res_sec = retriever.retrieve("security platform", threshold=0.5)
    assert len(res_sec) >= 1
    assert res_sec[0]["id"] == "doc3"


# --- Context Engine Tests ---

def test_context_engine_generation():
    conv_mem = ConversationMemory()
    conv_mem.add_message("user", "Hello assistant!")
    conv_mem.add_message("assistant", "Hi there, how can I help you today?")

    builder = ContextBuilder()
    context_str = builder.build_context(
        user_input="How do I configure Core Runtime?",
        chat_history=conv_mem.get_history(),
        retrieved_knowledge=["YasinAI configuration loading rules.", "Keep configurations secure."]
    )

    assert "Hello assistant!" in context_str
    assert "How do I configure Core Runtime?" in context_str
    assert "YasinAI configuration loading rules." in context_str
    assert "System Prompt:" in context_str


def test_reasoning_refinement():
    engine = ReasoningEngine()
    raw_context = "This is raw AI assistant context."
    rules = ["Only return secure responses.", "Do not expose master credentials."]

    refined = engine.evaluate_and_refine(raw_context, rules)
    assert "raw AI assistant context" in refined
    assert "Only return secure responses." in refined
    assert "Do not expose master credentials." in refined


# --- Reasoning and Rule Engine Tests ---

def test_rule_engine():
    rule_engine = RuleEngine()

    # Condition: string is longer than 5 chars
    # Action: return upper-cased string
    rule_engine.add_rule(
        name="uppercase_long_words",
        condition=lambda s: isinstance(s, str) and len(s) > 5,
        action=lambda s: s.upper()
    )

    rule_engine.add_rule(
        name="no_numbers",
        condition=lambda x: isinstance(x, int) and x < 0,
        action=lambda x: abs(x)
    )

    res1 = rule_engine.evaluate("hello") # length 5, should not trigger
    assert len(res1) == 0

    res2 = rule_engine.evaluate("yasinai") # length 7, should trigger
    assert len(res2) == 1
    assert res2[0]["rule_name"] == "uppercase_long_words"
    assert res2[0]["result"] == "YASINAI"

    res3 = rule_engine.evaluate(-99)
    assert len(res3) == 1
    assert res3[0]["rule_name"] == "no_numbers"
    assert res3[0]["result"] == 99


def test_knowledge_reasoner_deductions():
    graph = KnowledgeGraph()
    reasoner = KnowledgeReasoner(graph)

    # Test transitive relations: part_of
    graph.add_triple("Engine", "part_of", "Core")
    graph.add_triple("Core", "part_of", "YasinAI")
    graph.add_triple("YasinAI", "part_of", "Ecosystem")

    deduced = reasoner.deduce_transitive_relations("Engine", "part_of")
    assert "Core" in deduced
    assert "YasinAI" in deduced
    assert "Ecosystem" in deduced

    # Test symmetric relations: sibling_of / partner_of
    graph.add_triple("ModuleA", "partner_of", "ModuleB")

    symmetric_deductions = reasoner.deduce_symmetric_relations("partner_of", "partner_of")
    assert len(symmetric_deductions) == 1
    assert symmetric_deductions[0] == ("ModuleB", "partner_of", "ModuleA")


def test_additional_knowledge_platform_coverage():
    # 1. ConversationMemory.get_formatted_history & clear
    conv_mem = ConversationMemory()
    conv_mem.add_message("user", "Hello")
    assert conv_mem.get_formatted_history() == "User: Hello"
    conv_mem.clear()
    assert conv_mem.get_history() == []

    # 2. ReasoningEngine empty rules
    engine = ReasoningEngine()
    assert engine.evaluate_and_refine("raw", []) == "raw"

    # 3. Entity and Relation __repr__
    ent = Entity("TestName", "TestType")
    assert repr(ent) == "Entity(name='TestName', type='TestType')"
    rel = Relation("TestRel")
    assert repr(rel) == "Relation(name='TestRel')"

    # 4. KnowledgeGraph add existing entity/relation, delete non-existent, clear
    graph = KnowledgeGraph()
    graph.add_entity("E1", "Type1", {"p1": "v1"})
    # Adding again with new properties
    e_updated = graph.add_entity("E1", "Type1", {"p2": "v2"})
    assert e_updated.get_property("p2") == "v2"
    assert e_updated.get_property("p1") == "v1"

    graph.add_relation("R1", "Desc1", {"p1": "v1"})
    # Adding again
    r_updated = graph.add_relation("R1", "Desc2", {"p2": "v2"})
    assert r_updated.description == "Desc2"
    assert r_updated.properties["p2"] == "v2"

    assert graph.delete_entity("nonexistent") is False
    graph.clear()
    assert len(graph.entities) == 0

    # 5. MemoryManager delete_long_term, consolidate_short_to_long out of bounds
    mgr = MemoryManager()
    mgr.add_long_term("k1", "content1")
    assert mgr.delete_long_term("k1") is True
    assert mgr.delete_long_term("nonexistent") is False
    assert mgr.consolidate_short_to_long("new_k", 99) is None

    # 6. RuleEngine exceptions
    rule_engine = RuleEngine()
    def broken_condition(x):
        raise ValueError("Broken")
    rule_engine.add_rule("broken", broken_condition, lambda x: x)
    # This should not raise but log error and return empty triggered results
    res = rule_engine.evaluate("some_facts")
    assert res == []

    # 7. EmbeddingEngine empty/missing fit and get_embedding empty token/vocab
    emb = EmbeddingEngine()
    emb.fit([])
    assert emb.get_embedding("hello") == [0.0]
    emb.fit(["hello"])
    assert emb.get_embedding("") == [0.0]

    # 8. SemanticSearch cosine_similarity edge cases
    search = SemanticSearch()
    assert search.cosine_similarity([], []) == 0.0
    assert search.cosine_similarity([1.0], [2.0, 3.0]) == 0.0
    assert search.cosine_similarity([0.0], [0.0]) == 0.0

    # 9. Retriever.clear and empty query search
    retriever = Retriever(store=VectorStore())
    retriever.add_document("mem_001", "text1")
    retriever.add_document("mem_002", "text2")
    # Empty query retrieval
    empty_results = retriever.retrieve("", threshold=0.0)
    assert len(empty_results) == 2
    # Empty query retrieval with high threshold
    empty_results_high = retriever.retrieve("", threshold=0.9)
    assert len(empty_results_high) == 2

    retriever.clear()
    assert len(retriever.vector_store.records) == 0

    # 10. TripleStore existing triple, clear
    store = TripleStore()
    store.add_triple("A", "B", "C")
    store.add_triple("A", "B", "C") # duplicate
    assert len(store.list_all()) == 1
    store.clear()
    assert len(store.list_all()) == 0
