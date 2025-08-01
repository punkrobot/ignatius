"""Base repository for database operations"""
from abc import ABC, abstractmethod
from typing import Optional
from mongoengine import Document, ValidationError, DoesNotExist
import logging

logger = logging.getLogger(__name__)


class RepositoryError(Exception):
    """Base exception for repository operations"""
    pass


class BaseRepository(ABC):
    """Abstract base repository with essential operations"""
    
    @abstractmethod
    def save(self, entity: Document) -> Document:
        """Save entity to database"""
        pass
    
    @abstractmethod
    def get_by_id(self, entity_id: str) -> Optional[Document]:
        """Get entity by ID"""
        pass


class MongoRepository(BaseRepository):
    """MongoDB implementation of repository pattern"""
    
    def __init__(self, model_class: type):
        if not issubclass(model_class, Document):
            raise ValueError("Model class must be a MongoEngine Document")
        
        self.model_class = model_class
        self.logger = logging.getLogger(f"{__name__}.{model_class.__name__}")
    
    def save(self, entity: Document) -> Document:
        """Save entity to database"""
        try:
            entity.validate()
            entity.save()
            self.logger.info(f"Saved {self.model_class.__name__} with ID: {entity.id}")
            return entity
            
        except ValidationError as e:
            self.logger.error(f"Validation error saving {self.model_class.__name__}: {e}")
            raise RepositoryError(f"Validation failed: {e}")
        
        except Exception as e:
            self.logger.error(f"Error saving {self.model_class.__name__}: {e}")
            raise RepositoryError(f"Failed to save entity: {e}")
    
    def get_by_id(self, entity_id: str) -> Optional[Document]:
        """Get entity by ID"""
        try:
            entity = self.model_class.objects.get(id=entity_id)
            self.logger.debug(f"Retrieved {self.model_class.__name__} with ID: {entity_id}")
            return entity
            
        except DoesNotExist:
            self.logger.debug(f"{self.model_class.__name__} not found with ID: {entity_id}")
            return None
        
        except Exception as e:
            self.logger.error(f"Error retrieving {self.model_class.__name__} {entity_id}: {e}")
            raise RepositoryError(f"Failed to retrieve entity: {e}")