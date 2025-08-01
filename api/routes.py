import logging
from flask import Blueprint, jsonify, request
from .bot import Bot
from .db import DB

logger = logging.getLogger(__name__)
bp = Blueprint('api', __name__)

@bp.route('/chat', methods=['POST'])
def chat():
    params = request.get_json(force=True)

    if params["conversation_id"] == None:
        c = DB().createConversation(params["message"])
    else: 
        c = DB().getConversation(params["conversation_id"], params["message"])

    conversation = Bot().respond(c)

    conversation.save()

    return jsonify(conversation)

@bp.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Endpoint not found"}), 404

@bp.errorhandler(405)
def method_not_allowed(error):
    return jsonify({"error": "Method not allowed"}), 405