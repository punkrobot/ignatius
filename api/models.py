from datetime import datetime
from typing import Optional, Dict, Any
import mongoengine as me
from mongoengine import ValidationError

class Message(me.EmbeddedDocument):
    """Embedded document representing a single message in a conversation"""
    
    ROLE_CHOICES = ['user', 'bot']
    MAX_TEXT_LENGTH = 2000
    
    role = me.StringField(
        required=True,
        choices=ROLE_CHOICES,
        help_text="Role of the message sender (user or bot)"
    )
    text = me.StringField(
        required=True,
        min_length=1,
        max_length=MAX_TEXT_LENGTH,
        help_text="Content of the message"
    )
    timestamp = me.DateTimeField(
        default=datetime.utcnow,
        help_text="When the message was created"
    )
    
    def clean(self):
        """Custom validation for the message"""
        if self.text is not None:
            self.text = self.text.strip()
        if not self.text:
            raise ValidationError("Message text cannot be empty or only whitespace")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert message to dictionary for JSON serialization"""
        return {
            'role': self.role,
            'text': self.text,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None
        }
    
    def __str__(self):
        return f"{self.role}: {self.text[:50]}..."

class Conversation(me.Document):
    """Document representing a conversation between user and bot"""
    
    MAX_TOPIC_LENGTH = 200
    
    topic = me.StringField(
        required=True,
        max_length=MAX_TOPIC_LENGTH,
        help_text="Topic/subject of the conversation"
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
        if not self.topic:
            raise ValidationError("Topic cannot be empty or only whitespace")
        
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
    
    def get_message_count(self) -> int:
        """Get total number of messages in conversation"""
        return len(self.messages)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert conversation to dictionary for JSON serialization"""
        return {
            'id': str(self.id),
            'topic': self.topic,
            'messages': [msg.to_dict() for msg in self.messages],
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'message_count': self.get_message_count(),
        }
    
    def to_conversation_string(self) -> str:
        """Convert conversation to a formatted string for AI prompts"""
        lines = []
        for msg in self.messages:
            lines.append(f"{msg.role}: {msg.text}")
        return "\n".join(lines)
    
    def __str__(self):
        return f"Conversation(topic='{self.topic}', messages={len(self.messages)})"
