"""Unit tests for Celery async tasks

This module contains comprehensive tests for the Celery task processing system,
including contract parsing tasks, health checks, and cleanup operations.
"""

import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime

from src.tasks.celery import (
    parse_contract, health_check, cleanup_old_results,
    _calculate_section_confidence, celery_app
)
from src.core.exceptions import ProcessingError, ExtractionError


class TestCeleryTasks:
    """Test cases for Celery task functionality"""

    def setup_method(self):
        """Set up test environment before each test"""
        self.contract_id = "test-contract-123"
        self.sample_extracted_data = {
            "parties": [
                {"name": "Test Company", "role": "Client", "confidence": 90}
            ],
            "financial_details": {
                "total_value": "$100,000",
                "currency": "USD"
            },
            "payment_structure": {
                "terms": "Net 30",
                "method": "Wire Transfer"
            },
            "sla_terms": {
                "response_time": "4 hours",
                "uptime_guarantee": "99.9%"
            },
            "contact_information": {
                "emails": ["test@company.com"]
            },
            "account_information": {
                "account_number": "ACC-123"
            }
        }

    @patch('src.tasks.celery.get_contracts_collection')
    @patch('src.tasks.celery.extractor')
    @patch('src.tasks.celery.calculate_score')
    @patch('src.tasks.celery.identify_gaps')
    def test_parse_contract_success(self, mock_identify_gaps, mock_calculate_score,
                                   mock_extractor, mock_get_collection):
        """Test successful contract parsing task"""
        # Mock database collection
        mock_collection = MagicMock()
        mock_get_collection.return_value = mock_collection

        # Mock contract document
        mock_contract = {
            "contract_id": self.contract_id,
            "original_file": b"fake pdf content",
            "status": "pending"
        }
        mock_collection.find_one.return_value = mock_contract

        # Mock extractor
        mock_extractor.extract_data.return_value = self.sample_extracted_data

        # Mock scoring functions
        mock_calculate_score.return_value = 85
        mock_identify_gaps.return_value = []

        # Execute task
        result = parse_contract(self.contract_id)

        # Verify database operations
        assert mock_collection.find_one.call_count == 1
        assert mock_collection.update_one.call_count == 3  # status updates

        # Verify result
        assert result["status"] == "completed"
        assert result["contract_id"] == self.contract_id
        assert result["score"] == 85
        assert result["gaps_count"] == 0

    @patch('src.tasks.celery.get_contracts_collection')
    def test_parse_contract_not_found(self, mock_get_collection):
        """Test contract parsing when contract is not found"""
        mock_collection = MagicMock()
        mock_get_collection.return_value = mock_collection
        mock_collection.find_one.return_value = None

        with pytest.raises(ProcessingError):
            parse_contract(self.contract_id)

    @patch('src.tasks.celery.get_contracts_collection')
    @patch('src.tasks.celery.extractor')
    def test_parse_contract_extraction_failure(self, mock_extractor, mock_get_collection):
        """Test contract parsing when extraction fails"""
        # Mock database collection
        mock_collection = MagicMock()
        mock_get_collection.return_value = mock_collection

        # Mock contract document
        mock_contract = {
            "contract_id": self.contract_id,
            "original_file": b"fake pdf content",
            "status": "pending"
        }
        mock_collection.find_one.return_value = mock_contract

        # Mock extractor to raise exception
        mock_extractor.extract_data.side_effect = ExtractionError("PDF extraction failed")

        # Execute task and expect it to handle the error gracefully
        result = parse_contract(self.contract_id)

        # Verify error handling
        assert result is not None  # Task should complete (not raise exception)
        # The task should have updated the contract status to failed

    def test_calculate_section_confidence_complete_data(self):
        """Test confidence calculation with complete extracted data"""
        confidence_scores = _calculate_section_confidence(self.sample_extracted_data)

        # Verify all sections have confidence scores
        assert "parties" in confidence_scores
        assert "financial_details" in confidence_scores
        assert "payment_structure" in confidence_scores
        assert "sla_terms" in confidence_scores
        assert "account_information" in confidence_scores

        # Verify confidence values are reasonable
        for section, confidence in confidence_scores.items():
            assert 0 <= confidence <= 100

    def test_calculate_section_confidence_empty_data(self):
        """Test confidence calculation with empty data"""
        confidence_scores = _calculate_section_confidence({})

        # Should return empty dictionary for empty data
        assert confidence_scores == {}

    def test_calculate_section_confidence_partial_data(self):
        """Test confidence calculation with partial data"""
        partial_data = {
            "parties": [{"name": "Test Company", "confidence": 95}],
            "financial_details": {"total_value": "$50,000"}
        }

        confidence_scores = _calculate_section_confidence(partial_data)

        # Should only include sections that exist
        assert "parties" in confidence_scores
        assert "financial_details" in confidence_scores
        assert len(confidence_scores) == 2

    def test_health_check_task(self):
        """Test health check task execution"""
        result = health_check()

        # Verify health check structure
        assert result["status"] == "healthy"
        assert "timestamp" in result
        assert result["worker"] == "contract_parser"

        # Verify timestamp format
        try:
            datetime.fromisoformat(result["timestamp"].replace('Z', '+00:00'))
        except ValueError:
            pytest.fail("Health check timestamp is not in valid ISO format")

    @patch('src.tasks.celery.get_contracts_collection')
    def test_cleanup_old_results_success(self, mock_get_collection):
        """Test successful cleanup of old results"""
        mock_collection = MagicMock()
        mock_get_collection.return_value = mock_collection

        # Mock cleanup operation
        mock_result = MagicMock()
        mock_result.deleted_count = 5
        mock_collection.delete_many.return_value = mock_result

        result = cleanup_old_results()

        # Verify cleanup result
        assert result["status"] == "completed"
        assert result["deleted_count"] == 5
        assert "timestamp" in result

    @patch('src.tasks.celery.get_contracts_collection')
    def test_cleanup_old_results_failure(self, mock_get_collection):
        """Test cleanup task failure handling"""
        mock_collection = MagicMock()
        mock_get_collection.return_value = mock_collection

        # Mock database error
        mock_collection.delete_many.side_effect = Exception("Database connection failed")

        result = cleanup_old_results()

        # Verify error handling
        assert result["status"] == "failed"
        assert "error" in result
        assert "timestamp" in result

    @patch('src.tasks.celery.get_contracts_collection')
    @patch('src.tasks.celery.extractor')
    def test_parse_contract_retry_logic(self, mock_extractor, mock_get_collection):
        """Test retry logic when task fails"""
        # Mock database collection
        mock_collection = MagicMock()
        mock_get_collection.return_value = mock_collection

        # Mock contract document
        mock_contract = {
            "contract_id": self.contract_id,
            "original_file": b"fake pdf content",
            "status": "pending"
        }
        mock_collection.find_one.return_value = mock_contract

        # Mock extractor to always fail
        mock_extractor.extract_data.side_effect = Exception("Persistent extraction error")

        # Create a mock task with retry attributes
        task_mock = MagicMock()
        task_mock.request.retries = 2
        task_mock.max_retries = 3

        # Execute task with retry context
        with patch('src.tasks.celery.parse_contract.request', task_mock.request):
            result = parse_contract(self.contract_id)

        # Task should complete (not raise exception due to retry logic)
        assert result is not None

    def test_celery_app_configuration(self):
        """Test Celery app configuration"""
        # Verify Celery app is properly configured
        assert celery_app.conf['task_serializer'] == 'json'
        assert celery_app.conf['accept_content'] == ['json']
        assert celery_app.conf['result_serializer'] == 'json'
        assert celery_app.conf['enable_utc'] is True
        assert celery_app.conf['task_track_started'] is True

    def test_task_routing(self):
        """Test task routing configuration"""
        # Verify task routing is configured
        routes = celery_app.conf.get('task_routes', {})
        assert 'src.tasks.celery.parse_contract' in routes

    @patch('src.tasks.celery.get_contracts_collection')
    def test_parse_contract_progress_updates(self, mock_get_collection):
        """Test that contract parsing updates progress correctly"""
        mock_collection = MagicMock()
        mock_get_collection.return_value = mock_collection

        # Mock contract document
        mock_contract = {
            "contract_id": self.contract_id,
            "original_file": b"fake pdf content",
            "status": "pending"
        }
        mock_collection.find_one.return_value = mock_contract

        # Mock successful extraction
        with patch('src.tasks.celery.extractor') as mock_extractor:
            mock_extractor.extract_data.return_value = self.sample_extracted_data

            with patch('src.tasks.celery.calculate_score', return_value=85):
                with patch('src.tasks.celery.identify_gaps', return_value=[]):
                    parse_contract(self.contract_id)

        # Verify progress updates were called
        progress_calls = [call for call in mock_collection.update_one.call_args_list
                         if 'progress' in str(call)]
        assert len(progress_calls) >= 3  # At least 3 progress updates


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
