"""Unit tests for contract extraction services"""

import pytest
from unittest.mock import patch, MagicMock
from io import BytesIO

from src.services.extractor import ContractExtractor
from src.core.exceptions import ExtractionError


class TestContractExtractor:
    """Test cases for contract extraction functionality"""

    def setup_method(self):
        """Set up test cases"""
        self.extractor = ContractExtractor()
        self.sample_contract_text = """
        SERVICE AGREEMENT
        
        This agreement is between TechCorp Solutions Inc. (Service Provider) 
        and Global Industries Ltd. (Client).
        
        Total Contract Value: $150,000
        Currency: USD
        Tax Rate: 8.5%
        
        Payment Terms: Net 30 days
        Payment Method: Wire Transfer
        
        Line Items:
        Software Development Services    1    $120,000    $120,000
        Technical Support               12    $2,500      $30,000
        
        Response Time: 4 hours
        Uptime Guarantee: 99.9%
        Penalty: 5% reduction for < 99% uptime
        
        Account Number: ACC-2024-001
        Contact Email: billing@techcorp.com
        
        This is a recurring monthly service agreement.
        """

    @patch('src.services.extractor.pdfplumber.open')
    def test_extract_text_from_pdf_success(self, mock_pdfplumber):
        """Test successful text extraction from PDF"""
        # Mock pdfplumber
        mock_pdf = MagicMock()
        mock_page = MagicMock()
        mock_page.extract_text.return_value = self.sample_contract_text
        mock_pdf.pages = [mock_page]
        mock_pdf.__enter__ = MagicMock(return_value=mock_pdf)
        mock_pdf.__exit__ = MagicMock(return_value=None)
        mock_pdfplumber.return_value = mock_pdf
        
        # Test extraction
        file_bytes = b'%PDF-1.4\nTest content\n%%EOF'
        text = self.extractor._extract_text_from_pdf(file_bytes)
        
        assert text == self.sample_contract_text
        mock_pdfplumber.assert_called_once()

    @patch('src.services.extractor.pdfplumber.open')
    def test_extract_text_from_pdf_failure(self, mock_pdfplumber):
        """Test PDF extraction failure"""
        # Mock pdfplumber to raise exception
        mock_pdfplumber.side_effect = Exception("PDF parsing failed")
        
        file_bytes = b'%PDF-1.4\nTest content\n%%EOF'
        
        with pytest.raises(ExtractionError):
            self.extractor._extract_text_from_pdf(file_bytes)

    def test_extract_parties(self):
        """Test party extraction"""
        parties = self.extractor._extract_parties(self.sample_contract_text)
        
        assert len(parties) >= 2
        party_names = [p["name"] for p in parties]
        assert "TechCorp Solutions Inc." in party_names
        assert "Global Industries Ltd." in party_names
        
        # Check roles
        for party in parties:
            assert party["role"] in ["Service Provider", "Client", "Party"]
            assert "confidence" in party
            assert 0 <= party["confidence"] <= 100

    def test_extract_financial_details(self):
        """Test financial details extraction"""
        financial = self.extractor._extract_financial_details(self.sample_contract_text)
        
        # Check total value
        assert financial.get("total_value") == "$150,000"
        assert "total_value_confidence" in financial
        
        # Check currency
        assert financial.get("currency") == "USD"
        
        # Check line items
        line_items = financial.get("line_items", [])
        assert len(line_items) >= 2
        
        # Check first line item
        item = line_items[0]
        assert item["description"] == "Software Development Services"
        assert item["quantity"] == 1
        assert item["unit_price"] == "$120,000"
        assert item["total"] == "$120,000"

    def test_extract_payment_structure(self):
        """Test payment structure extraction"""
        payment = self.extractor._extract_payment_structure(self.sample_contract_text)
        
        assert payment.get("terms") == "Net 30"
        assert "terms_confidence" in payment
        assert payment.get("method") == "Wire Transfer"

    def test_extract_sla_terms(self):
        """Test SLA terms extraction"""
        sla = self.extractor._extract_sla_terms(self.sample_contract_text)
        
        assert sla.get("response_time") == "4 hours"
        assert sla.get("uptime_guarantee") == "99.9%"
        assert "5%" in sla.get("penalties", "")

    def test_extract_contact_information(self):
        """Test contact information extraction"""
        contact = self.extractor._extract_contact_information(self.sample_contract_text)
        
        assert "emails" in contact
        assert "billing@techcorp.com" in contact["emails"]

    def test_extract_account_information(self):
        """Test account information extraction"""
        account = self.extractor._extract_account_information(self.sample_contract_text)
        
        assert account.get("account_number") == "ACC-2024-001"
        assert "account_confidence" in account

    def test_extract_revenue_classification(self):
        """Test revenue classification extraction"""
        revenue = self.extractor._extract_revenue_classification(self.sample_contract_text)
        
        assert revenue.get("type") == "Recurring"
        assert revenue.get("billing_cycle") == "Monthly"

    @patch.object(ContractExtractor, '_extract_text_from_pdf')
    def test_extract_data_full_flow(self, mock_extract_text):
        """Test full data extraction flow"""
        mock_extract_text.return_value = self.sample_contract_text
        
        file_bytes = b'%PDF-1.4\nTest content\n%%EOF'
        result = self.extractor.extract_data(file_bytes)
        
        # Check all sections are present
        assert "parties" in result
        assert "financial_details" in result
        assert "payment_structure" in result
        assert "sla_terms" in result
        assert "contact_information" in result
        assert "account_information" in result
        assert "revenue_classification" in result
        assert "extraction_metadata" in result
        
        # Check metadata
        metadata = result["extraction_metadata"]
        assert "extraction_method" in metadata
        assert "text_length" in metadata

    @patch.object(ContractExtractor, '_extract_text_from_pdf')
    def test_extract_data_insufficient_text(self, mock_extract_text):
        """Test extraction with insufficient text content"""
        mock_extract_text.return_value = "Short text"
        
        file_bytes = b'%PDF-1.4\nTest content\n%%EOF'
        
        with pytest.raises(ExtractionError):
            self.extractor.extract_data(file_bytes)

    def test_determine_party_role_client(self):
        """Test party role determination - client"""
        party_name = "Global Industries Ltd."
        role = self.extractor._determine_party_role(self.sample_contract_text, party_name)
        assert role == "Client"

    def test_determine_party_role_service_provider(self):
        """Test party role determination - service provider"""
        party_name = "TechCorp Solutions Inc."
        role = self.extractor._determine_party_role(self.sample_contract_text, party_name)
        assert role == "Service Provider"

    def test_extract_total_value_found(self):
        """Test total value extraction when present"""
        result = self.extractor._extract_total_value(self.sample_contract_text)
        
        assert result is not None
        assert result["value"] == "$150,000"
        assert result["confidence"] > 0

    def test_extract_total_value_not_found(self):
        """Test total value extraction when not present"""
        text_without_value = "This contract has no total value mentioned."
        result = self.extractor._extract_total_value(text_without_value)
        
        assert result is None

    def test_extract_currency_usd(self):
        """Test currency extraction - USD"""
        currency = self.extractor._extract_currency(self.sample_contract_text)
        assert currency == "USD"

    def test_extract_currency_eur(self):
        """Test currency extraction - EUR"""
        eur_text = "Total amount: €50,000 EUR"
        currency = self.extractor._extract_currency(eur_text)
        assert currency == "EUR"

    def test_extract_currency_not_found(self):
        """Test currency extraction when not found"""
        text_without_currency = "This contract has no currency mentioned."
        currency = self.extractor._extract_currency(text_without_currency)
        assert currency is None

    @patch('src.services.extractor.pdfplumber.open')
    def test_count_pages(self, mock_pdfplumber):
        """Test page counting"""
        mock_pdf = MagicMock()
        mock_pdf.pages = [MagicMock(), MagicMock()]  # 2 pages
        mock_pdf.__enter__ = MagicMock(return_value=mock_pdf)
        mock_pdf.__exit__ = MagicMock(return_value=None)
        mock_pdfplumber.return_value = mock_pdf
        
        file_bytes = b'%PDF-1.4\nTest content\n%%EOF'
        page_count = self.extractor._count_pages(file_bytes)
        
        assert page_count == 2

    def test_extract_line_items_multiple(self):
        """Test line items extraction with multiple items"""
        line_items = self.extractor._extract_line_items(self.sample_contract_text)
        
        assert len(line_items) >= 2
        
        # Check structure of first item
        item = line_items[0]
        assert "description" in item
        assert "quantity" in item
        assert "unit_price" in item
        assert "total" in item
        assert isinstance(item["quantity"], int)

    def test_extract_tax_information_found(self):
        """Test tax information extraction when present"""
        tax_info = self.extractor._extract_tax_information(self.sample_contract_text)
        
        assert tax_info is not None
        assert tax_info["rate"] == "8.5%"
        assert tax_info["confidence"] > 0

    def test_extract_tax_information_not_found(self):
        """Test tax information extraction when not present"""
        text_without_tax = "This contract has no tax information."
        tax_info = self.extractor._extract_tax_information(text_without_tax)
        
        assert tax_info is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
