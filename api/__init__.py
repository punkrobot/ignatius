import os
from dotenv import load_dotenv

from flask import Flask
from flask_mongoengine import MongoEngine
from .routes import bp

load_dotenv()

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    
    app.config['DEBUG'] = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    app.config['ENV'] = os.getenv('FLASK_ENV', 'production')
    
    mongodb_host = os.getenv('MONGODB_HOST', 'localhost')
    mongodb_port = int(os.getenv('MONGODB_PORT', '27017'))
    mongodb_db = os.getenv('MONGODB_DB', 'test')
    
    app.config["MONGODB_SETTINGS"] = [
        {
            "db": mongodb_db,
            "host": mongodb_host,
            "port": mongodb_port,
            "alias": "default",
        }
    ]

    db = MongoEngine()
    db.init_app(app)

    if test_config is None:
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.from_mapping(test_config)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # Register blueprints
    app.register_blueprint(bp)

    return app
