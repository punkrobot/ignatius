import logging
from flask import Blueprint, jsonify, request
from mongoengine import ValidationError
from .bot import DebateBotService, BotError, OpenAIError, ResponseParsingError
from .db import ConversationService, ConversationNotFoundError

logger = logging.getLogger(__name__)
bp = Blueprint('api', __name__)

@bp.route('/chat', methods=['POST'])
def chat():
    try:
        # Validate request data
        if not request.is_json:
            return jsonify({"error": "Request must be JSON"}), 400
            
        params = request.get_json()
        if not params:
            return jsonify({"error": "Request body cannot be empty"}), 400
            
        message = params.get("message")
        if not message or not message.strip():
            return jsonify({"error": "Message is required and cannot be empty"}), 400
            
        conversation_id = params.get("conversation_id")
        
        # Create or retrieve conversation
        if conversation_id is None:
            conversation = ConversationService.create_conversation(message)
            logger.info("Created new conversation")
        else:
            conversation = ConversationService.get_conversation(conversation_id, message)
            logger.info(f"Retrieved existing conversation {conversation_id}")

        # Generate bot response
        bot = DebateBotService()
        conversation = bot.respond(conversation)

        # Save conversation
        conversation = ConversationService.save_conversation(conversation)

        return jsonify({
            "conversation_id": str(conversation.id),
            "topic": conversation.topic,
            "messages": [
                {"role": msg.role, "text": msg.text} 
                for msg in conversation.messages
            ]
        })
        
    except ValueError as e:
        logger.warning(f"Validation error: {e}")
        return jsonify({"error": str(e)}), 400
        
    except ConversationNotFoundError as e:
        logger.warning(f"Conversation not found: {e}")
        return jsonify({"error": str(e)}), 404
        
    except ValidationError as e:
        logger.error(f"Database validation error: {e}")
        return jsonify({"error": "Invalid data provided"}), 400
        
    except BotError as e:
        logger.error(f"Bot service error: {e}")
        return jsonify({"error": "Failed to generate response"}), 500
        
    except OpenAIError as e:
        logger.error(f"OpenAI API error: {e}")
        return jsonify({"error": "AI service temporarily unavailable"}), 503
        
    except ResponseParsingError as e:
        logger.error(f"Response parsing error: {e}")
        return jsonify({"error": "Invalid AI response format"}), 500
        
    except Exception as e:
        logger.error(f"Unexpected error in chat endpoint: {e}")
        return jsonify({"error": "Internal server error"}), 500

@bp.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Endpoint not found"}), 404

@bp.errorhandler(405)
def method_not_allowed(error):
    return jsonify({"error": "Method not allowed"}), 405