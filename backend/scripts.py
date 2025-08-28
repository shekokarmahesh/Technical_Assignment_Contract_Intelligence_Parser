#!/usr/bin/env python3
"""Script runner for the contract intelligence backend"""

import subprocess
import sys
import os

def run_command(cmd, description=""):
    """Run a command and handle errors"""
    if description:
        print(f"\n🚀 {description}")
    
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=False)
        return result.returncode == 0
    except subprocess.CalledProcessError as e:
        print(f"❌ Command failed: {cmd}")
        return False

def main():
    if len(sys.argv) < 2:
        print("""
Contract Intelligence Parser - Script Runner

Usage: python scripts.py <command>

Available commands:
  start       - Start the FastAPI server
  celery      - Start the Celery worker
  test        - Run tests with coverage
  format      - Format code with Black
  lint        - Check code with Ruff
  install     - Install dependencies
  docker      - Start with Docker Compose
  """)
        return

    command = sys.argv[1]
    
    commands = {
        "start": ("uv run uvicorn src.main:app --reload --host 0.0.0.0 --port 8000", "Starting FastAPI server..."),
        "celery": ("uv run celery -A src.tasks.celery worker --loglevel=info", "Starting Celery worker..."),
        "test": ("uv run pytest tests/ -v --cov=src --cov-report=term-missing", "Running tests..."),
        "format": ("uv run black src/ tests/", "Formatting code..."),
        "lint": ("uv run ruff check src/ tests/", "Linting code..."),
        "install": ("uv sync", "Installing dependencies..."),
        "docker": ("docker-compose up --build", "Starting with Docker Compose..."),
    }
    
    if command in commands:
        cmd, description = commands[command]
        success = run_command(cmd, description)
        if success:
            print(f"✅ {description} completed successfully")
        else:
            print(f"❌ {description} failed")
            sys.exit(1)
    else:
        print(f"❌ Unknown command: {command}")
        sys.exit(1)

if __name__ == "__main__":
    main()
