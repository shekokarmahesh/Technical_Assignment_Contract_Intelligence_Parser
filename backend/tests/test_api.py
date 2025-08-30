"""Unit tests for API endpoints

This module provides comprehensive testing for all FastAPI endpoints including:
- Contract upload and validation
- Status tracking and progress monitoring
- Data retrieval with proper error handling
- Pagination and filtering functionality
- File download capabilities
- Statistics and analytics endpoints

Tests cover both success and failure scenarios with proper mocking of
database operations and external dependencies.
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import io

from src.main import app

client = TestClient(app)


class TestContractAPI:
    """Test cases for contract API endpoints"""

    def test_root_endpoint(self):
        """Test root endpoint"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert data["message"] == "Contract Intelligence Parser API"

    def test_health_check(self):
        """Test health check endpoint"""
        response = client.get("/api/v1/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data

    @patch('src.api.routers.get_contracts_collection')
    @patch('src.api.routers.parse_contract')
    def test_upload_contract_success(self, mock_parse_contract, mock_get_collection):
        """Test successful contract upload"""
        # Mock database collection
        mock_collection = MagicMock()
        mock_get_collection.return_value = mock_collection
        
        # Mock celery task
        mock_parse_contract.delay.return_value = MagicMock()
        
        # Create test PDF file
        pdf_content = b'%PDF-1.4\n%Test PDF content\n%%EOF'
        
        # Upload file
        response = client.post(
            "/api/v1/contracts/upload",
            files={"file": ("test.pdf", io.BytesIO(pdf_content), "application/pdf")}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "contract_id" in data
        assert data["filename"] == "test.pdf"
        
        # Verify database insert was called
        mock_collection.insert_one.assert_called_once()
        # Verify celery task was started
        mock_parse_contract.delay.assert_called_once()

    def test_upload_invalid_file_type(self):
        """Test upload with invalid file type"""
        # Create test text file
        txt_content = b'This is not a PDF file'
        
        response = client.post(
            "/api/v1/contracts/upload",
            files={"file": ("test.txt", io.BytesIO(txt_content), "text/plain")}
        )
        
        assert response.status_code == 400
        assert "Only PDF files are supported" in response.json()["detail"]

    def test_upload_empty_file(self):
        """Test upload with empty file"""
        response = client.post(
            "/api/v1/contracts/upload",
            files={"file": ("empty.pdf", io.BytesIO(b''), "application/pdf")}
        )
        
        assert response.status_code == 400
        assert "File is empty" in response.json()["detail"]

    @patch('src.api.routers.get_contracts_collection')
    def test_get_contract_status_found(self, mock_get_collection):
        """Test get contract status - found"""
        mock_collection = MagicMock()
        mock_get_collection.return_value = mock_collection
        
        # Mock contract data
        mock_contract = {
            "contract_id": "test-id",
            "status": "completed",
            "progress": 100,
            "filename": "test.pdf",
            "upload_date": "2024-01-01T00:00:00"
        }
        mock_collection.find_one.return_value = mock_contract
        
        response = client.get("/api/v1/contracts/test-id/status")
        
        assert response.status_code == 200
        data = response.json()
        assert data["contract_id"] == "test-id"
        assert data["status"] == "completed"
        assert data["progress"] == 100

    @patch('src.api.routers.get_contracts_collection')
    def test_get_contract_status_not_found(self, mock_get_collection):
        """Test get contract status - not found"""
        mock_collection = MagicMock()
        mock_get_collection.return_value = mock_collection
        mock_collection.find_one.return_value = None
        
        response = client.get("/api/v1/contracts/nonexistent-id/status")
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]

    @patch('src.api.routers.get_contracts_collection')
    def test_get_contract_data_completed(self, mock_get_collection):
        """Test get contract data - completed"""
        mock_collection = MagicMock()
        mock_get_collection.return_value = mock_collection
        
        # Mock completed contract data
        mock_contract = {
            "contract_id": "test-id",
            "status": "completed",
            "score": 85,
            "extracted_data": {"parties": [{"name": "Test Company"}]},
            "gaps": [],
            "confidence_scores": {"parties": 90}
        }
        mock_collection.find_one.return_value = mock_contract
        
        response = client.get("/api/v1/contracts/test-id")
        
        assert response.status_code == 200
        data = response.json()
        assert data["contract_id"] == "test-id"
        assert data["score"] == 85
        assert "extracted_data" in data

    @patch('src.api.routers.get_contracts_collection')
    def test_get_contract_data_not_completed(self, mock_get_collection):
        """Test get contract data - not completed"""
        mock_collection = MagicMock()
        mock_get_collection.return_value = mock_collection
        
        # Mock processing contract
        mock_contract = {
            "contract_id": "test-id",
            "status": "processing"
        }
        mock_collection.find_one.return_value = mock_contract
        
        response = client.get("/api/v1/contracts/test-id")
        
        assert response.status_code == 400
        assert "not completed" in response.json()["detail"]

    @patch('src.api.routers.get_contracts_collection')
    def test_list_contracts(self, mock_get_collection):
        """Test list contracts"""
        mock_collection = MagicMock()
        mock_get_collection.return_value = mock_collection
        
        # Mock contract list
        mock_contracts = [
            {
                "contract_id": "test-1",
                "filename": "test1.pdf",
                "status": "completed",
                "progress": 100,
                "score": 85,
                "gaps": []
            },
            {
                "contract_id": "test-2",
                "filename": "test2.pdf",
                "status": "processing",
                "progress": 50,
                "gaps": []
            }
        ]
        
        mock_collection.count_documents.return_value = 2
        mock_collection.find.return_value.sort.return_value.skip.return_value.limit.return_value = mock_contracts
        
        response = client.get("/api/v1/contracts")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["contracts"]) == 2
        assert "pagination" in data
        assert data["pagination"]["total_count"] == 2

    @patch('src.api.routers.get_contracts_collection')
    def test_list_contracts_with_status_filter(self, mock_get_collection):
        """Test list contracts with status filter"""
        mock_collection = MagicMock()
        mock_get_collection.return_value = mock_collection
        
        mock_collection.count_documents.return_value = 1
        mock_collection.find.return_value.sort.return_value.skip.return_value.limit.return_value = []
        
        response = client.get("/api/v1/contracts?status=completed")
        
        assert response.status_code == 200
        # Verify the collection was queried with status filter
        mock_collection.find.assert_called_with({"status": "completed"}, {"original_file": 0})

    def test_list_contracts_invalid_status(self):
        """Test list contracts with invalid status filter"""
        response = client.get("/api/v1/contracts?status=invalid")
        
        assert response.status_code == 400
        assert "Invalid status filter" in response.json()["detail"]

    @patch('src.api.routers.get_contracts_collection')
    def test_download_contract_success(self, mock_get_collection):
        """Test download contract - success"""
        mock_collection = MagicMock()
        mock_get_collection.return_value = mock_collection
        
        # Mock contract with file data
        pdf_content = b'%PDF-1.4\nTest PDF content\n%%EOF'
        mock_contract = {
            "contract_id": "test-id",
            "filename": "test.pdf",
            "original_file": pdf_content
        }
        mock_collection.find_one.return_value = mock_contract
        
        response = client.get("/api/v1/contracts/test-id/download")
        
        assert response.status_code == 200
        assert response.headers["content-type"] == "application/pdf"
        assert "attachment" in response.headers["content-disposition"]

    @patch('src.api.routers.get_contracts_collection')
    def test_download_contract_not_found(self, mock_get_collection):
        """Test download contract - not found"""
        mock_collection = MagicMock()
        mock_get_collection.return_value = mock_collection
        mock_collection.find_one.return_value = None
        
        response = client.get("/api/v1/contracts/nonexistent-id/download")
        
        assert response.status_code == 404

    @patch('src.api.routers.get_contracts_collection')
    def test_delete_contract_success(self, mock_get_collection):
        """Test delete contract - success"""
        mock_collection = MagicMock()
        mock_get_collection.return_value = mock_collection
        
        # Mock successful deletion
        mock_result = MagicMock()
        mock_result.deleted_count = 1
        mock_collection.delete_one.return_value = mock_result
        
        response = client.delete("/api/v1/contracts/test-id")
        
        assert response.status_code == 200
        data = response.json()
        assert "deleted successfully" in data["message"]

    @patch('src.api.routers.get_contracts_collection')
    def test_delete_contract_not_found(self, mock_get_collection):
        """Test delete contract - not found"""
        mock_collection = MagicMock()
        mock_get_collection.return_value = mock_collection
        
        # Mock no deletion (not found)
        mock_result = MagicMock()
        mock_result.deleted_count = 0
        mock_collection.delete_one.return_value = mock_result
        
        response = client.delete("/api/v1/contracts/nonexistent-id")
        
        assert response.status_code == 404

    @patch('src.api.routers.get_contracts_collection')
    def test_get_statistics(self, mock_get_collection):
        """Test get contract statistics"""
        mock_collection = MagicMock()
        mock_get_collection.return_value = mock_collection
        
        # Mock statistics data
        mock_collection.count_documents.side_effect = [100, 80]  # total, completed
        mock_collection.aggregate.side_effect = [
            [{"_id": "completed", "count": 80}, {"_id": "processing", "count": 20}],  # status stats
            [{"_id": None, "avg_score": 85.5}]  # average score
        ]
        
        response = client.get("/api/v1/contracts/stats")
        
        assert response.status_code == 200
        data = response.json()
        assert data["total_contracts"] == 100
        assert data["completed_contracts"] == 80
        assert data["completion_rate"] == 80.0
        assert data["average_score"] == 85.5


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
