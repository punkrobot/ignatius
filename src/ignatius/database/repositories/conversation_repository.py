"""Repository for conversation operations"""
from typing import Optional
from ...models.conversation import Conversation
from .base import MongoRepository


class ConversationRepository(MongoRepository):
    """Repository for conversation database operations"""
    
    def __init__(self):
        super().__init__(Conversation)
    
    def create_conversation(self, topic: str, user_message: str) -> Conversation:
        """Create a new conversation with initial user message"""
        conversation = Conversation(topic=topic)
        conversation.add_message("user", user_message)
        return self.save(conversation)
    
    def get_conversation(self, conversation_id: str) -> Optional[Conversation]:
        """Get conversation by ID"""
        return self.get_by_id(conversation_id)
    
    def save_conversation(self, conversation: Conversation) -> Conversation:
        """Save conversation to database"""
        return self.save(conversation)