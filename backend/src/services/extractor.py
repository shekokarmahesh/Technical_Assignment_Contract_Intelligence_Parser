"""PDF extraction and contract data parsing services

This module provides intelligent extraction of structured data from contract PDF documents.
It uses advanced regex patterns and text analysis to identify key contract elements including:

- Contract parties and their roles
- Financial details (values, currencies, line items)
- Payment terms and structures
- Service Level Agreements (SLAs)
- Contact information and account details
- Revenue classification

The extraction process leverages confidence scoring to assess the reliability of
identified information and provides comprehensive metadata about the extraction process.
"""

import pdfplumber
import re
from io import BytesIO
from typing import Dict, List, Any, Optional
import logging
from src.core.utils import extract_confidence_score
from src.core.exceptions import ExtractionError

logger = logging.getLogger(__name__)


class ContractExtractor:
    """Main class for extracting data from contract PDFs

    This class implements sophisticated pattern matching and text analysis
    to extract structured contract intelligence from PDF documents. It uses
    multiple regex patterns for different contract elements and provides
    confidence scoring for extracted data.

    Attributes:
        currency_patterns (List[str]): Regex patterns for currency detection
        payment_terms_patterns (List[str]): Patterns for payment terms extraction
        party_patterns (List[str]): Patterns for identifying contract parties
    """

    def __init__(self):
        """Initialize the ContractExtractor with predefined regex patterns

        Sets up comprehensive regex patterns for various contract elements
        including currencies, payment terms, and party identification.
        """
        # Currency detection patterns - supports USD, EUR, GBP formats
        self.currency_patterns = [
            r'\$\s*(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)',  # USD format: $1,000.00
            r'USD\s*(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)',  # USD explicit: USD 1000
            r'€\s*(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)',   # EUR format: €1.000,00
            r'£\s*(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)',   # GBP format: £1,000.00
        ]

        # Payment terms patterns - identifies net payment periods
        self.payment_terms_patterns = [
            r'Net\s*(\d+)\s*days?',           # "Net 30 days"
            r'(\d+)\s*days?\s*net',           # "30 days net"
            r'Payment\s*due\s*in\s*(\d+)\s*days?',  # "Payment due in 30 days"
            r'Terms?\s*:\s*Net\s*(\d+)',      # "Terms: Net 30"
        ]

        # Party identification patterns - finds company names and roles
        self.party_patterns = [
            r'(?:Party|Contractor|Vendor|Client|Customer)[\s:]+([A-Z][^,\n\.]+(?:Inc\.|LLC|Ltd\.|Corp\.)?)',
            r'([A-Z][A-Za-z\s]+(?:Inc\.|LLC|Ltd\.|Corp\.|Company))',
            r'between\s+([A-Z][^,\n]+?)(?:\s+and|\s*,)',
        ]
        
    def extract_data(self, file_bytes: bytes) -> Dict[str, Any]:
        """Extract structured data from PDF contract

        Main entry point for contract data extraction. This method orchestrates
        the entire extraction process including text extraction, pattern matching,
        and data structuring.

        Args:
            file_bytes: Binary PDF data to process

        Returns:
            Dictionary containing extracted contract data with the following structure:
            {
                "parties": List of contract parties with roles and confidence scores,
                "financial_details": Contract values, currencies, and line items,
                "payment_structure": Payment terms, schedules, and methods,
                "sla_terms": Service level agreements and penalties,
                "contact_information": Email addresses and phone numbers,
                "account_information": Account numbers and billing addresses,
                "revenue_classification": Recurring/one-time classification,
                "raw_text_length": Total characters extracted,
                "extraction_metadata": Processing statistics and method info
            }

        Raises:
            ExtractionError: If PDF processing fails or content is insufficient
        """
        try:
            # Step 1: Extract raw text from PDF
            text = self._extract_text_from_pdf(file_bytes)

            # Validate minimum content requirements
            if not text or len(text.strip()) < 100:
                raise ExtractionError("PDF contains insufficient text content")

            # Step 2: Extract different contract components using specialized methods
            extracted_data = {
                "parties": self._extract_parties(text),
                "financial_details": self._extract_financial_details(text),
                "payment_structure": self._extract_payment_structure(text),
                "sla_terms": self._extract_sla_terms(text),
                "contact_information": self._extract_contact_information(text),
                "account_information": self._extract_account_information(text),
                "revenue_classification": self._extract_revenue_classification(text),
                "raw_text_length": len(text),
                "extraction_metadata": {
                    "total_pages": self._count_pages(file_bytes),
                    "extraction_method": "pdfplumber + regex",
                    "text_length": len(text)
                }
            }

            logger.info(f"Successfully extracted data from contract. Text length: {len(text)} chars")
            return extracted_data

        except Exception as e:
            logger.error(f"Contract extraction failed: {str(e)}")
            raise ExtractionError(f"Failed to extract contract data: {str(e)}")
    
    def _extract_text_from_pdf(self, file_bytes: bytes) -> str:
        """Extract text from PDF using pdfplumber

        Uses the pdfplumber library to extract readable text from PDF documents.
        This method handles multi-page documents and concatenates text from all pages.

        Args:
            file_bytes: Binary PDF data

        Returns:
            Extracted text content as a single string

        Raises:
            ExtractionError: If PDF parsing fails
        """
        try:
            with pdfplumber.open(BytesIO(file_bytes)) as pdf:
                text_parts = []
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text_parts.append(page_text)

                full_text = "\n".join(text_parts)
                return full_text

        except Exception as e:
            raise ExtractionError(f"Failed to extract text from PDF: {str(e)}")

    def _count_pages(self, file_bytes: bytes) -> int:
        """Count pages in PDF document

        Args:
            file_bytes: Binary PDF data

        Returns:
            Number of pages in the PDF, or 0 if counting fails
        """
        try:
            with pdfplumber.open(BytesIO(file_bytes)) as pdf:
                return len(pdf.pages)
        except:
            return 0
    
    def _extract_parties(self, text: str) -> List[Dict[str, Any]]:
        """Extract contract parties from text

        Identifies companies and individuals mentioned as parties to the contract.
        Uses multiple regex patterns to find party names and determines their roles
        based on context analysis.

        Args:
            text: Full contract text

        Returns:
            List of party dictionaries with name, role, legal entity, and confidence
        """
        parties = []

        for pattern in self.party_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE | re.MULTILINE)
            for match in matches:
                party_name = match.strip()
                if len(party_name) > 3 and party_name not in [p["name"] for p in parties]:

                    # Determine party role based on context
                    role = self._determine_party_role(text, party_name)

                    # Extract additional party details
                    legal_entity = self._extract_legal_entity_details(text, party_name)

                    # Calculate confidence score for this extraction
                    confidence = extract_confidence_score(text, re.escape(party_name), "party")

                    parties.append({
                        "name": party_name,
                        "role": role,
                        "legal_entity": legal_entity,
                        "confidence": confidence["confidence"]
                    })

        return parties[:4]  # Limit to 4 parties max to avoid duplicates

    def _determine_party_role(self, text: str, party_name: str) -> str:
        """Determine the role of a party in the contract

        Analyzes the context around a party name to determine if they are
        a client, service provider, partner, or general party.

        Args:
            text: Full contract text
            party_name: Name of the party to analyze

        Returns:
            Role classification: "Client", "Service Provider", "Partner", or "Party"
        """
        party_context = re.search(f".{{0,100}}{re.escape(party_name)}.{{0,100}}", text, re.IGNORECASE)

        if party_context:
            context = party_context.group().lower()
            if any(word in context for word in ['client', 'customer', 'buyer', 'purchaser']):
                return "Client"
            elif any(word in context for word in ['vendor', 'supplier', 'contractor', 'service provider']):
                return "Service Provider"
            elif any(word in context for word in ['partner', 'joint venture']):
                return "Partner"

        return "Party"

    def _extract_legal_entity_details(self, text: str, party_name: str) -> Optional[str]:
        """Extract legal entity information for a party

        Looks for legal entity suffixes like Inc., LLC, Corp. associated with the party.

        Args:
            text: Full contract text
            party_name: Name of the party

        Returns:
            Legal entity type (e.g., "Inc.", "LLC") or None if not found
        """
        entity_pattern = rf"{re.escape(party_name)}[^,\n\.]*?(Inc\.|LLC|Ltd\.|Corp\.|Company|Corporation)"
        match = re.search(entity_pattern, text, re.IGNORECASE)

        return match.group(1) if match else None
    
    def _extract_financial_details(self, text: str) -> Dict[str, Any]:
        """Extract financial information from contract

        Comprehensive extraction of all financial aspects including contract values,
        currencies, line items, and tax information.

        Args:
            text: Full contract text

        Returns:
            Dictionary containing financial details with confidence scores
        """
        financial_details = {}

        # Extract total contract value
        total_value = self._extract_total_value(text)
        if total_value:
            financial_details["total_value"] = total_value["value"]
            financial_details["total_value_confidence"] = total_value["confidence"]

        # Extract currency information
        currency = self._extract_currency(text)
        if currency:
            financial_details["currency"] = currency

        # Extract line items (detailed billing breakdown)
        line_items = self._extract_line_items(text)
        if line_items:
            financial_details["line_items"] = line_items

        # Extract tax information
        tax_info = self._extract_tax_information(text)
        if tax_info:
            financial_details["tax_information"] = tax_info

        return financial_details

    def _extract_total_value(self, text: str) -> Optional[Dict[str, Any]]:
        """Extract total contract value

        Uses multiple patterns to find contract totals, handling various
        formatting styles and currency representations.

        Args:
            text: Contract text

        Returns:
            Dictionary with value and confidence score, or None if not found
        """
        value_patterns = [
            r'Total\s*(?:Contract\s*)?(?:Value|Amount)[\s:]*\$?\s*(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)',
            r'Contract\s*Value[\s:]*\$?\s*(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)',
            r'Total[\s:]*\$\s*(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)',
            r'Amount\s*Due[\s:]*\$?\s*(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)',
        ]

        for pattern in value_patterns:
            result = extract_confidence_score(text, pattern, "total_value")
            if result["value"]:
                return {
                    "value": f"${result['value']}",
                    "confidence": result["confidence"]
                }

        return None

    def _extract_currency(self, text: str) -> Optional[str]:
        """Extract currency information

        Detects currency type from symbols and explicit mentions.

        Args:
            text: Contract text

        Returns:
            Currency code ("USD", "EUR", "GBP") or None
        """
        if re.search(r'\$|USD|US Dollar', text, re.IGNORECASE):
            return "USD"
        elif re.search(r'€|EUR|Euro', text, re.IGNORECASE):
            return "EUR"
        elif re.search(r'£|GBP|British Pound', text, re.IGNORECASE):
            return "GBP"

        return None

    def _extract_line_items(self, text: str) -> List[Dict[str, Any]]:
        """Extract line items from contract

        Parses detailed billing line items with descriptions, quantities, and pricing.

        Args:
            text: Contract text

        Returns:
            List of line item dictionaries
        """
        line_items = []

        # Pattern for line items with descriptions, quantities, and prices
        line_pattern = r'([A-Z][^$\n]*?)\s+(\d+)\s+\$\s*(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)\s+\$\s*(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)'

        matches = re.findall(line_pattern, text, re.MULTILINE)

        for match in matches:
            line_items.append({
                "description": match[0].strip(),
                "quantity": int(match[1]),
                "unit_price": f"${match[2]}",
                "total": f"${match[3]}"
            })

        return line_items[:10]  # Limit to 10 line items

    def _extract_tax_information(self, text: str) -> Optional[Dict[str, Any]]:
        """Extract tax information

        Finds tax rates and types mentioned in the contract.

        Args:
            text: Contract text

        Returns:
            Dictionary with tax rate and confidence, or None
        """
        tax_patterns = [
            r'Tax\s*Rate[\s:]*(\d+(?:\.\d+)?%)',
            r'VAT[\s:]*(\d+(?:\.\d+)?%)',
            r'Sales\s*Tax[\s:]*(\d+(?:\.\d+)?%)',
        ]

        for pattern in tax_patterns:
            result = extract_confidence_score(text, pattern, "tax")
            if result["value"]:
                return {
                    "rate": result["value"],
                    "confidence": result["confidence"]
                }

        return None
    
    def _extract_payment_structure(self, text: str) -> Dict[str, Any]:
        """Extract payment terms and structure

        Identifies payment schedules, terms, and methods from contract text.

        Args:
            text: Contract text

        Returns:
            Dictionary containing payment structure details
        """
        payment_structure = {}

        # Extract payment terms (e.g., "Net 30 days")
        for pattern in self.payment_terms_patterns:
            result = extract_confidence_score(text, pattern, "payment_terms")
            if result["value"]:
                payment_structure["terms"] = f"Net {result['value']}"
                payment_structure["terms_confidence"] = result["confidence"]
                break

        # Extract payment schedule
        schedule_patterns = [
            r'(?:Payment|Billing)\s*Schedule[\s:]*([^\n\.]+)',
            r'(?:Monthly|Quarterly|Annual|Weekly)\s*payments?',
        ]

        for pattern in schedule_patterns:
            result = extract_confidence_score(text, pattern, "schedule")
            if result["value"]:
                payment_structure["schedule"] = result["value"]
                payment_structure["schedule_confidence"] = result["confidence"]
                break

        # Extract payment method
        method_patterns = [
            r'Payment\s*Method[\s:]*([^\n\.]+)',
            r'(?:Wire\s*Transfer|ACH|Check|Credit\s*Card)',
        ]

        for pattern in method_patterns:
            result = extract_confidence_score(text, pattern, "payment_method")
            if result["value"]:
                payment_structure["method"] = result["value"]
                payment_structure["method_confidence"] = result["confidence"]
                break

        return payment_structure

    def _extract_sla_terms(self, text: str) -> Dict[str, Any]:
        """Extract Service Level Agreement terms

        Finds SLA components like response times, uptime guarantees, and penalties.

        Args:
            text: Contract text

        Returns:
            Dictionary containing SLA terms and conditions
        """
        sla_terms = {}

        # Extract response time requirements
        response_patterns = [
            r'Response\s*Time[\s:]*(\d+\s*(?:hours?|minutes?|days?))',
            r'(\d+\s*(?:hour|minute|day))\s*response',
        ]

        for pattern in response_patterns:
            result = extract_confidence_score(text, pattern, "response_time")
            if result["value"]:
                sla_terms["response_time"] = result["value"]
                sla_terms["response_time_confidence"] = result["confidence"]
                break

        # Extract uptime guarantee
        uptime_patterns = [
            r'(?:Uptime|Availability)[\s:]*(\d+(?:\.\d+)?%)',
            r'(\d+(?:\.\d+)?%)\s*(?:uptime|availability)',
        ]

        for pattern in uptime_patterns:
            result = extract_confidence_score(text, pattern, "uptime")
            if result["value"]:
                sla_terms["uptime_guarantee"] = result["value"]
                sla_terms["uptime_confidence"] = result["confidence"]
                break

        # Extract penalty clauses
        penalty_patterns = [
            r'Penalty[\s:]*([^\n\.]+)',
            r'(?:reduction|penalty).*?(\d+(?:\.\d+)?%)',
        ]

        for pattern in penalty_patterns:
            result = extract_confidence_score(text, pattern, "penalties")
            if result["value"]:
                sla_terms["penalties"] = result["value"]
                sla_terms["penalties_confidence"] = result["confidence"]
                break

        return sla_terms

    def _extract_contact_information(self, text: str) -> Dict[str, Any]:
        """Extract contact information

        Finds email addresses and phone numbers mentioned in the contract.

        Args:
            text: Contract text

        Returns:
            Dictionary containing contact details
        """
        contact_info = {}

        # Extract email addresses
        email_pattern = r'([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})'
        emails = re.findall(email_pattern, text)

        if emails:
            contact_info["emails"] = list(set(emails))  # Remove duplicates

        # Extract phone numbers (US format)
        phone_pattern = r'(?:\+?1[-.\s]?)?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})'
        phones = re.findall(phone_pattern, text)

        if phones:
            contact_info["phones"] = [f"({phone[0]}) {phone[1]}-{phone[2]}" for phone in phones]

        return contact_info

    def _extract_account_information(self, text: str) -> Dict[str, Any]:
        """Extract account and billing information

        Finds account numbers, customer IDs, and billing addresses.

        Args:
            text: Contract text

        Returns:
            Dictionary containing account-related information
        """
        account_info = {}

        # Extract account number
        account_patterns = [
            r'Account\s*(?:Number|#)[\s:]*([A-Z0-9-]+)',
            r'Customer\s*ID[\s:]*([A-Z0-9-]+)',
        ]

        for pattern in account_patterns:
            result = extract_confidence_score(text, pattern, "account_number")
            if result["value"]:
                account_info["account_number"] = result["value"]
                account_info["account_confidence"] = result["confidence"]
                break

        # Extract billing address (simplified multi-line extraction)
        address_pattern = r'(?:Billing\s*Address|Address)[\s:]*([^\n]+(?:\n[^\n]+){0,3})'
        address_match = re.search(address_pattern, text, re.IGNORECASE | re.MULTILINE)

        if address_match:
            account_info["billing_address"] = address_match.group(1).strip()

        return account_info

    def _extract_revenue_classification(self, text: str) -> Dict[str, Any]:
        """Extract revenue classification information

        Determines if the contract represents recurring or one-time revenue
        and identifies billing cycles.

        Args:
            text: Contract text

        Returns:
            Dictionary containing revenue classification details
        """
        revenue_info = {}

        # Check for recurring vs one-time revenue
        if re.search(r'(?:recurring|subscription|monthly|annual|quarterly)', text, re.IGNORECASE):
            revenue_info["type"] = "Recurring"

            # Extract billing cycle
            if re.search(r'monthly', text, re.IGNORECASE):
                revenue_info["billing_cycle"] = "Monthly"
            elif re.search(r'quarterly', text, re.IGNORECASE):
                revenue_info["billing_cycle"] = "Quarterly"
            elif re.search(r'annually|annual', text, re.IGNORECASE):
                revenue_info["billing_cycle"] = "Annual"
        else:
            revenue_info["type"] = "One-time"

        # Extract renewal terms
        renewal_pattern = r'(?:renewal|auto-renew|automatically\s*renew)[^\n\.]*'
        renewal_match = re.search(renewal_pattern, text, re.IGNORECASE)

        if renewal_match:
            revenue_info["renewal_terms"] = renewal_match.group(0)

        return revenue_info


# Create global extractor instance for use across the application
extractor = ContractExtractor()
