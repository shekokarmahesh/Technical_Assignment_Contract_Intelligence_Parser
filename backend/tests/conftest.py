"""Shared test fixtures and configuration for pytest

This module provides common test fixtures, mock objects, and test data
that can be used across all test modules in the project.
"""

import pytest
from unittest.mock import MagicMock, patch
from io import BytesIO


@pytest.fixture
def sample_pdf_content():
    """Sample PDF content for testing"""
    return b'%PDF-1.4\n%Test PDF content for contract intelligence\n%%EOF'


@pytest.fixture
def sample_contract_text():
    """Sample contract text for extraction testing"""
    return """
    SERVICE AGREEMENT

    This agreement is between TechCorp Solutions Inc. (Service Provider)
    and Global Industries Ltd. (Client).

    Total Contract Value: $150,000
    Currency: USD
    Tax Rate: 8.5%

    Payment Terms: Net 30 days
    Payment Method: Wire Transfer
    Billing Schedule: Monthly

    Line Items:
    Software Development Services    1    $120,000    $120,000
    Technical Support               12    $2,500      $30,000

    Response Time: 4 hours
    Uptime Guarantee: 99.9%
    Penalty: 5% reduction for < 99% uptime

    Account Number: ACC-2024-001
    Billing Address: 123 Business St, Suite 100, Business City, BC 12345
    Contact Email: billing@techcorp.com
    Technical Contact: support@techcorp.com
    Phone: (555) 123-4567

    This is a recurring monthly service agreement with automatic renewal.
    """


@pytest.fixture
def mock_database_collection():
    """Mock MongoDB collection for testing"""
    collection = MagicMock()
    collection.find_one.return_value = None
    collection.insert_one.return_value = MagicMock(inserted_id="test_id")
    collection.update_one.return_value = MagicMock(modified_count=1)
    collection.delete_one.return_value = MagicMock(deleted_count=1)
    collection.count_documents.return_value = 0
    return collection


@pytest.fixture
def mock_contract_document():
    """Mock contract document for testing"""
    return {
        "contract_id": "test-contract-123",
        "filename": "test_contract.pdf",
        "file_size": 1024000,
        "status": "completed",
        "progress": 100,
        "score": 85,
        "upload_date": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T01:00:00Z",
        "original_file": b'%PDF-1.4\nTest PDF content\n%%EOF',
        "extracted_data": {
            "parties": [{"name": "Test Company", "role": "Client"}],
            "financial_details": {"total_value": "$100,000"}
        },
        "gaps": [],
        "confidence_scores": {"parties": 90},
        "processing_completed_at": "2024-01-01T01:00:00Z"
    }


@pytest.fixture
def mock_pdfplumber():
    """Mock pdfplumber for PDF processing tests"""
    with patch('src.services.extractor.pdfplumber.open') as mock_open:
        mock_pdf = MagicMock()
        mock_page = MagicMock()
        mock_page.extract_text.return_value = "Sample contract text"
        mock_pdf.pages = [mock_page]
        mock_pdf.__enter__ = MagicMock(return_value=mock_pdf)
        mock_pdf.__exit__ = MagicMock(return_value=None)
        mock_open.return_value = mock_pdf
        yield mock_open


@pytest.fixture
def mock_celery_task():
    """Mock Celery task for testing"""
    task = MagicMock()
    task.delay.return_value = MagicMock()
    return task


@pytest.fixture(autouse=True)
def mock_environment_variables():
    """Mock environment variables for consistent testing"""
    env_vars = {
        "MONGO_URI": "mongodb://localhost:27017/test_db",
        "REDIS_HOST": "localhost",
        "REDIS_PORT": "6379",
        "CELERY_BROKER_URL": "redis://localhost:6379/0",
        "CELERY_RESULT_BACKEND": "redis://localhost:6379/0",
        "SECRET_KEY": "test-secret-key",
        "MAX_FILE_SIZE": "52428800",  # 50MB
        "API_V1_STR": "/api/v1"
    }

    with patch.dict('os.environ', env_vars):
        yield


@pytest.fixture
def test_client():
    """Test client for FastAPI testing"""
    from fastapi.testclient import TestClient
    from src.main import app
    return TestClient(app)


# Custom test markers
def pytest_configure(config):
    """Configure custom pytest markers"""
    config.addinivalue_line("markers", "unit: Unit tests")
    config.addinivalue_line("markers", "integration: Integration tests")
    config.addinivalue_line("markers", "slow: Slow running tests")
    config.addinivalue_line("markers", "api: API endpoint tests")
    config.addinivalue_line("markers", "extractor: Data extraction tests")
    config.addinivalue_line("markers", "utils: Utility function tests")
    config.addinivalue_line("markers", "celery: Asynchronous task tests")


# Test data factories
def create_test_contract(overrides=None):
    """Factory function to create test contract data"""
    base_contract = {
        "contract_id": "test-123",
        "filename": "test.pdf",
        "status": "pending",
        "progress": 0,
        "upload_date": "2024-01-01T00:00:00Z",
        "file_size": 1024000
    }

    if overrides:
        base_contract.update(overrides)

    return base_contract


def create_test_extracted_data(overrides=None):
    """Factory function to create test extracted data"""
    base_data = {
        "parties": [{"name": "Test Company", "role": "Client", "confidence": 90}],
        "financial_details": {
            "total_value": "$100,000",
            "currency": "USD",
            "line_items": [{"description": "Service", "total": "$100,000"}]
        },
        "payment_structure": {"terms": "Net 30", "method": "Wire Transfer"},
        "sla_terms": {"response_time": "4 hours", "uptime_guarantee": "99.9%"},
        "contact_information": {"emails": ["test@company.com"]},
        "account_information": {"account_number": "ACC-123"},
        "revenue_classification": {"type": "Recurring", "billing_cycle": "Monthly"}
    }

    if overrides:
        base_data.update(overrides)

    return base_data
