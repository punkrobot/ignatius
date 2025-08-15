"""Unit tests for AIService"""
import pytest
import json
from unittest.mock import Mock, patch, MagicMock, mock_open
from string import Template

from ignatius.services.ai_service import AIService
from ignatius.services.exceptions import BotError, OpenAIError, ResponseParsingError
from ignatius.models.conversation import Conversation


class TestAIService:
    """Test cases for AIService"""
    
    def setup_method(self):
        """Reset singleton state before each test"""
        AIService._instance = None
        AIService._client = None
        AIService._prompts = None
    
    def test_singleton_pattern(self, app_context):
        """Test that AIService follows singleton pattern"""
        service1 = AIService()
        service2 = AIService()
        
        assert service1 is service2
    
    @patch('ignatius.services.ai_service.yaml.safe_load')
    @patch('builtins.open', new_callable=mock_open)
    @patch('ignatius.services.ai_service.OpenAI')
    def test_init_success(self, mock_openai_class, mock_file, mock_yaml, app_context):
        """Test successful initialization"""
        mock_client = Mock()
        mock_openai_class.return_value = mock_client
        mock_yaml.return_value = {
            'debate': {
                'default': 'Test prompt: $conversation'
            }
        }
        
        service = AIService()
        
        mock_openai_class.assert_called_once_with(api_key="test-api-key")
        assert service._client == mock_client
        assert service._prompts is not None
    
    def test_init_missing_api_key(self, app_context):
        """Test initialization with missing API key"""
        # Reset singleton state to force reinitialization
        AIService._instance = None
        AIService._client = None
        
        with patch('flask.current_app.config') as mock_config:
            mock_config.get.return_value = None
            
            with pytest.raises(ValueError, match="OPENAI_API_KEY configuration is required"):
                AIService()
    
    @patch('ignatius.services.ai_service.yaml.safe_load')
    @patch('builtins.open', new_callable=mock_open)
    @patch('ignatius.services.ai_service.OpenAI')
    def test_format_conversation_for_prompt(self, mock_openai_class, mock_file, mock_yaml, app_context):
        """Test conversation formatting for prompt"""
        mock_yaml.return_value = {'debate': {'default': 'Test prompt: $conversation'}}
        
        service = AIService()
        
        mock_conversation = Mock()
        mock_conversation.to_conversation_string.return_value = "user: Hello\nbot: Hi there"
        
        result = service._format_conversation_for_prompt(mock_conversation)
        
        assert result == "user: Hello\nbot: Hi there"
        mock_conversation.to_conversation_string.assert_called_once()
    
    @patch('ignatius.services.ai_service.yaml.safe_load')
    @patch('builtins.open', new_callable=mock_open)
    @patch('ignatius.services.ai_service.OpenAI')
    def test_format_conversation_error(self, mock_openai_class, mock_file, mock_yaml, app_context):
        """Test conversation formatting with error"""
        mock_yaml.return_value = {'debate': {'default': 'Test prompt: $conversation'}}
        
        service = AIService()
        
        mock_conversation = Mock()
        mock_conversation.to_conversation_string.side_effect = Exception("Format error")
        
        with pytest.raises(BotError, match="Failed to format conversation"):
            service._format_conversation_for_prompt(mock_conversation)
    
    @patch('ignatius.services.ai_service.yaml.safe_load')
    @patch('builtins.open', new_callable=mock_open)
    @patch('ignatius.services.ai_service.OpenAI')
    def test_generate_response_success(self, mock_openai_class, mock_file, mock_yaml, app_context):
        """Test successful response generation"""
        # Config is already set in app_context fixture
        mock_yaml.return_value = {'debate': {'default': 'Test prompt: $conversation'}}
        
        # Setup OpenAI client mock
        mock_client = Mock()
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = '{"topic": "Test", "text": "Response"}'
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai_class.return_value = mock_client
        
        
        service = AIService()
        result = service._generate_response("Test prompt")
        
        assert result == {"topic": "Test", "text": "Response"}
        mock_client.chat.completions.create.assert_called_once()
    
    @patch('ignatius.services.ai_service.yaml.safe_load')
    @patch('builtins.open', new_callable=mock_open)
    @patch('ignatius.services.ai_service.OpenAI')
    def test_generate_response_empty_response(self, mock_openai_class, mock_file, mock_yaml, app_context):
        """Test response generation with empty response"""
        mock_yaml.return_value = {'debate': {'default': 'Test prompt: $conversation'}}
        
        mock_client = Mock()
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = None
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai_class.return_value = mock_client
        
        
        service = AIService()
        
        with pytest.raises(OpenAIError, match="Empty response from OpenAI"):
            service._generate_response("Test prompt")
    
    @patch('ignatius.services.ai_service.yaml.safe_load')
    @patch('builtins.open', new_callable=mock_open)
    @patch('ignatius.services.ai_service.OpenAI')
    def test_generate_response_invalid_json(self, mock_openai_class, mock_file, mock_yaml, app_context):
        """Test response generation with invalid JSON"""
        mock_yaml.return_value = {'debate': {'default': 'Test prompt: $conversation'}}
        
        mock_client = Mock()
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Invalid JSON"
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai_class.return_value = mock_client
        
        
        service = AIService()
        
        with pytest.raises(ResponseParsingError, match="Invalid JSON response from AI"):
            service._generate_response("Test prompt")
    
    @patch('ignatius.services.ai_service.yaml.safe_load')
    @patch('builtins.open', new_callable=mock_open)
    @patch('ignatius.services.ai_service.OpenAI')
    def test_generate_debate_response_success(self, mock_openai_class, mock_file, mock_yaml, app_context):
        """Test successful debate response generation"""
        mock_yaml.return_value = {'debate': {'default': 'Test prompt: $conversation'}}
        
        # Setup mocks
        mock_client = Mock()
        mock_openai_class.return_value = mock_client
        
        
        service = AIService()
        
        # Mock conversation
        mock_conversation = Mock(spec=Conversation)
        mock_conversation.messages = [Mock()]
        mock_conversation.to_conversation_string.return_value = "user: Hello"
        
        # Mock AI response
        with patch.object(service, '_generate_response') as mock_generate:
            mock_generate.return_value = {
                "topic": "Updated Topic",
                "text": "AI response"
            }
            
            result = service.generate_debate_response(mock_conversation)
            
            # Verify topic was updated
            assert mock_conversation.topic == "Updated Topic"
            
            # Verify message was added
            mock_conversation.add_message.assert_called_once_with("bot", "AI response")
            
            assert result == mock_conversation
    
    @patch('ignatius.services.ai_service.yaml.safe_load')
    @patch('builtins.open', new_callable=mock_open)
    @patch('ignatius.services.ai_service.OpenAI')
    def test_generate_debate_response_no_messages(self, mock_openai_class, mock_file, mock_yaml, app_context):
        """Test debate response generation with no messages"""
        mock_yaml.return_value = {'debate': {'default': 'Test prompt: $conversation'}}
        
        service = AIService()
        
        mock_conversation = Mock(spec=Conversation)
        mock_conversation.messages = []
        
        with pytest.raises(ValueError, match="Conversation must have at least one message"):
            service.generate_debate_response(mock_conversation)
    
    @patch('ignatius.services.ai_service.yaml.safe_load')
    @patch('builtins.open', new_callable=mock_open)
    @patch('ignatius.services.ai_service.OpenAI')
    def test_generate_debate_response_missing_text(self, mock_openai_class, mock_file, mock_yaml, app_context):
        """Test debate response generation with missing text in response"""
        mock_yaml.return_value = {'debate': {'default': 'Test prompt: $conversation'}}
        
        service = AIService()
        
        mock_conversation = Mock(spec=Conversation)
        mock_conversation.messages = [Mock()]
        mock_conversation.to_conversation_string.return_value = "user: Hello"
        
        with patch.object(service, '_generate_response') as mock_generate:
            mock_generate.return_value = {"topic": "Test"}  # Missing "text"
            
            with pytest.raises(ResponseParsingError, match="Response missing required 'text' field"):
                service.generate_debate_response(mock_conversation)
    
    @patch('ignatius.services.ai_service.yaml.safe_load')
    @patch('builtins.open', new_callable=mock_open)
    @patch('ignatius.services.ai_service.OpenAI')
    def test_generate_debate_response_custom_template(self, mock_openai_class, mock_file, mock_yaml, app_context):
        """Test debate response generation with custom template"""
        mock_yaml.return_value = {'debate': {'default': 'Test prompt: $conversation'}}
        
        service = AIService()
        
        mock_conversation = Mock(spec=Conversation)
        mock_conversation.messages = [Mock()]
        mock_conversation.to_conversation_string.return_value = "user: Hello"
        
        custom_template = Template("Custom prompt: $conversation")
        
        with patch.object(service, '_generate_response') as mock_generate:
            mock_generate.return_value = {"text": "Custom response"}
            
            service.generate_debate_response(mock_conversation, custom_template)
            
            # Verify custom template was used
            mock_generate.assert_called_once()
            call_args = mock_generate.call_args[0][0]
            assert "Custom prompt:" in call_args
    
    @patch('ignatius.services.ai_service.yaml.safe_load')
    @patch('builtins.open', new_callable=mock_open)
    @patch('ignatius.services.ai_service.OpenAI')
    def test_load_prompts_success(self, mock_openai_class, mock_file, mock_yaml, app_context):
        """Test successful prompt loading from YAML file"""
        mock_prompts = {
            'debate': {
                'default': 'Default prompt: $conversation'
            }
        }
        mock_yaml.return_value = mock_prompts
        
        service = AIService()
        
        assert service._prompts == mock_prompts
        mock_file.assert_called_once()
        mock_yaml.assert_called_once()
    
    @patch('ignatius.services.ai_service.yaml.safe_load')
    @patch('builtins.open', side_effect=FileNotFoundError("File not found"))
    @patch('ignatius.services.ai_service.OpenAI')
    def test_load_prompts_file_not_found(self, mock_openai_class, mock_file, mock_yaml, app_context):
        """Test prompt loading raises error when file not found"""
        with pytest.raises(BotError, match="Failed to load prompts"):
            AIService()
    
    @patch('ignatius.services.ai_service.yaml.safe_load')
    @patch('builtins.open', new_callable=mock_open)
    @patch('ignatius.services.ai_service.OpenAI')
    def test_get_prompt_template_success(self, mock_openai_class, mock_file, mock_yaml, app_context):
        """Test getting prompt template by type and style"""
        mock_prompts = {
            'debate': {
                'default': 'Default prompt: $conversation'
            }
        }
        mock_yaml.return_value = mock_prompts
        
        service = AIService()
        
        # Test default style
        template = service.get_prompt_template('debate', 'default')
        assert template.template == 'Default prompt: $conversation'
        
    
    @patch('ignatius.services.ai_service.yaml.safe_load')
    @patch('builtins.open', new_callable=mock_open)
    @patch('ignatius.services.ai_service.OpenAI')
    def test_get_prompt_template_fallback(self, mock_openai_class, mock_file, mock_yaml, app_context):
        """Test prompt template fallback for unknown type/style"""
        mock_prompts = {
            'debate': {
                'default': 'Default prompt: $conversation'
            }
        }
        mock_yaml.return_value = mock_prompts
        
        service = AIService()
        
        # Test unknown style - should fallback to default
        template = service.get_prompt_template('debate', 'unknown')
        assert template.template == 'Default prompt: $conversation'
        
        # Test unknown type - should fallback to default
        template = service.get_prompt_template('unknown', 'default')
        assert template.template == 'Default prompt: $conversation'
    
    @patch('ignatius.services.ai_service.yaml.safe_load')
    @patch('builtins.open', new_callable=mock_open)
    @patch('ignatius.services.ai_service.OpenAI')
    def test_generate_debate_response_with_style(self, mock_openai_class, mock_file, mock_yaml, app_context):
        """Test debate response generation with different styles"""
        mock_prompts = {
            'debate': {
                'default': 'Default: $conversation'
            }
        }
        mock_yaml.return_value = mock_prompts
        
        service = AIService()
        
        mock_conversation = Mock(spec=Conversation)
        mock_conversation.messages = [Mock()]
        mock_conversation.to_conversation_string.return_value = "user: Hello"
        
        with patch.object(service, '_generate_response') as mock_generate:
            mock_generate.return_value = {"text": "AI response"}
            
            # Test with default style
            service.generate_debate_response(mock_conversation, style='default')
            
            # Verify default template was used
            mock_generate.assert_called_once()
            call_args = mock_generate.call_args[0][0]
            assert "Default:" in call_args