# Variables
BACKEND_DIR = backend
FRONTEND_DIR = frontend

# Django commands
.PHONY: migrations
migrations:
	cd $(BACKEND_DIR) && poetry run python manage.py makemigrations

.PHONY: migrate
migrate:
	cd $(BACKEND_DIR) && poetry run python manage.py migrate

# Run commands
.PHONY: run-backend
run-backend:
	cd $(BACKEND_DIR) && poetry run python manage.py runserver

.PHONY: run-frontend
run-frontend:
	cd $(FRONTEND_DIR) && npm start

# Combined commands
.PHONY: run-all
run-all:
	make -j2 run-backend run-frontend

# Setup commands
.PHONY: setup
setup:
	cd $(BACKEND_DIR) && poetry install
	cd $(FRONTEND_DIR) && npm install

# Help command
.PHONY: help
help:
	@echo "Available commands:"
	@echo "  make migrations    - Create new Django migrations"
	@echo "  make migrate       - Apply Django migrations"
	@echo "  make run-backend   - Run Django backend server"
	@echo "  make run-frontend  - Run React frontend server"
	@echo "  make run-all       - Run both backend and frontend servers"
	@echo "  make setup         - Install dependencies for both backend and frontend"
	@echo "  make help          - Show this help message"
