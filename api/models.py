import mongoengine as me

class Message(me.EmbeddedDocument):
    role = me.StringField()
    text = me.StringField()

class Conversation(me.Document):
    topic = me.StringField()
    messages = me.EmbeddedDocumentListField('Message')
