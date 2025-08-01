"""Unit tests for ConversationRepository"""
import pytest
from unittest.mock import Mock, patch, MagicMock

from ignatius.database.repositories.conversation_repository import ConversationRepository
from ignatius.database.repositories.base import RepositoryError
from ignatius.models.conversation import Conversation


class TestConversationRepository:
    """Test cases for ConversationRepository"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.repository = ConversationRepository()
    
    def test_init(self):
        """Test repository initialization"""
        repo = ConversationRepository()
        assert repo.model_class == Conversation
    
    @patch.object(ConversationRepository, 'save')
    def test_create_conversation_success(self, mock_save):
        """Test successful conversation creation"""
        mock_conversation = Mock(spec=Conversation)
        mock_save.return_value = mock_conversation
        
        with patch('ignatius.database.repositories.conversation_repository.Conversation') as mock_conv_class:
            mock_conv_class.return_value = mock_conversation
            
            result = self.repository.create_conversation("Test Topic", "Hello world")
            
            # Verify conversation was created with correct topic
            mock_conv_class.assert_called_once_with(topic="Test Topic")
            
            # Verify message was added
            mock_conversation.add_message.assert_called_once_with("user", "Hello world")
            
            # Verify save was called
            mock_save.assert_called_once_with(mock_conversation)
            
            assert result == mock_conversation
    
    @patch.object(ConversationRepository, 'save')
    def test_create_conversation_save_error(self, mock_save):
        """Test conversation creation with save error"""
        mock_save.side_effect = RepositoryError("Save failed")
        
        with pytest.raises(RepositoryError):
            self.repository.create_conversation("Test Topic", "Hello world")
    
    @patch.object(ConversationRepository, 'get_by_id')
    def test_get_conversation_success(self, mock_get_by_id):
        """Test successful conversation retrieval"""
        mock_conversation = Mock(spec=Conversation)
        mock_get_by_id.return_value = mock_conversation
        
        result = self.repository.get_conversation("test_id")
        
        mock_get_by_id.assert_called_once_with("test_id")
        assert result == mock_conversation
    
    @patch.object(ConversationRepository, 'get_by_id')
    def test_get_conversation_not_found(self, mock_get_by_id):
        """Test conversation retrieval when not found"""
        mock_get_by_id.return_value = None
        
        result = self.repository.get_conversation("nonexistent_id")
        
        assert result is None
    
    @patch.object(ConversationRepository, 'save')
    def test_save_conversation_success(self, mock_save):
        """Test successful conversation save"""
        mock_conversation = Mock(spec=Conversation)
        mock_save.return_value = mock_conversation
        
        result = self.repository.save_conversation(mock_conversation)
        
        mock_save.assert_called_once_with(mock_conversation)
        assert result == mock_conversation
    
    @patch.object(ConversationRepository, 'save')
    def test_save_conversation_error(self, mock_save):
        """Test conversation save with error"""
        mock_conversation = Mock(spec=Conversation)
        mock_save.side_effect = RepositoryError("Save failed")
        
        with pytest.raises(RepositoryError):
            self.repository.save_conversation(mock_conversation)
    
    def test_inheritance(self):
        """Test that ConversationRepository inherits from MongoRepository"""
        from ignatius.database.repositories.base import MongoRepository
        assert isinstance(self.repository, MongoRepository)
    
    def test_model_class_assignment(self):
        """Test that model class is correctly assigned"""
        assert self.repository.model_class == Conversation