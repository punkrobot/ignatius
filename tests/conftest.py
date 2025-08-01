"""Test configuration and fixtures"""
import pytest
import sys
import os
from unittest.mock import Mock, patch

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from ignatius.app import create_app
from ignatius.models.conversation import Conversation
from ignatius.models.message import Message


@pytest.fixture
def app():
    """Create Flask app for testing"""
    app = create_app('testing')
    return app


@pytest.fixture
def app_context(app):
    """Create Flask app context for testing"""
    with app.app_context():
        yield app


@pytest.fixture
def client(app):
    """Create Flask test client"""
    return app.test_client()


@pytest.fixture
def sample_message():
    """Create sample message for testing"""
    return Message(role="user", text="Hello world")


@pytest.fixture
def sample_conversation():
    """Create sample conversation for testing"""
    conversation = Conversation(topic="Test Topic")
    conversation.add_message("user", "Hello world")
    return conversation


@pytest.fixture
def mock_openai_client():
    """Mock OpenAI client for testing"""
    mock_response = Mock()
    mock_response.choices = [Mock()]
    mock_response.choices[0].message.content = '{"topic": "Test Topic", "text": "This is a test response"}'
    
    mock_client = Mock()
    mock_client.chat.completions.create.return_value = mock_response
    
    with patch('ignatius.services.ai_service.OpenAI', return_value=mock_client):
        yield mock_client


@pytest.fixture
def mock_mongodb():
    """Mock MongoDB operations for testing"""
    with patch('mongoengine.connect'):
        with patch('mongoengine.Document.save'):
            with patch('mongoengine.Document.objects'):
                yield


@pytest.fixture(autouse=True)
def setup_test_environment():
    """Set up test environment variables"""
    test_env = {
        'FLASK_ENV': 'testing',
        'OPENAI_API_KEY': 'test-api-key',
        'MONGODB_DB': 'ignatius_test',
        'SECRET_KEY': 'test-secret-key1'
    }
    
    with patch.dict(os.environ, test_env):
        yield