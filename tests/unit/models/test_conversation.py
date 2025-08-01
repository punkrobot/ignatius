"""Unit tests for Conversation model"""
import pytest
from datetime import datetime
from mongoengine import ValidationError

from ignatius.models.conversation import Conversation
from ignatius.models.message import Message


class TestConversation:
    """Test cases for Conversation model"""
    
    def test_create_conversation(self):
        """Test creating a conversation"""
        conversation = Conversation(topic="Test Topic")
        
        assert conversation.topic == "Test Topic"
        assert len(conversation.messages) == 0
        assert isinstance(conversation.created_at, datetime)
        assert isinstance(conversation.updated_at, datetime)
    
    def test_conversation_validation_valid_topic(self):
        """Test conversation validation with valid topic"""
        conversation = Conversation(topic="Valid Topic")
        conversation.add_message("user", "Hello")
        conversation.validate()  # Should not raise
    
    def test_conversation_validation_empty_topic(self):
        """Test conversation validation with empty topic"""
        with pytest.raises(ValidationError):
            conversation = Conversation(topic="")
            conversation.validate()
    
    def test_conversation_validation_long_topic(self):
        """Test conversation validation with very long topic"""
        long_topic = "x" * 201  # Exceeds MAX_TOPIC_LENGTH
        with pytest.raises(ValidationError):
            conversation = Conversation(topic=long_topic)
            conversation.validate()
    
    def test_add_message(self):
        """Test adding a message to conversation"""
        conversation = Conversation(topic="Test")
        message = conversation.add_message("user", "Hello world")
        
        assert len(conversation.messages) == 1
        assert message.role == "user"
        assert message.text == "Hello world"
        assert conversation.messages[0] == message
    
    def test_add_message_updates_timestamp(self):
        """Test that adding a message updates the conversation timestamp"""
        conversation = Conversation(topic="Test")
        original_updated_at = conversation.updated_at
        
        import time
        time.sleep(0.001)
        
        conversation.add_message("user", "Hello")
        assert conversation.updated_at > original_updated_at
    
    def test_add_multiple_messages(self):
        """Test adding multiple messages"""
        conversation = Conversation(topic="Test")
        
        message1 = conversation.add_message("user", "Hello")
        message2 = conversation.add_message("bot", "Hi there")
        
        assert len(conversation.messages) == 2
        assert conversation.messages[0] == message1
        assert conversation.messages[1] == message2
    
    def test_get_last_user_message(self):
        """Test getting the last user message"""
        conversation = Conversation(topic="Test")
        conversation.add_message("user", "First message")
        conversation.add_message("bot", "Bot response")
        last_user_msg = conversation.add_message("user", "Second message")
        
        result = conversation.get_last_user_message()
        assert result == last_user_msg
        assert result.text == "Second message"
    
    def test_get_last_user_message_none(self):
        """Test getting last user message when none exists"""
        conversation = Conversation(topic="Test")
        conversation.add_message("bot", "Only bot message")
        
        result = conversation.get_last_user_message()
        assert result is None
    
    def test_get_last_bot_message(self):
        """Test getting the last bot message"""
        conversation = Conversation(topic="Test")
        conversation.add_message("user", "User message")
        last_bot_msg = conversation.add_message("bot", "Bot response")
        conversation.add_message("user", "Another user message")
        
        result = conversation.get_last_bot_message()
        assert result == last_bot_msg
        assert result.text == "Bot response"
    
    def test_get_last_bot_message_none(self):
        """Test getting last bot message when none exists"""
        conversation = Conversation(topic="Test")
        conversation.add_message("user", "Only user message")
        
        result = conversation.get_last_bot_message()
        assert result is None
    
    def test_get_user_messages_count(self):
        """Test getting count of user messages"""
        conversation = Conversation(topic="Test")
        conversation.add_message("user", "Message 1")
        conversation.add_message("bot", "Bot response")
        conversation.add_message("user", "Message 2")
        
        user_messages = [msg for msg in conversation.messages if msg.role == "user"]
        assert len(user_messages) == 2
    
    def test_get_bot_messages_count(self):
        """Test getting count of bot messages"""
        conversation = Conversation(topic="Test")
        conversation.add_message("user", "User message")
        conversation.add_message("bot", "Bot response 1")
        conversation.add_message("bot", "Bot response 2")
        
        bot_messages = [msg for msg in conversation.messages if msg.role == "bot"]
        assert len(bot_messages) == 2
    
    def test_to_conversation_string(self):
        """Test conversation string formatting"""
        conversation = Conversation(topic="Test")
        conversation.add_message("user", "Hello")
        conversation.add_message("bot", "Hi there")
        
        result = conversation.to_conversation_string()
        
        assert "user: Hello" in result
        assert "bot: Hi there" in result
    
    def test_to_dict(self):
        """Test conversation serialization to dictionary"""
        conversation = Conversation(topic="Test Topic")
        conversation.add_message("user", "Hello")
        
        result = conversation.to_dict()
        
        assert result["topic"] == "Test Topic"
        assert "messages" in result
        assert len(result["messages"]) == 1
        assert result["messages"][0]["role"] == "user"
        assert result["messages"][0]["text"] == "Hello"
        assert "created_at" in result
        assert "updated_at" in result
        assert "created_at" in result
        assert "updated_at" in result
    
    def test_conversation_clean_strips_topic_whitespace(self):
        """Test that conversation clean method strips topic whitespace"""
        conversation = Conversation(topic="  Test Topic  ")
        conversation.add_message("user", "Hello")  # Need message for validation
        conversation.clean()
        
        assert conversation.topic == "Test Topic"
    
    def test_conversation_str(self):
        """Test conversation string representation"""
        conversation = Conversation(topic="Test Topic")
        str_repr = str(conversation)
        
        assert "Test Topic" in str_repr
        assert "messages=0" in str_repr
    
    def test_conversation_with_messages_str(self):
        """Test conversation string representation with messages"""
        conversation = Conversation(topic="Test")
        conversation.add_message("user", "Hello")
        conversation.add_message("bot", "Hi")
        
        str_repr = str(conversation)
        assert "messages=2" in str_repr
    
    def test_conversation_auto_timestamps(self):
        """Test that timestamps are automatically set"""
        conversation = Conversation(topic="Test")
        
        assert conversation.created_at is not None
        assert conversation.updated_at is not None
        assert isinstance(conversation.created_at, datetime)
        assert isinstance(conversation.updated_at, datetime)
    
    def test_topic_validation_none(self):
        """Test that topic cannot be None"""
        with pytest.raises(ValidationError):
            conversation = Conversation(topic=None)
            conversation.validate()