"""Unit tests for Message model"""
import pytest
from datetime import datetime
from mongoengine import ValidationError

from ignatius.models.message import Message


class TestMessage:
    """Test cases for Message model"""
    
    def test_create_user_message(self):
        """Test creating a user message"""
        message = Message(role="user", text="Hello world")
        
        assert message.role == "user"
        assert message.text == "Hello world"
        assert isinstance(message.timestamp, datetime)
    
    def test_create_bot_message(self):
        """Test creating a bot message"""
        message = Message(role="bot", text="Hello there!")
        
        assert message.role == "bot"
        assert message.text == "Hello there!"
        assert isinstance(message.timestamp, datetime)
    
    def test_message_validation_valid_roles(self):
        """Test message validation with valid roles"""
        user_message = Message(role="user", text="Test")
        bot_message = Message(role="bot", text="Test")
        
        # Should not raise validation errors
        user_message.validate()
        bot_message.validate()
    
    def test_message_validation_invalid_role(self):
        """Test message validation with invalid role"""
        with pytest.raises(ValidationError):
            message = Message(role="invalid", text="Test")
            message.validate()
    
    def test_message_validation_empty_text(self):
        """Test message validation with empty text"""
        with pytest.raises(ValidationError):
            message = Message(role="user", text="")
            message.validate()
    
    def test_message_validation_whitespace_text(self):
        """Test message validation with whitespace-only text"""
        with pytest.raises(ValidationError):
            message = Message(role="user", text="   ")
            message.validate()
    
    def test_message_validation_long_text(self):
        """Test message validation with very long text"""
        long_text = "x" * 5001  # Exceeds MAX_MESSAGE_LENGTH
        with pytest.raises(ValidationError):
            message = Message(role="user", text=long_text)
            message.validate()
    
    def test_message_clean_strips_whitespace(self):
        """Test that message clean method strips whitespace"""
        message = Message(role="user", text="  Hello world  ")
        message.clean()
        
        assert message.text == "Hello world"
    
    def test_message_to_dict(self):
        """Test message serialization to dictionary"""
        message = Message(role="user", text="Hello world")
        result = message.to_dict()
        
        assert result["role"] == "user"
        assert result["text"] == "Hello world"
        assert "timestamp" in result
        assert isinstance(result["timestamp"], str)
    
    def test_message_repr(self):
        """Test message string representation"""
        message = Message(role="user", text="Hello")
        repr_str = repr(message)
        
        assert "user" in repr_str
        assert "Hello" in repr_str
    
    def test_message_timestamp_auto_set(self):
        """Test that timestamp is automatically set"""
        message = Message(role="user", text="Test")
        
        assert message.timestamp is not None
        assert isinstance(message.timestamp, datetime)
    
    def test_message_role_choices(self):
        """Test that only valid role choices are accepted"""
        # Valid roles
        Message(role="user", text="Test").validate()
        Message(role="bot", text="Test").validate()
        
        # Invalid role should raise ValidationError
        with pytest.raises(ValidationError):
            Message(role="admin", text="Test").validate()
    
    def test_message_immutable_timestamp(self):
        """Test that timestamp doesn't change after creation"""
        message = Message(role="user", text="Test")
        original_timestamp = message.timestamp
        
        # Simulate some time passing
        import time
        time.sleep(0.001)
        
        # Timestamp should remain the same
        assert message.timestamp == original_timestamp