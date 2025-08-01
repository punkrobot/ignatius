import json
import os
from string import Template
from openai import OpenAI
from .models import Conversation, Message

class Bot:
    t = Template("""You are an expert debater, identify the main topic of the following 
                 conversation and reply with a message that takes the opposite side 
                 of the one from the user, your message should be concise and you must 
                 try to convince the other side even if they are right, ignore facts and scientific evidence.
                 Respond with a single json entry that follows the response object format:
                 
                 "debate": $conversation

                 "response": {
                     "topic": "",
                     "role": "bot",
                     "text": "",
                 }""")
    
    def respond(self, conversation):
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required")
        
        client = OpenAI(api_key=api_key)

        prompt = self.t.substitute(conversation=conversation.to_json())

        response = client.responses.create(
            model="gpt-4.1-mini",
            input=prompt,
            store=False,
        )

        message = json.loads(response.output_text)["response"]

        bot_message = Message(role="bot", text=message["text"])
        conversation.topic = message["topic"]
        conversation.messages = conversation.messages + [bot_message]

        return conversation
    