"""PDF extraction and contract data parsing services"""

import pdfplumber
import re
from io import BytesIO
from typing import Dict, List, Any, Optional
import logging
from src.core.utils import extract_confidence_score
from src.core.exceptions import ExtractionError

logger = logging.getLogger(__name__)


class ContractExtractor:
    """Main class for extracting data from contract PDFs"""
    
    def __init__(self):
        self.currency_patterns = [
            r'\$\s*(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)',  # USD format
            r'USD\s*(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)',  # USD explicit
            r'€\s*(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)',   # EUR format
            r'£\s*(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)',   # GBP format
        ]
        
        self.payment_terms_patterns = [
            r'Net\s*(\d+)\s*days?',
            r'(\d+)\s*days?\s*net',
            r'Payment\s*due\s*in\s*(\d+)\s*days?',
            r'Terms?\s*:\s*Net\s*(\d+)',
        ]
        
        self.party_patterns = [
            r'(?:Party|Contractor|Vendor|Client|Customer)[\s:]+([A-Z][^,\n\.]+(?:Inc\.|LLC|Ltd\.|Corp\.)?)',
            r'([A-Z][A-Za-z\s]+(?:Inc\.|LLC|Ltd\.|Corp\.|Company))',
            r'between\s+([A-Z][^,\n]+?)(?:\s+and|\s*,)',
        ]
        
    def extract_data(self, file_bytes: bytes) -> Dict[str, Any]:
        """
        Extract structured data from PDF contract
        
        Args:
            file_bytes: Binary PDF data
            
        Returns:
            Dictionary containing extracted contract data
            
        Raises:
            ExtractionError: If extraction fails
        """
        try:
            # Extract text from PDF
            text = self._extract_text_from_pdf(file_bytes)
            
            if not text or len(text.strip()) < 100:
                raise ExtractionError("PDF contains insufficient text content")
            
            # Extract different components
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
        """Extract text from PDF using pdfplumber"""
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
        """Count pages in PDF"""
        try:
            with pdfplumber.open(BytesIO(file_bytes)) as pdf:
                return len(pdf.pages)
        except:
            return 0
    
    def _extract_parties(self, text: str) -> List[Dict[str, Any]]:
        """Extract contract parties"""
        parties = []
        
        for pattern in self.party_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE | re.MULTILINE)
            for match in matches:
                party_name = match.strip()
                if len(party_name) > 3 and party_name not in [p["name"] for p in parties]:
                    
                    # Determine party role
                    role = self._determine_party_role(text, party_name)
                    
                    # Extract additional party details
                    legal_entity = self._extract_legal_entity_details(text, party_name)
                    
                    confidence = extract_confidence_score(text, re.escape(party_name), "party")
                    
                    parties.append({
                        "name": party_name,
                        "role": role,
                        "legal_entity": legal_entity,
                        "confidence": confidence["confidence"]
                    })
        
        return parties[:4]  # Limit to 4 parties max
    
    def _determine_party_role(self, text: str, party_name: str) -> str:
        """Determine the role of a party in the contract"""
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
        """Extract legal entity information for a party"""
        entity_pattern = rf"{re.escape(party_name)}[^,\n\.]*?(Inc\.|LLC|Ltd\.|Corp\.|Company|Corporation)"
        match = re.search(entity_pattern, text, re.IGNORECASE)
        
        return match.group(1) if match else None
    
    def _extract_financial_details(self, text: str) -> Dict[str, Any]:
        """Extract financial information from contract"""
        financial_details = {}
        
        # Extract total contract value
        total_value = self._extract_total_value(text)
        if total_value:
            financial_details["total_value"] = total_value["value"]
            financial_details["total_value_confidence"] = total_value["confidence"]
        
        # Extract currency
        currency = self._extract_currency(text)
        if currency:
            financial_details["currency"] = currency
        
        # Extract line items
        line_items = self._extract_line_items(text)
        if line_items:
            financial_details["line_items"] = line_items
        
        # Extract tax information
        tax_info = self._extract_tax_information(text)
        if tax_info:
            financial_details["tax_information"] = tax_info
        
        return financial_details
    
    def _extract_total_value(self, text: str) -> Optional[Dict[str, Any]]:
        """Extract total contract value"""
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
        """Extract currency information"""
        if re.search(r'\$|USD|US Dollar', text, re.IGNORECASE):
            return "USD"
        elif re.search(r'€|EUR|Euro', text, re.IGNORECASE):
            return "EUR"
        elif re.search(r'£|GBP|British Pound', text, re.IGNORECASE):
            return "GBP"
        
        return None
    
    def _extract_line_items(self, text: str) -> List[Dict[str, Any]]:
        """Extract line items from contract"""
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
        """Extract tax information"""
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
        """Extract payment terms and structure"""
        payment_structure = {}
        
        # Payment terms
        for pattern in self.payment_terms_patterns:
            result = extract_confidence_score(text, pattern, "payment_terms")
            if result["value"]:
                payment_structure["terms"] = f"Net {result['value']}"
                payment_structure["terms_confidence"] = result["confidence"]
                break
        
        # Payment schedule
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
        
        # Payment method
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
        """Extract Service Level Agreement terms"""
        sla_terms = {}
        
        # Response time
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
        
        # Uptime guarantee
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
        
        # Penalties
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
        """Extract contact information"""
        contact_info = {}
        
        # Email patterns
        email_pattern = r'([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})'
        emails = re.findall(email_pattern, text)
        
        if emails:
            contact_info["emails"] = list(set(emails))
        
        # Phone patterns
        phone_pattern = r'(?:\+?1[-.\s]?)?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})'
        phones = re.findall(phone_pattern, text)
        
        if phones:
            contact_info["phones"] = [f"({phone[0]}) {phone[1]}-{phone[2]}" for phone in phones]
        
        return contact_info
    
    def _extract_account_information(self, text: str) -> Dict[str, Any]:
        """Extract account and billing information"""
        account_info = {}
        
        # Account number patterns
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
        
        # Billing address (simplified)
        address_pattern = r'(?:Billing\s*Address|Address)[\s:]*([^\n]+(?:\n[^\n]+){0,3})'
        address_match = re.search(address_pattern, text, re.IGNORECASE | re.MULTILINE)
        
        if address_match:
            account_info["billing_address"] = address_match.group(1).strip()
        
        return account_info
    
    def _extract_revenue_classification(self, text: str) -> Dict[str, Any]:
        """Extract revenue classification information"""
        revenue_info = {}
        
        # Check for recurring vs one-time
        if re.search(r'(?:recurring|subscription|monthly|annual|quarterly)', text, re.IGNORECASE):
            revenue_info["type"] = "Recurring"
            
            # Extract billing cycle
            if re.search(r'monthly', text, re.IGNORECASE):
                revenue_info["billing_cycle"] = "Monthly"
            elif re.search(r'quarterly', text, re.IGNORECASE):
                revenue_info["billing_cycle"] = "Quarterly"
            elif re.search(r'annual', text, re.IGNORECASE):
                revenue_info["billing_cycle"] = "Annual"
        else:
            revenue_info["type"] = "One-time"
        
        # Renewal terms
        renewal_pattern = r'(?:renewal|auto-renew|automatically\s*renew)[^\n\.]*'
        renewal_match = re.search(renewal_pattern, text, re.IGNORECASE)
        
        if renewal_match:
            revenue_info["renewal_terms"] = renewal_match.group(0)
        
        return revenue_info


# Create global extractor instance
extractor = ContractExtractor()
