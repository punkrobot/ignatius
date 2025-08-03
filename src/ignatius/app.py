import os
import logging
from dotenv import load_dotenv
from flask import Flask
from flask_mongoengine import MongoEngine
from flask_cors import CORS
from .api.v1.conversation import conversation_bp
from .config import ConfigFactory

# Load environment variables from .env file
load_dotenv()

def create_app(config_name=None, test_config=None):
    """
    Application factory pattern for Flask app creation
    
    Args:
        config_name: Environment configuration name (development, production, testing)
        test_config: Optional test configuration dictionary
        
    Returns:
        Flask application instance
    """
    app = Flask(__name__, instance_relative_config=True)
    
    # Load configuration
    if test_config is None:
        config = ConfigFactory.create_config(config_name)
        app.config.from_object(config)
        
        # Set MongoDB settings
        app.config["MONGODB_SETTINGS"] = [config.get_mongodb_settings()]
    else:
        # Use test configuration
        app.config.from_mapping(test_config)
    
    # Configure logging
    logging.basicConfig(
        level=getattr(logging, app.config.get('LOG_LEVEL', 'INFO')),
        format=app.config.get('LOG_FORMAT', '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    )
    
    # Initialize MongoDB
    db = MongoEngine()
    db.init_app(app)
    
    # Enable CORS for all domains and routes
    CORS(app)

    # Ensure instance path exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # Register API blueprints
    app.register_blueprint(conversation_bp, url_prefix='/api/v1')

    return app