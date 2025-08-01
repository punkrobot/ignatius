"""Unit tests for base repository"""
import pytest
from unittest.mock import Mock, patch
from mongoengine import Document, ValidationError, DoesNotExist

from ignatius.database.repositories.base import (
    BaseRepository, 
    MongoRepository, 
    RepositoryError
)


class MockDocument(Document):
    """Mock document class for testing"""
    meta = {'collection': 'test_collection'}
    
    def validate(self):
        pass
    
    def save(self):
        self.id = "test_id"
        return self


class TestBaseRepository:
    """Test cases for BaseRepository abstract class"""
    
    def test_base_repository_is_abstract(self):
        """Test that BaseRepository cannot be instantiated directly"""
        with pytest.raises(TypeError):
            BaseRepository()


class TestMongoRepository:
    """Test cases for MongoRepository implementation"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.repository = MongoRepository(MockDocument)
    
    def test_init_valid_document_class(self):
        """Test repository initialization with valid document class"""
        repo = MongoRepository(MockDocument)
        assert repo.model_class == MockDocument
    
    def test_init_invalid_document_class(self):
        """Test repository initialization with invalid document class"""
        with pytest.raises(ValueError, match="Model class must be a MongoEngine Document"):
            MongoRepository(str)  # Not a Document class
    
    @patch.object(MockDocument, 'save')
    @patch.object(MockDocument, 'validate')
    def test_save_success(self, mock_validate, mock_save):
        """Test successful save operation"""
        entity = MockDocument()
        entity.id = "test_id"
        mock_save.return_value = entity
        
        result = self.repository.save(entity)
        
        mock_validate.assert_called_once()
        mock_save.assert_called_once()
        assert result == entity
    
    @patch.object(MockDocument, 'validate')
    def test_save_validation_error(self, mock_validate):
        """Test save operation with validation error"""
        entity = MockDocument()
        mock_validate.side_effect = ValidationError("Validation failed")
        
        with pytest.raises(RepositoryError, match="Validation failed"):
            self.repository.save(entity)
    
    @patch.object(MockDocument, 'save')
    @patch.object(MockDocument, 'validate')
    def test_save_generic_error(self, mock_validate, mock_save):
        """Test save operation with generic error"""
        entity = MockDocument()
        mock_save.side_effect = Exception("Database error")
        
        with pytest.raises(RepositoryError, match="Failed to save entity"):
            self.repository.save(entity)
    
    def test_get_by_id_success(self):
        """Test successful get by ID operation"""
        entity = MockDocument()
        entity.id = "test_id"
        
        with patch.object(MockDocument, 'objects') as mock_objects:
            mock_objects.get.return_value = entity
            
            result = self.repository.get_by_id("test_id")
            
            mock_objects.get.assert_called_once_with(id="test_id")
            assert result == entity
    
    def test_get_by_id_not_found(self):
        """Test get by ID when entity not found"""
        with patch.object(MockDocument, 'objects') as mock_objects:
            mock_objects.get.side_effect = DoesNotExist()
            
            result = self.repository.get_by_id("nonexistent_id")
            
            assert result is None
    
    def test_get_by_id_generic_error(self):
        """Test get by ID with generic error"""
        with patch.object(MockDocument, 'objects') as mock_objects:
            mock_objects.get.side_effect = Exception("Database error")
            
            with pytest.raises(RepositoryError, match="Failed to retrieve entity"):
                self.repository.get_by_id("test_id")
    
    def test_logger_name(self):
        """Test that repository logger has correct name"""
        repo = MongoRepository(MockDocument)
        assert "MockDocument" in repo.logger.name