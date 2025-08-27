"""Unit tests for core utilities"""

import pytest
from unittest.mock import patch
from datetime import datetime

from src.core.utils import (
    calculate_score, identify_gaps, validate_file, generate_contract_id,
    get_current_timestamp, extract_confidence_score
)
from src.core.exceptions import FileValidationError


class TestCoreUtils:
    """Test cases for core utility functions"""

    def setup_method(self):
        """Set up test data"""
        self.sample_extracted_data = {
            "parties": [
                {"name": "Company A", "role": "Client", "confidence": 90},
                {"name": "Company B", "role": "Service Provider", "confidence": 85}
            ],
            "financial_details": {
                "total_value": "$100,000",
                "currency": "USD",
                "line_items": [{"description": "Service", "total": "$100,000"}],
                "tax_information": {"rate": "10%"}
            },
            "payment_structure": {
                "terms": "Net 30",
                "schedule": "Monthly",
                "method": "Wire Transfer"
            },
            "sla_terms": {
                "response_time": "4 hours",
                "uptime_guarantee": "99.9%",
                "penalties": "5% reduction"
            },
            "contact_information": {
                "billing_contact": "billing@company.com",
                "technical_contact": "support@company.com"
            }
        }

    def test_calculate_score_complete_data(self):
        """Test score calculation with complete data"""
        score = calculate_score(self.sample_extracted_data)
        
        # Should get maximum score (100) for complete data
        assert score == 100
        assert isinstance(score, int)

    def test_calculate_score_partial_data(self):
        """Test score calculation with partial data"""
        partial_data = {
            "financial_details": {
                "total_value": "$100,000",
                "currency": "USD"
            },
            "parties": [{"name": "Company A", "role": "Client"}]
        }
        
        score = calculate_score(partial_data)
        
        # Should get partial score
        assert 0 < score < 100
        assert isinstance(score, int)

    def test_calculate_score_empty_data(self):
        """Test score calculation with empty data"""
        score = calculate_score({})
        
        assert score == 0

    def test_calculate_score_financial_completeness(self):
        """Test financial completeness scoring component"""
        financial_only_data = {
            "financial_details": {
                "total_value": "$100,000",
                "currency": "USD",
                "line_items": [{"description": "Service"}],
                "tax_information": {"rate": "10%"}
            }
        }
        
        score = calculate_score(financial_only_data)
        
        # Should get 30 points for complete financial details
        assert score == 30

    def test_calculate_score_parties_completeness(self):
        """Test parties completeness scoring component"""
        parties_only_data = {
            "parties": [
                {"name": "Company A", "legal_entity": "Inc.", "authorized_signatory": "John Doe"},
                {"name": "Company B", "legal_entity": "LLC", "authorized_signatory": "Jane Smith"}
            ]
        }
        
        score = calculate_score(parties_only_data)
        
        # Should get 25 points for complete party identification
        assert score == 25

    def test_identify_gaps_complete_data(self):
        """Test gap identification with complete data"""
        gaps = identify_gaps(self.sample_extracted_data)
        
        # Complete data should have no gaps
        assert len(gaps) == 0

    def test_identify_gaps_missing_financial(self):
        """Test gap identification with missing financial details"""
        incomplete_data = {
            "parties": [{"name": "Company A"}],
            "payment_structure": {"terms": "Net 30"}
        }
        
        gaps = identify_gaps(incomplete_data)
        
        # Should identify missing financial details
        gap_fields = [gap["field"] for gap in gaps]
        assert "Financial Details" in gap_fields
        
        # Check gap structure
        financial_gap = next(gap for gap in gaps if gap["field"] == "Financial Details")
        assert financial_gap["importance"] == "High"
        assert financial_gap["status"] == "Missing"
        assert "description" in financial_gap

    def test_identify_gaps_incomplete_parties(self):
        """Test gap identification with incomplete parties"""
        incomplete_data = {
            "parties": [{"name": "Company A"}],  # Only one party
            "financial_details": {"total_value": "$100,000"}
        }
        
        gaps = identify_gaps(incomplete_data)
        
        # Should identify incomplete parties
        gap_fields = [gap["field"] for gap in gaps]
        assert "Contract Parties" in gap_fields

    def test_identify_gaps_missing_payment(self):
        """Test gap identification with missing payment terms"""
        incomplete_data = {
            "parties": [{"name": "Company A"}, {"name": "Company B"}],
            "financial_details": {"total_value": "$100,000"}
        }
        
        gaps = identify_gaps(incomplete_data)
        
        # Should identify missing payment terms
        gap_fields = [gap["field"] for gap in gaps]
        assert "Payment Terms" in gap_fields

    def test_identify_gaps_missing_sla(self):
        """Test gap identification with missing SLA terms"""
        incomplete_data = {
            "parties": [{"name": "Company A"}, {"name": "Company B"}],
            "financial_details": {"total_value": "$100,000"},
            "payment_structure": {"terms": "Net 30"}
        }
        
        gaps = identify_gaps(incomplete_data)
        
        # Should identify missing SLA terms
        gap_fields = [gap["field"] for gap in gaps]
        assert "Service Level Agreements" in gap_fields

    def test_validate_file_valid_pdf(self):
        """Test file validation with valid PDF"""
        pdf_content = b'%PDF-1.4\nTest PDF content\n%%EOF'
        filename = "test.pdf"
        max_size = 1000000  # 1MB
        
        # Should not raise exception
        result = validate_file(pdf_content, filename, max_size)
        assert result is True

    def test_validate_file_invalid_extension(self):
        """Test file validation with invalid extension"""
        file_content = b'Some file content'
        filename = "test.txt"
        max_size = 1000000
        
        with pytest.raises(FileValidationError) as exc_info:
            validate_file(file_content, filename, max_size)
        
        assert "Only PDF files are supported" in str(exc_info.value)

    def test_validate_file_too_large(self):
        """Test file validation with file too large"""
        pdf_content = b'%PDF-1.4\n' + b'x' * 1000000  # Large content
        filename = "test.pdf"
        max_size = 500000  # 500KB limit
        
        with pytest.raises(FileValidationError) as exc_info:
            validate_file(pdf_content, filename, max_size)
        
        assert "File size exceeds maximum limit" in str(exc_info.value)

    def test_validate_file_empty(self):
        """Test file validation with empty file"""
        pdf_content = b''
        filename = "test.pdf"
        max_size = 1000000
        
        with pytest.raises(FileValidationError) as exc_info:
            validate_file(pdf_content, filename, max_size)
        
        assert "File is empty" in str(exc_info.value)

    def test_validate_file_invalid_pdf_header(self):
        """Test file validation with invalid PDF header"""
        invalid_content = b'Not a PDF file'
        filename = "test.pdf"
        max_size = 1000000
        
        with pytest.raises(FileValidationError) as exc_info:
            validate_file(invalid_content, filename, max_size)
        
        assert "File is not a valid PDF" in str(exc_info.value)

    def test_generate_contract_id(self):
        """Test contract ID generation"""
        contract_id1 = generate_contract_id()
        contract_id2 = generate_contract_id()
        
        # Should be strings
        assert isinstance(contract_id1, str)
        assert isinstance(contract_id2, str)
        
        # Should be unique
        assert contract_id1 != contract_id2
        
        # Should be UUID format (length check)
        assert len(contract_id1) == 36  # UUID4 string length
        assert len(contract_id2) == 36

    def test_get_current_timestamp(self):
        """Test current timestamp generation"""
        timestamp = get_current_timestamp()
        
        # Should be string
        assert isinstance(timestamp, str)
        
        # Should be valid ISO format
        try:
            parsed_time = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            assert isinstance(parsed_time, datetime)
        except ValueError:
            pytest.fail("Timestamp is not in valid ISO format")

    def test_extract_confidence_score_match_found(self):
        """Test confidence score extraction with matches found"""
        text = "The total amount is $50,000 for this contract."
        pattern = r'\$(\d{1,3}(?:,\d{3})*)'
        field_name = "amount"
        
        result = extract_confidence_score(text, pattern, field_name)
        
        assert result["value"] == "50,000"
        assert result["confidence"] > 0
        assert result["matches_count"] == 1

    def test_extract_confidence_score_no_match(self):
        """Test confidence score extraction with no matches"""
        text = "This text has no dollar amounts."
        pattern = r'\$(\d{1,3}(?:,\d{3})*)'
        field_name = "amount"
        
        result = extract_confidence_score(text, pattern, field_name)
        
        assert result["value"] is None
        assert result["confidence"] == 0
        assert result["matches_count"] == 0

    def test_extract_confidence_score_multiple_matches(self):
        """Test confidence score extraction with multiple matches"""
        text = "Amount 1: $10,000 and Amount 2: $20,000"
        pattern = r'\$(\d{1,3}(?:,\d{3})*)'
        field_name = "amount"
        
        result = extract_confidence_score(text, pattern, field_name)
        
        assert isinstance(result["value"], list)
        assert len(result["value"]) == 2
        assert result["confidence"] > 0
        assert result["matches_count"] == 2

    def test_extract_confidence_score_context_boost(self):
        """Test confidence score gets boost for field name in context"""
        text = "The payment amount is $50,000 for this contract."
        pattern = r'\$(\d{1,3}(?:,\d{3})*)'
        field_name = "payment"
        
        result = extract_confidence_score(text, pattern, field_name)
        
        # Should get confidence boost for field name in context
        assert result["confidence"] > 85  # Base confidence + boost


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
