from datetime import datetime
from typing import List, Optional, Dict, Any
import mongoengine as me
from mongoengine import ValidationError
from .message import Message

class Conversation(me.Document):
    """Document representing a conversation between user and bot"""
    
    MAX_TOPIC_LENGTH = 200
    
    topic = me.StringField(
        max_length=MAX_TOPIC_LENGTH,
        help_text="Topic/subject of the conversation"
    )
    viewpoint = me.StringField(
        max_length=MAX_TOPIC_LENGTH,
        help_text="Bot's viewpoint/side of the debate"
    )
    messages = me.EmbeddedDocumentListField(
        Message,
        required=True,
        help_text="List of messages in the conversation"
    )
    created_at = me.DateTimeField(
        default=datetime.utcnow,
        help_text="When the conversation was created"
    )
    updated_at = me.DateTimeField(
        default=datetime.utcnow,
        help_text="When the conversation was last updated"
    )
    
    meta = {
        'collection': 'conversations',
        'indexes': [
            'created_at',
            'updated_at',
            'topic'
        ],
        'ordering': ['-updated_at']
    }
    
    def clean(self):
        """Custom validation for the conversation"""
        if self.topic is not None:
            self.topic = self.topic.strip()
        
        if self.viewpoint is not None:
            self.viewpoint = self.viewpoint.strip()
        
        if not self.messages:
            raise ValidationError("Conversation must have at least one message")
        
        # Update timestamp on save
        self.updated_at = datetime.utcnow()
    
    def add_message(self, role: str, text: str) -> Message:
        """
        Add a new message to the conversation
        
        Args:
            role: Role of the message sender ('user' or 'bot')
            text: Content of the message
            
        Returns:
            Message: The created message
            
        Raises:
            ValidationError: If role or text is invalid
        """
        if role not in Message.ROLE_CHOICES:
            raise ValidationError(f"Invalid role: {role}. Must be one of {Message.ROLE_CHOICES}")
        
        message = Message(role=role, text=text)
        message.clean()  # Validate the message
        
        self.messages.append(message)
        self.updated_at = datetime.utcnow()
        
        return message
    
    def get_last_user_message(self) -> Optional[Message]:
        """Get the most recent user message"""
        for message in reversed(self.messages):
            if message.role == 'user':
                return message
        return None
    
    def get_last_bot_message(self) -> Optional[Message]:
        """Get the most recent bot message"""
        for message in reversed(self.messages):
            if message.role == 'bot':
                return message
        return None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert conversation to dictionary for JSON serialization"""
        return {
            'id': str(self.id),
            'topic': self.topic,
            'viewpoint': self.viewpoint,
            'messages': [msg.to_dict() for msg in self.messages],
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
    
    def to_conversation_string(self) -> str:
        """Convert conversation to a formatted string for AI prompts"""
        lines = []
        for msg in self.messages:
            lines.append(f"{msg.role}: {msg.text}")
        return "\n".join(lines)
    
    def __str__(self):
        return f"Conversation(topic='{self.topic}', viewpoint='{self.viewpoint}', messages={len(self.messages)})"