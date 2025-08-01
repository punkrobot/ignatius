import logging
from bson import ObjectId
from mongoengine import DoesNotExist, ValidationError
from .models import Conversation, Message

logger = logging.getLogger(__name__)

class ConversationNotFoundError(Exception):
    """Raised when a conversation cannot be found"""
    pass

class ConversationService:
    """Service class for handling conversation database operations"""
    
    @staticmethod
    def create_conversation(message: str, topic: str = None) -> Conversation:
        """
        Create a new conversation with an initial user message.
        
        Args:
            message: The initial user message
            topic: Optional topic for the conversation
            
        Returns:
            Conversation: The created conversation instance
            
        Raises:
            ValueError: If message is empty
            ValidationError: If the conversation data is invalid
        """
        if not message or not message.strip():
            raise ValueError("Message cannot be empty")
            
        try:
            user_message = Message(role="user", text=message.strip())
            conversation = Conversation(
                topic=topic or "General Discussion",
                messages=[user_message]
            )
            logger.info("Created new conversation")
            return conversation
            
        except ValidationError as e:
            logger.error(f"Validation error creating conversation: {e}")
            raise
        except Exception as e:
            logger.error(f"Error creating conversation: {e}")
            raise
    
    @staticmethod
    def get_conversation(conversation_id: str, new_message: str = None) -> Conversation:
        """
        Retrieve a conversation by ID and optionally add a new message.
        
        Args:
            conversation_id: The ID of the conversation to retrieve
            new_message: Optional new message to add to the conversation
            
        Returns:
            Conversation: The retrieved conversation instance
            
        Raises:
            ConversationNotFoundError: If the conversation doesn't exist
            ValueError: If conversation_id is invalid
            ValidationError: If the new message is invalid
        """
        if not conversation_id:
            raise ValueError("Conversation ID cannot be empty")
            
        try:
            # Validate ObjectId format
            if not ObjectId.is_valid(conversation_id):
                raise ValueError("Invalid conversation ID format")
                
            conversation = Conversation.objects(id=conversation_id).first()
            if not conversation:
                raise ConversationNotFoundError(f"Conversation with ID {conversation_id} not found")
            
            # Add new message if provided
            if new_message and new_message.strip():
                user_message = Message(role="user", text=new_message.strip())
                conversation.messages = conversation.messages + [user_message]
                logger.info(f"Added new message to conversation {conversation_id}")
            
            return conversation
            
        except (DoesNotExist, ConversationNotFoundError):
            logger.error(f"Conversation {conversation_id} not found")
            raise ConversationNotFoundError(f"Conversation with ID {conversation_id} not found")
        except ValidationError as e:
            logger.error(f"Validation error updating conversation: {e}")
            raise
        except Exception as e:
            logger.error(f"Error retrieving conversation {conversation_id}: {e}")
            raise
    
    @staticmethod
    def save_conversation(conversation: Conversation) -> Conversation:
        """
        Save a conversation to the database.
        
        Args:
            conversation: The conversation instance to save
            
        Returns:
            Conversation: The saved conversation instance
            
        Raises:
            ValidationError: If the conversation data is invalid
        """
        try:
            conversation.save()
            logger.info(f"Saved conversation {conversation.id}")
            return conversation
            
        except ValidationError as e:
            logger.error(f"Validation error saving conversation: {e}")
            raise
        except Exception as e:
            logger.error(f"Error saving conversation: {e}")
            raise
