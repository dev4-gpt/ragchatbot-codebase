"""
Unit tests for SessionManager — conversation session lifecycle and message history.
"""

import pytest

from session_manager import Message, SessionManager


class TestMessage:
    """Tests for the Message dataclass."""

    def test_message_creation(self):
        msg = Message(role="user", content="Hello")
        assert msg.role == "user"
        assert msg.content == "Hello"

    def test_message_equality(self):
        msg1 = Message(role="user", content="Hello")
        msg2 = Message(role="user", content="Hello")
        assert msg1 == msg2

    def test_message_different_roles(self):
        user = Message(role="user", content="Hi")
        assistant = Message(role="assistant", content="Hi")
        assert user != assistant


class TestSessionManagerCreation:
    """Tests for session creation and initialization."""

    def test_default_max_history(self):
        sm = SessionManager()
        assert sm.max_history == 5

    def test_custom_max_history(self):
        sm = SessionManager(max_history=10)
        assert sm.max_history == 10

    def test_create_session_returns_id(self):
        sm = SessionManager()
        sid = sm.create_session()
        assert sid.startswith("session_")

    def test_create_session_increments_counter(self):
        sm = SessionManager()
        sid1 = sm.create_session()
        sid2 = sm.create_session()
        assert sid1 != sid2
        # Counter should increment
        num1 = int(sid1.split("_")[1])
        num2 = int(sid2.split("_")[1])
        assert num2 == num1 + 1

    def test_create_session_initializes_empty_history(self):
        sm = SessionManager()
        sid = sm.create_session()
        assert sid in sm.sessions
        assert sm.sessions[sid] == []


class TestAddMessage:
    """Tests for adding individual messages."""

    def test_add_user_message(self):
        sm = SessionManager()
        sid = sm.create_session()
        sm.add_message(sid, "user", "Hello")
        assert len(sm.sessions[sid]) == 1
        assert sm.sessions[sid][0].role == "user"
        assert sm.sessions[sid][0].content == "Hello"

    def test_add_assistant_message(self):
        sm = SessionManager()
        sid = sm.create_session()
        sm.add_message(sid, "assistant", "Hi there!")
        assert sm.sessions[sid][0].role == "assistant"

    def test_add_message_to_nonexistent_session_creates_it(self):
        sm = SessionManager()
        sm.add_message("new_session", "user", "Hello")
        assert "new_session" in sm.sessions
        assert len(sm.sessions["new_session"]) == 1

    def test_add_multiple_messages(self):
        sm = SessionManager()
        sid = sm.create_session()
        sm.add_message(sid, "user", "Q1")
        sm.add_message(sid, "assistant", "A1")
        sm.add_message(sid, "user", "Q2")
        assert len(sm.sessions[sid]) == 3

    def test_history_truncation(self):
        """Messages beyond max_history*2 should be pruned."""
        sm = SessionManager(max_history=2)
        sid = sm.create_session()
        # Add 6 messages (exceeds 2*2=4 limit)
        for i in range(6):
            role = "user" if i % 2 == 0 else "assistant"
            sm.add_message(sid, role, f"msg_{i}")
        # Should keep only the last 4 (max_history * 2)
        assert len(sm.sessions[sid]) == 4
        assert sm.sessions[sid][0].content == "msg_2"

    def test_empty_content_is_allowed(self):
        sm = SessionManager()
        sid = sm.create_session()
        sm.add_message(sid, "user", "")
        assert sm.sessions[sid][0].content == ""


class TestAddExchange:
    """Tests for add_exchange (user+assistant pair)."""

    def test_adds_both_messages(self):
        sm = SessionManager()
        sid = sm.create_session()
        sm.add_exchange(sid, "What is RAG?", "RAG stands for...")
        assert len(sm.sessions[sid]) == 2
        assert sm.sessions[sid][0].role == "user"
        assert sm.sessions[sid][1].role == "assistant"

    def test_exchange_preserves_order(self):
        sm = SessionManager()
        sid = sm.create_session()
        sm.add_exchange(sid, "Q1", "A1")
        sm.add_exchange(sid, "Q2", "A2")
        contents = [m.content for m in sm.sessions[sid]]
        assert contents == ["Q1", "A1", "Q2", "A2"]


class TestGetConversationHistory:
    """Tests for retrieving formatted conversation history."""

    def test_returns_none_for_no_session_id(self):
        sm = SessionManager()
        assert sm.get_conversation_history(None) is None

    def test_returns_none_for_unknown_session(self):
        sm = SessionManager()
        assert sm.get_conversation_history("nonexistent") is None

    def test_returns_none_for_empty_session(self):
        sm = SessionManager()
        sid = sm.create_session()
        assert sm.get_conversation_history(sid) is None

    def test_returns_formatted_string(self):
        sm = SessionManager()
        sid = sm.create_session()
        sm.add_exchange(sid, "What is RAG?", "Retrieval Augmented Generation")
        history = sm.get_conversation_history(sid)
        assert "User: What is RAG?" in history
        assert "Assistant: Retrieval Augmented Generation" in history

    def test_multiple_exchanges_in_history(self):
        sm = SessionManager()
        sid = sm.create_session()
        sm.add_exchange(sid, "Q1", "A1")
        sm.add_exchange(sid, "Q2", "A2")
        history = sm.get_conversation_history(sid)
        lines = history.split("\n")
        assert len(lines) == 4


class TestClearSession:
    """Tests for clearing / deleting sessions."""

    def test_clear_existing_session(self):
        sm = SessionManager()
        sid = sm.create_session()
        sm.add_message(sid, "user", "Hi")
        sm.clear_session(sid)
        assert sid not in sm.sessions

    def test_clear_nonexistent_session_no_error(self):
        sm = SessionManager()
        sm.clear_session("does_not_exist")  # Should not raise

    def test_clear_frees_memory(self):
        sm = SessionManager()
        sid = sm.create_session()
        for i in range(100):
            sm.add_message(sid, "user", f"message {i}")
        sm.clear_session(sid)
        assert sid not in sm.sessions


class TestSessionIsolation:
    """Verify sessions don't interfere with each other."""

    def test_messages_isolated_between_sessions(self):
        sm = SessionManager()
        s1 = sm.create_session()
        s2 = sm.create_session()
        sm.add_message(s1, "user", "Session 1 message")
        sm.add_message(s2, "user", "Session 2 message")
        assert len(sm.sessions[s1]) == 1
        assert len(sm.sessions[s2]) == 1
        assert sm.sessions[s1][0].content == "Session 1 message"
        assert sm.sessions[s2][0].content == "Session 2 message"

    def test_clearing_one_session_keeps_others(self):
        sm = SessionManager()
        s1 = sm.create_session()
        s2 = sm.create_session()
        sm.add_message(s1, "user", "keep me")
        sm.add_message(s2, "user", "delete me")
        sm.clear_session(s2)
        assert s1 in sm.sessions
        assert s2 not in sm.sessions
