"""Sample test data fixtures"""

SAMPLE_CONVERSATIONS = [
    {
        "topic": "Climate Change Discussion",
        "messages": [
            {"role": "user", "text": "I think climate change is a serious issue that needs immediate action."},
            {"role": "bot", "text": "While environmental concerns are valid, economic impacts of rapid changes could be devastating for many communities."},
            {"role": "user", "text": "But the long-term economic costs of inaction far outweigh short-term adjustments."}
        ]
    },
    {
        "topic": "Technology and Privacy",
        "messages": [
            {"role": "user", "text": "Social media companies should be regulated more strictly regarding privacy."},
            {"role": "bot", "text": "Heavy regulation could stifle innovation and limit the beneficial services these platforms provide."}
        ]
    }
]

SAMPLE_MESSAGES = [
    {"role": "user", "text": "Hello, I'd like to discuss artificial intelligence."},
    {"role": "bot", "text": "While AI has potential benefits, we should be cautious about rapid development without proper safeguards."},
    {"role": "user", "text": "I believe AI will solve many of humanity's greatest challenges."},
    {"role": "bot", "text": "That optimism might be misplaced - AI could exacerbate inequality and job displacement issues."}
]

OPENAI_RESPONSES = [
    {
        "valid": {
            "topic": "AI Ethics",
            "text": "While artificial intelligence shows promise, we must consider the ethical implications and potential for misuse."
        }
    },
    {
        "invalid_json": "This is not valid JSON response",
    },
    {
        "missing_text": {
            "topic": "Incomplete Response"
            # Missing "text" field
        }
    }
]

CONFIG_EXAMPLES = {
    "valid_development": {
        "OPENAI_API_KEY": "sk-test-key-12345",
        "OPENAI_MODEL": "gpt-4o-mini",
        "OPENAI_TEMPERATURE": 0.7,
        "OPENAI_MAX_TOKENS": 500,
        "FLASK_ENV": "development",
        "FLASK_DEBUG": True,
        "SECRET_KEY": "development-secret-key",
        "MONGODB_HOST": "localhost",
        "MONGODB_PORT": 27017,
        "MONGODB_DB": "ignatius_dev",
        "LOG_LEVEL": "DEBUG"
    },
    "valid_production": {
        "OPENAI_API_KEY": "sk-prod-key-67890",
        "OPENAI_MODEL": "gpt-4o-mini",
        "FLASK_ENV": "production",
        "FLASK_DEBUG": False,
        "SECRET_KEY": "secure-production-secret-key-12345",
        "MONGODB_HOST": "prod-mongodb.example.com",
        "MONGODB_PORT": 27017,
        "MONGODB_DB": "ignatius_prod",
        "MONGODB_USERNAME": "prod_user",
        "MONGODB_PASSWORD": "secure_password",
        "LOG_LEVEL": "WARNING"
    },
    "invalid_config": {
        "OPENAI_API_KEY": "",  # Empty
        "OPENAI_TEMPERATURE": 3.0,  # Too high
        "SECRET_KEY": "short",  # Too short
        "MONGODB_PORT": 70000,  # Invalid port
        "LOG_LEVEL": "INVALID"  # Invalid level
    }
}