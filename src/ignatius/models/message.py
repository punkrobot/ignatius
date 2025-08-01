from datetime import datetime
from typing import Dict, Any
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