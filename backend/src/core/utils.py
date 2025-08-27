"""Core utility functions for scoring and gap analysis"""

from typing import Dict, List, Any
import re
from datetime import datetime
from src.core.config import SCORING_WEIGHTS


def calculate_score(extracted_data: Dict[str, Any]) -> int:
    """
    Calculate overall score for a contract based on extracted data completeness
    
    Args:
        extracted_data: Dictionary containing extracted contract data
        
    Returns:
        Score from 0-100
    """
    score = 0
    
    # Financial completeness (30 points)
    if extracted_data.get("financial_details"):
        financial = extracted_data["financial_details"]
        financial_score = 0
        
        if financial.get("total_value"):
            financial_score += 10
        if financial.get("line_items") and len(financial["line_items"]) > 0:
            financial_score += 10
        if financial.get("currency"):
            financial_score += 5
        if financial.get("tax_information"):
            financial_score += 5
            
        score += min(financial_score, SCORING_WEIGHTS["financial_completeness"])
    
    # Party identification (25 points)
    if extracted_data.get("parties"):
        parties = extracted_data["parties"]
        if len(parties) >= 2:  # At least two parties
            party_score = 15
            if any(p.get("legal_entity") for p in parties):
                party_score += 5
            if any(p.get("authorized_signatory") for p in parties):
                party_score += 5
            score += min(party_score, SCORING_WEIGHTS["party_identification"])
    
    # Payment terms clarity (20 points)
    if extracted_data.get("payment_structure"):
        payment = extracted_data["payment_structure"]
        payment_score = 0
        
        if payment.get("terms"):
            payment_score += 8
        if payment.get("schedule"):
            payment_score += 6
        if payment.get("method"):
            payment_score += 6
            
        score += min(payment_score, SCORING_WEIGHTS["payment_terms_clarity"])
    
    # SLA definition (15 points)
    if extracted_data.get("sla_terms"):
        sla = extracted_data["sla_terms"]
        sla_score = 0
        
        if sla.get("response_time"):
            sla_score += 5
        if sla.get("uptime_guarantee"):
            sla_score += 5
        if sla.get("penalties"):
            sla_score += 5
            
        score += min(sla_score, SCORING_WEIGHTS["sla_definition"])
    
    # Contact information (10 points)
    if extracted_data.get("contact_information"):
        contact = extracted_data["contact_information"]
        contact_score = 0
        
        if contact.get("billing_contact"):
            contact_score += 5
        if contact.get("technical_contact"):
            contact_score += 5
            
        score += min(contact_score, SCORING_WEIGHTS["contact_information"])
    
    return min(score, 100)


def identify_gaps(extracted_data: Dict[str, Any]) -> List[Dict[str, str]]:
    """
    Identify missing or incomplete critical fields in contract data
    
    Args:
        extracted_data: Dictionary containing extracted contract data
        
    Returns:
        List of gaps with field name, importance, and status
    """
    gaps = []
    
    # Critical financial information
    if not extracted_data.get("financial_details"):
        gaps.append({
            "field": "Financial Details",
            "importance": "High",
            "status": "Missing",
            "description": "No financial information found"
        })
    else:
        financial = extracted_data["financial_details"]
        if not financial.get("total_value"):
            gaps.append({
                "field": "Contract Value",
                "importance": "High",
                "status": "Missing",
                "description": "Total contract value not specified"
            })
        if not financial.get("currency"):
            gaps.append({
                "field": "Currency",
                "importance": "Medium",
                "status": "Missing",
                "description": "Currency not specified"
            })
    
    # Party information
    parties = extracted_data.get("parties", [])
    if len(parties) < 2:
        gaps.append({
            "field": "Contract Parties",
            "importance": "High",
            "status": "Incomplete",
            "description": "Less than 2 parties identified"
        })
    
    # Payment terms
    if not extracted_data.get("payment_structure"):
        gaps.append({
            "field": "Payment Terms",
            "importance": "High",
            "status": "Missing",
            "description": "Payment terms not found"
        })
    else:
        payment = extracted_data["payment_structure"]
        if not payment.get("terms"):
            gaps.append({
                "field": "Payment Schedule",
                "importance": "High",
                "status": "Missing",
                "description": "Payment schedule not specified"
            })
    
    # SLA terms
    if not extracted_data.get("sla_terms"):
        gaps.append({
            "field": "Service Level Agreements",
            "importance": "Medium",
            "status": "Missing",
            "description": "SLA terms not found"
        })
    
    # Contact information
    if not extracted_data.get("contact_information"):
        gaps.append({
            "field": "Contact Information",
            "importance": "Medium",
            "status": "Missing",
            "description": "Contact details not found"
        })
    
    return gaps


def validate_file(file_data: bytes, filename: str, max_size: int) -> bool:
    """
    Validate uploaded file
    
    Args:
        file_data: Binary file data
        filename: Original filename
        max_size: Maximum allowed file size in bytes
        
    Returns:
        True if file is valid
        
    Raises:
        FileValidationError: If file is invalid
    """
    from src.core.exceptions import FileValidationError
    
    # Check file extension
    if not filename.lower().endswith('.pdf'):
        raise FileValidationError("Only PDF files are supported")
    
    # Check file size
    if len(file_data) > max_size:
        raise FileValidationError(f"File size exceeds maximum limit of {max_size / 1024 / 1024:.1f} MB")
    
    # Check if file has content
    if len(file_data) == 0:
        raise FileValidationError("File is empty")
    
    # Basic PDF header check
    if not file_data.startswith(b'%PDF'):
        raise FileValidationError("File is not a valid PDF")
    
    return True


def generate_contract_id() -> str:
    """Generate a unique contract ID"""
    from uuid import uuid4
    return str(uuid4())


def get_current_timestamp() -> str:
    """Get current timestamp in ISO format"""
    return datetime.utcnow().isoformat()


def extract_confidence_score(text: str, pattern: str, field_name: str) -> Dict[str, Any]:
    """
    Extract data with confidence scoring based on pattern match strength
    
    Args:
        text: Text to search in
        pattern: Regex pattern
        field_name: Name of the field being extracted
        
    Returns:
        Dictionary with extracted value and confidence score
    """
    matches = re.findall(pattern, text, re.IGNORECASE | re.MULTILINE)
    
    if not matches:
        return {"value": None, "confidence": 0}
    
    # Calculate confidence based on:
    # - Number of matches (more matches = higher confidence)
    # - Context around matches
    # - Pattern specificity
    
    confidence = min(85 + len(matches) * 5, 95)  # Base confidence with boost for multiple matches
    
    if len(matches) == 1:
        # Single match - check context
        match_context = re.search(f".{{0,50}}{re.escape(matches[0])}.{{0,50}}", text, re.IGNORECASE)
        if match_context and field_name.lower() in match_context.group().lower():
            confidence += 10
    
    return {
        "value": matches[0] if len(matches) == 1 else matches,
        "confidence": min(confidence, 95),
        "matches_count": len(matches)
    }
