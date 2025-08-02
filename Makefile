.PHONY: help install test run down clean

# Default target - show help
help:
	@echo "Available commands:"
	@echo "  make help     - Show this help message"
	@echo "  make install  - Install all requirements to run the service"
	@echo "  make test     - Run tests"
	@echo "  make run      - Run the service and all related services in Docker"
	@echo "  make down     - Teardown all running services"
	@echo "  make clean    - Teardown and remove all containers"

# Check for required tools and install dependencies
install:
	@echo "Checking for required tools..."
	@command -v python3 >/dev/null 2>&1 || { echo "Python 3 is required but not installed. Please install Python 3.13+"; exit 1; }
	@command -v docker >/dev/null 2>&1 || { echo "Docker is required but not installed. Please install Docker from https://docker.com/get-started"; exit 1; }
	@command -v docker-compose >/dev/null 2>&1 || command -v docker compose >/dev/null 2>&1 || { echo "Docker Compose is required but not installed. Please install Docker Compose"; exit 1; }
	@echo "All required tools are available."
	@echo "Creating virtual environment..."
	@python3 -m venv .venv || { echo "Failed to create virtual environment"; exit 1; }
	@echo "Installing Python dependencies..."
	@.venv/bin/pip install -r requirements.txt || { echo "Failed to install dependencies"; exit 1; }
	@.venv/bin/pip install pytest pytest-mock pytest-cov || { echo "Failed to install test dependencies"; exit 1; }
	@echo "Installation complete!"
	@echo "To activate the virtual environment, run: source .venv/bin/activate"

# Run tests
test:
	@echo "Running tests..."
	@if [ ! -d ".venv" ]; then echo "Virtual environment not found. Run 'make install' first."; exit 1; fi
	@.venv/bin/python -m pytest

# Run the service and all related services in Docker
run:
	@echo "Starting services with Docker Compose..."
	@docker compose up --build

# Teardown all running services
down:
	@echo "Stopping all services..."
	@docker compose down

# Teardown and remove all containers
clean:
	@echo "Stopping and removing all containers, networks, and volumes..."
	@docker compose down --volumes --remove-orphans
	@docker system prune -f
	@echo "Cleanup complete!"