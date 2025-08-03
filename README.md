# Ignatius

> "My excellence confused them"
> 
>  -- Ignatius J. Reilly 

A very opinionated chat bot API.

## Overview

Ignatius is a Python web application built with Flask and MongoDB that provides REST API endpoints for creating and managing conversations. The chat bot is programmed to take the opposite side from the user and defend its view, no mater how false.

## Quick Start

### Prerequisites

- Python 3.13+
- Docker and Docker Compose
- OpenAI API key

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd ignatius
   ```

2. **Install dependencies**
   ```bash
   make install
   ```

3. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your OpenAI API key and other settings
   ```

4. **Run with Docker**
   ```bash
   make run
   ```

The services will be available at:
- **API**: `http://localhost:5001`
- **Web App**: `http://localhost:8080` (nginx-served frontend)

## Available Commands

```bash
make help     # Show available commands
make install  # Install all requirements
make test     # Run tests
make run      # Run services in Docker
make down     # Stop all services
make clean    # Remove all containers and volumes
```

## API Endpoints

### Conversations

- **POST /api/v1/conversations**
  - Create a new conversation or add a response to an existing conversation
  - Request body: `{"conversation_id": "id" | null, "message": "text"}`

- **GET /api/v1/conversations/{id}**
  - Retrieve a specific conversation by ID
  - Returns full conversation history

## Configuration

The application supports multiple environments:

- **Development**: Debug enabled, relaxed security
- **Production**: For production deployment
- **Testing**: Isolated test environment

### Environment Variables

Key configuration variables:

```bash
# OpenAI
OPENAI_API_KEY=your-openai-api-key
OPENAI_MODEL=gpt-4o-mini
```

## Development

### Local Development

1. **Activate virtual environment**
   ```bash
   source .venv/bin/activate
   ```

2. **Run application locally**
   ```bash
   python -c "
   import sys
   sys.path.insert(0, 'src')
   from ignatius.app import create_app
   app = create_app('development')
   app.run(debug=True)
   "
   ```

### Testing

Run the test suite:

```bash
make test

# Or with coverage
python -m pytest --cov=src/ignatius --cov-report=html
```

### Project Structure

```
src/ignatius/
├── app.py                    # Flask application factory
├── config/                   # Configuration management
│   ├── base.py               # Base configuration
│   ├── development.py        # Development settings
│   ├── production.py         # Production settings
│   ├── testing.py            # Test settings
│   ├── factory.py            # Configuration factory
│   └── validation.py         # Configuration validation
├── api/v1/                   # API endpoints
│   └── conversation.py       # Conversation routes
├── services/                 # Business logic
│   ├── conversation_service.py
│   ├── ai_service.py
│   └── exceptions.py
├── database/repositories/    # Data access layer
│   ├── base.py
│   └── conversation_repository.py
└── models/                   # Data models
    ├── conversation.py
    └── message.py
```
