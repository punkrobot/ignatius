"""Custom exceptions for the application"""

class IgnatiusError(Exception):
    """Base exception for all application errors"""
    pass

class ConversationNotFoundError(IgnatiusError):
    """Raised when a conversation cannot be found"""
    pass

class BotError(IgnatiusError):
    """Base exception for bot-related errors"""
    pass

class OpenAIError(BotError):
    """Raised when OpenAI API calls fail"""
    pass

class ResponseParsingError(BotError):
    """Raised when bot response cannot be parsed"""
    pass

class ValidationError(IgnatiusError):
    """Raised when validation fails"""
    pass