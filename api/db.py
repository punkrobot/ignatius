from .models import Conversation, Message

class DB:
    def createConversation(self, message):
        conversation = Conversation(topic="test", messages=[ Message(role="user", text=message) ])

        return conversation
    
    def getConversation(self, id, message):
        conversation = Conversation.objects(id=id).first()
        conversation.messages = conversation.messages + [Message(role="user", text=message)]

        return conversation
    
