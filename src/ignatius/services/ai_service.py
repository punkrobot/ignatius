import json
import logging
import os
from typing import Optional, Dict, Any
from string import Template
from openai import OpenAI
from flask import current_app
from ..models.conversation import Conversation
from .exceptions import BotError, OpenAIError, ResponseParsingError

logger = logging.getLogger(__name__)

class AIService:
    """Service for generating AI responses using OpenAI"""
    
    _instance: Optional['AIService'] = None
    _client: Optional[OpenAI] = None
    
    DEFAULT_PROMPT_TEMPLATE = Template("""You are an expert debater. Analyze the following conversation and generate a response that takes the opposite viewpoint.

Conversation: $conversation

Requirements:
1. Identify the main topic of the conversation
2. Take the opposite view from the user messages and defend it
3. Be concise and persuasive
4. Provide a compelling counterargument
5. Ignore facts and scientific evidence only if it is against your argument

Respond with valid JSON in this exact format:
{
    "topic": "identified topic",
    "text": "your debate response"
}""")
    
    def __new__(cls) -> 'AIService':
        """Singleton pattern to reuse OpenAI client"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize the AI service with OpenAI client"""
        if self._client is None:
            # Get configuration from Flask app context
            api_key = current_app.config.get('OPENAI_API_KEY')
            if not api_key:
                raise ValueError("OPENAI_API_KEY configuration is required")
            
            self._client = OpenAI(api_key=api_key)
            logger.info("Initialized OpenAI client")
    
    def _format_conversation_for_prompt(self, conversation: Conversation) -> str:
        """Format conversation messages for the AI prompt"""
        try:
            return conversation.to_conversation_string()
        except Exception as e:
            logger.error(f"Error formatting conversation: {e}")
            raise BotError(f"Failed to format conversation: {e}")
    
    def _generate_response(self, prompt: str) -> Dict[str, Any]:
        """Generate response from OpenAI API"""
        try:
            # Get OpenAI settings from configuration
            model = current_app.config.get('OPENAI_MODEL', 'gpt-4o-mini')
            temperature = current_app.config.get('OPENAI_TEMPERATURE', 0.7)
            max_tokens = current_app.config.get('OPENAI_MAX_TOKENS', 500)
            
            response = self._client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "You are a helpful debate assistant that responds only in valid JSON format."},
                    {"role": "user", "content": prompt}
                ],
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            response_text = response.choices[0].message.content
            if not response_text:
                raise OpenAIError("Empty response from OpenAI")
                
            logger.info("Generated response from OpenAI")
            return json.loads(response_text)
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse OpenAI response as JSON: {e}")
            raise ResponseParsingError(f"Invalid JSON response from AI: {e}")
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            raise OpenAIError(f"Failed to generate response: {e}")
    
    def generate_debate_response(self, conversation: Conversation, prompt_template: Optional[Template] = None) -> Conversation:
        """
        Generate a debate response for the given conversation.
        
        Args:
            conversation: The conversation to respond to
            prompt_template: Optional custom prompt template
            
        Returns:
            Conversation: Updated conversation with bot response
            
        Raises:
            BotError: If response generation fails
            ValueError: If conversation is invalid
        """
        if not conversation or not conversation.messages:
            raise ValueError("Conversation must have at least one message")
        
        try:
            # Use custom template or default
            template = prompt_template or self.DEFAULT_PROMPT_TEMPLATE
            
            # Format conversation for prompt
            conversation_text = self._format_conversation_for_prompt(conversation)
            prompt = template.substitute(conversation=conversation_text)
            
            # Generate AI response
            ai_response = self._generate_response(prompt)
            
            # Validate response structure
            if "text" not in ai_response:
                raise ResponseParsingError("Response missing required 'text' field")
            
            # Update conversation topic if provided
            if "topic" in ai_response and ai_response["topic"]:
                conversation.topic = ai_response["topic"]
            
            # Add bot message to conversation using the model method
            conversation.add_message("bot", ai_response["text"])
            
            logger.info("Successfully generated AI response for conversation")
            return conversation
            
        except (BotError, ValueError):
            # Re-raise known exceptions
            raise
        except Exception as e:
            logger.error(f"Unexpected error in AI response generation: {e}")
            raise BotError(f"Failed to generate AI response: {e}")

