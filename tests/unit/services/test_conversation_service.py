"""Unit tests for ConversationService"""
import pytest
from unittest.mock import Mock, patch
from mongoengine import ValidationError
from bson import ObjectId

from ignatius.services.conversation_service import ConversationService
from ignatius.services.exceptions import ConversationNotFoundError
from ignatius.database.repositories.base import RepositoryError
from ignatius.models.conversation import Conversation


class TestConversationService:
    """Test cases for ConversationService"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.service = ConversationService()
    
    def test_init(self):
        """Test service initialization"""
        service = ConversationService()
        assert hasattr(service, 'repository')
        from ignatius.database.repositories.conversation_repository import ConversationRepository
        assert isinstance(service.repository, ConversationRepository)
    
    @patch.object(ConversationService, '__init__', lambda x: None)
    def test_create_conversation_success(self):
        """Test successful conversation creation"""
        service = ConversationService()
        service.repository = Mock()
        
        mock_conversation = Mock(spec=Conversation)
        service.repository.create_conversation.return_value = mock_conversation
        
        result = service.create_conversation("Hello world", "Test Topic")
        
        service.repository.create_conversation.assert_called_once_with("Test Topic", "Hello world")
        assert result == mock_conversation
    
    @patch.object(ConversationService, '__init__', lambda x: None)
    def test_create_conversation_no_topic(self):
        """Test conversation creation without topic"""
        service = ConversationService()
        service.repository = Mock()
        
        mock_conversation = Mock(spec=Conversation)
        service.repository.create_conversation.return_value = mock_conversation
        
        message = "This is a test message"
        result = service.create_conversation(message)
        
        # Should call repository with None topic and message
        service.repository.create_conversation.assert_called_once_with(None, message)
    
    @patch.object(ConversationService, '__init__', lambda x: None)
    def test_create_conversation_with_topic(self):
        """Test conversation creation with explicit topic"""
        service = ConversationService()
        service.repository = Mock()
        
        mock_conversation = Mock(spec=Conversation)
        service.repository.create_conversation.return_value = mock_conversation
        
        message = "Short message"
        topic = "Custom Topic"
        result = service.create_conversation(message, topic)
        
        # Should call repository with provided topic
        service.repository.create_conversation.assert_called_once_with(topic, message)
    
    @patch.object(ConversationService, '__init__', lambda x: None)
    def test_create_conversation_empty_message(self):
        """Test conversation creation with empty message"""
        service = ConversationService()
        service.repository = Mock()
        
        with pytest.raises(ValueError, match="Message cannot be empty"):
            service.create_conversation("")
    
    @patch.object(ConversationService, '__init__', lambda x: None)
    def test_create_conversation_whitespace_message(self):
        """Test conversation creation with whitespace-only message"""
        service = ConversationService()
        service.repository = Mock()
        
        with pytest.raises(ValueError, match="Message cannot be empty"):
            service.create_conversation("   ")
    
    @patch.object(ConversationService, '__init__', lambda x: None)
    def test_create_conversation_repository_error(self):
        """Test conversation creation with repository error"""
        service = ConversationService()
        service.repository = Mock()
        
        service.repository.create_conversation.side_effect = RepositoryError("Database error")
        
        with pytest.raises(ValidationError):
            service.create_conversation("Hello world")
    
    @patch.object(ConversationService, '__init__', lambda x: None)
    def test_get_conversation_success(self):
        """Test successful conversation retrieval"""
        service = ConversationService()
        service.repository = Mock()
        
        mock_conversation = Mock(spec=Conversation)
        service.repository.get_conversation.return_value = mock_conversation
        
        with patch('bson.ObjectId.is_valid', return_value=True):
            result = service.get_conversation("507f1f77bcf86cd799439011")
        
        service.repository.get_conversation.assert_called_once_with("507f1f77bcf86cd799439011")
        assert result == mock_conversation
    
    @patch.object(ConversationService, '__init__', lambda x: None)
    def test_get_conversation_with_new_message(self):
        """Test conversation retrieval with new message"""
        service = ConversationService()
        service.repository = Mock()
        
        mock_conversation = Mock(spec=Conversation)
        service.repository.get_conversation.return_value = mock_conversation
        
        with patch('bson.ObjectId.is_valid', return_value=True):
            result = service.get_conversation("507f1f77bcf86cd799439011", "New message")
        
        mock_conversation.add_message.assert_called_once_with("user", "New message")
    
    @patch.object(ConversationService, '__init__', lambda x: None)
    def test_get_conversation_not_found(self):
        """Test conversation retrieval when not found"""
        service = ConversationService()
        service.repository = Mock()
        
        service.repository.get_conversation.return_value = None
        
        with patch('bson.ObjectId.is_valid', return_value=True):
            with pytest.raises(ConversationNotFoundError):
                service.get_conversation("507f1f77bcf86cd799439011")
    
    @patch.object(ConversationService, '__init__', lambda x: None)
    def test_get_conversation_invalid_id_format(self):
        """Test conversation retrieval with invalid ID format"""
        service = ConversationService()
        service.repository = Mock()
        
        with patch('bson.ObjectId.is_valid', return_value=False):
            with pytest.raises(ValueError, match="Invalid conversation ID format"):
                service.get_conversation("invalid_id")
    
    @patch.object(ConversationService, '__init__', lambda x: None)
    def test_get_conversation_empty_id(self):
        """Test conversation retrieval with empty ID"""
        service = ConversationService()
        service.repository = Mock()
        
        with pytest.raises(ValueError, match="Conversation ID cannot be empty"):
            service.get_conversation("")
    
    @patch.object(ConversationService, '__init__', lambda x: None)
    def test_save_conversation_success(self):
        """Test successful conversation save"""
        service = ConversationService()
        service.repository = Mock()
        
        mock_conversation = Mock(spec=Conversation)
        service.repository.save_conversation.return_value = mock_conversation
        
        result = service.save_conversation(mock_conversation)
        
        service.repository.save_conversation.assert_called_once_with(mock_conversation)
        assert result == mock_conversation
    
    @patch.object(ConversationService, '__init__', lambda x: None)
    def test_save_conversation_repository_error(self):
        """Test conversation save with repository error"""
        service = ConversationService()
        service.repository = Mock()
        
        mock_conversation = Mock(spec=Conversation)
        service.repository.save_conversation.side_effect = RepositoryError("Save failed")
        
        with pytest.raises(ValidationError):
            service.save_conversation(mock_conversation)