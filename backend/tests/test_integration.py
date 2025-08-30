"""Integration tests for the main FastAPI application

This module provides integration tests that verify the complete application
startup, configuration, and basic functionality without mocking.
"""

import pytest
from fastapi.testclient import TestClient


class TestApplicationStartup:
    """Test application startup and basic functionality"""

    def test_application_creation(self):
        """Test that the FastAPI application can be created"""
        from src.main import app

        assert app is not None
        assert app.title == "Contract Intelligence Parser"
        assert app.version == "1.0.0"

    def test_cors_middleware_configured(self):
        """Test that CORS middleware is properly configured"""
        from src.main import app

        cors_middleware = None
        for middleware in app.user_middleware:
            if hasattr(middleware, 'cls') and 'CORSMiddleware' in str(middleware.cls):
                cors_middleware = middleware
                break

        assert cors_middleware is not None

        # Check CORS options
        options = cors_middleware.options
        assert "http://localhost:3000" in options["allow_origins"]
        assert "http://localhost:5173" in options["allow_origins"]
        assert "http://localhost:8080" in options["allow_origins"]
        assert options["allow_credentials"] is True
        assert options["allow_methods"] == ["*"]
        assert options["allow_headers"] == ["*"]

    def test_router_inclusion(self):
        """Test that API router is properly included"""
        from src.main import app

        # Check that routes are registered
        routes = [route.path for route in app.routes]
        assert "/api/v1/health" in routes
        assert "/api/v1/contracts/upload" in routes
        assert "/api/v1/contracts/{contract_id}/status" in routes

    def test_root_endpoint_integration(self, test_client):
        """Test root endpoint with actual application"""
        response = test_client.get("/")

        assert response.status_code == 200
        data = response.json()

        assert "message" in data
        assert "version" in data
        assert "docs" in data
        assert "health" in data

    def test_health_endpoint_integration(self, test_client):
        """Test health endpoint with actual application"""
        response = test_client.get("/api/v1/health")

        assert response.status_code == 200
        data = response.json()

        assert data["status"] == "healthy"
        assert "timestamp" in data
        assert "service" in data

    def test_favicon_endpoint(self, test_client):
        """Test favicon endpoint"""
        response = test_client.get("/favicon.ico")

        # Should return some response (may be 200 or redirect)
        assert response.status_code in [200, 404]  # 404 is acceptable for missing favicon

    def test_openapi_schema_generation(self):
        """Test that OpenAPI schema can be generated"""
        from src.main import app

        schema = app.openapi()
        assert schema is not None
        assert "openapi" in schema
        assert "info" in schema
        assert "paths" in schema

        # Check that our main endpoints are in the schema
        paths = schema["paths"]
        assert "/api/v1/health" in paths
        assert "/api/v1/contracts/upload" in paths
        assert "/api/v1/contracts/{contract_id}" in paths


class TestApplicationConfiguration:
    """Test application configuration and settings"""

    def test_project_constants(self):
        """Test that project constants are properly defined"""
        from src.core.config import (
            PROJECT_NAME, PROJECT_DESCRIPTION, PROJECT_VERSION,
            API_V1_STR, MAX_FILE_SIZE, ALLOWED_FILE_TYPES
        )

        assert PROJECT_NAME == "Contract Intelligence Parser"
        assert PROJECT_DESCRIPTION is not None
        assert PROJECT_VERSION == "1.0.0"
        assert API_V1_STR == "/api/v1"
        assert MAX_FILE_SIZE == 52428800  # 50MB
        assert ".pdf" in ALLOWED_FILE_TYPES

    def test_scoring_weights_configuration(self):
        """Test that scoring weights are properly configured"""
        from src.core.config import SCORING_WEIGHTS

        required_weights = [
            "financial_completeness",
            "party_identification",
            "payment_terms_clarity",
            "sla_definition",
            "contact_information"
        ]

        for weight in required_weights:
            assert weight in SCORING_WEIGHTS
            assert isinstance(SCORING_WEIGHTS[weight], int)
            assert SCORING_WEIGHTS[weight] > 0

        # Total should be reasonable (not too high or low)
        total_weight = sum(SCORING_WEIGHTS.values())
        assert 80 <= total_weight <= 120


class TestApplicationDependencies:
    """Test application dependencies and imports"""

    def test_core_imports(self):
        """Test that core modules can be imported"""
        try:
            from src.core import config, utils, exceptions
            from src.database import models
            from src.services import extractor
            from src.api import routers
            from src.tasks import celery

            # All imports successful
            assert True
        except ImportError as e:
            pytest.fail(f"Failed to import core modules: {e}")

    def test_database_connection_handling(self):
        """Test database connection handling during startup"""
        from src.database.models import mongodb

        # Should not raise exception even if MongoDB is not available
        try:
            result = mongodb.connect()
            # Result can be None if MongoDB is not available
            assert result is None or hasattr(result, 'name')
        except Exception as e:
            pytest.fail(f"Database connection handling failed: {e}")

    def test_extractor_initialization(self):
        """Test that contract extractor can be initialized"""
        from src.services.extractor import ContractExtractor

        try:
            extractor = ContractExtractor()
            assert extractor is not None
            assert hasattr(extractor, 'currency_patterns')
            assert hasattr(extractor, 'payment_terms_patterns')
            assert hasattr(extractor, 'party_patterns')
            assert len(extractor.currency_patterns) > 0
            assert len(extractor.payment_terms_patterns) > 0
            assert len(extractor.party_patterns) > 0
        except Exception as e:
            pytest.fail(f"Extractor initialization failed: {e}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
