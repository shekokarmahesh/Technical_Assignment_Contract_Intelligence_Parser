"""Celery configuration and async tasks"""

from celery import Celery
import logging
from datetime import datetime
from typing import Dict, Any

from src.core.config import CELERY_BROKER_URL, CELERY_RESULT_BACKEND
from src.database.models import get_contracts_collection
from src.services.extractor import extractor
from src.core.utils import calculate_score, identify_gaps, get_current_timestamp
from src.core.exceptions import ProcessingError, ExtractionError

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create Celery app
celery_app = Celery(
    "contract_parser",
    broker=CELERY_BROKER_URL,
    backend=CELERY_RESULT_BACKEND,
    include=['src.tasks.celery']
)

# Celery configuration
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    result_expires=3600,  # Results expire after 1 hour
    task_routes={
        'src.tasks.celery.parse_contract': {'queue': 'contract_processing'},
    },
    # Retry configuration
    task_default_retry_delay=60,  # 1 minute
    task_max_retries=3,
    # Windows-specific configuration
    worker_pool='solo',  # Use solo pool for Windows compatibility
    worker_concurrency=1,  # Single worker for solo pool
)


@celery_app.task(bind=True, name='parse_contract')
def parse_contract(self, contract_id: str) -> Dict[str, Any]:
    """
    Async task to parse a contract PDF and extract data
    
    Args:
        contract_id: Unique identifier for the contract
        
    Returns:
        Dictionary with processing results
    """
    contracts = get_contracts_collection()
    
    try:
        logger.info(f"Starting contract parsing for ID: {contract_id}")
        
        # Get contract document
        contract_doc = contracts.find_one({"contract_id": contract_id})
        if not contract_doc:
            raise ProcessingError(f"Contract {contract_id} not found in database")
        
        # Update status to processing
        contracts.update_one(
            {"contract_id": contract_id},
            {
                "$set": {
                    "status": "processing",
                    "progress": 10,
                    "updated_at": get_current_timestamp()
                }
            }
        )
        
        logger.info(f"Updated contract {contract_id} status to processing")
        
        # Extract data from PDF
        try:
            # Update progress
            contracts.update_one(
                {"contract_id": contract_id},
                {"$set": {"progress": 30, "updated_at": get_current_timestamp()}}
            )
            
            extracted_data = extractor.extract_data(contract_doc["original_file"])
            logger.info(f"Successfully extracted data for contract {contract_id}")
            
            # Update progress
            contracts.update_one(
                {"contract_id": contract_id},
                {"$set": {"progress": 60, "updated_at": get_current_timestamp()}}
            )
            
        except ExtractionError as e:
            logger.error(f"Extraction failed for contract {contract_id}: {str(e)}")
            raise
        
        # Calculate score and gaps
        try:
            score = calculate_score(extracted_data)
            gaps = identify_gaps(extracted_data)
            
            logger.info(f"Calculated score {score} and found {len(gaps)} gaps for contract {contract_id}")
            
            # Update progress
            contracts.update_one(
                {"contract_id": contract_id},
                {"$set": {"progress": 80, "updated_at": get_current_timestamp()}}
            )
            
        except Exception as e:
            logger.error(f"Scoring failed for contract {contract_id}: {str(e)}")
            score = 0
            gaps = []
        
        # Calculate confidence scores for each section
        confidence_scores = _calculate_section_confidence(extracted_data)
        
        # Update contract with extracted data
        update_data = {
            "status": "completed",
            "progress": 100,
            "extracted_data": extracted_data,
            "score": score,
            "gaps": gaps,
            "confidence_scores": confidence_scores,
            "processing_completed_at": get_current_timestamp(),
            "updated_at": get_current_timestamp()
        }
        
        contracts.update_one(
            {"contract_id": contract_id},
            {"$set": update_data}
        )
        
        logger.info(f"Successfully completed processing for contract {contract_id} with score {score}")
        
        return {
            "status": "completed",
            "contract_id": contract_id,
            "score": score,
            "gaps_count": len(gaps),
            "processing_time": "completed"
        }
        
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Contract parsing failed for {contract_id}: {error_msg}")
        
        # Update contract with error status
        contracts.update_one(
            {"contract_id": contract_id},
            {
                "$set": {
                    "status": "failed",
                    "progress": 0,
                    "error": error_msg,
                    "updated_at": get_current_timestamp()
                }
            }
        )
        
        # Retry logic
        if self.request.retries < self.max_retries:
            logger.info(f"Retrying contract {contract_id} in {self.default_retry_delay} seconds")
            raise self.retry(countdown=self.default_retry_delay, exc=e)
        
        # If max retries exceeded, mark as permanently failed
        contracts.update_one(
            {"contract_id": contract_id},
            {
                "$set": {
                    "status": "failed",
                    "error": f"Max retries exceeded: {error_msg}",
                    "updated_at": get_current_timestamp()
                }
            }
        )
        
        raise ProcessingError(f"Contract parsing failed after {self.max_retries} retries: {error_msg}")


def _calculate_section_confidence(extracted_data: Dict[str, Any]) -> Dict[str, float]:
    """Calculate confidence scores for each section of extracted data"""
    confidence_scores = {}
    
    # Parties confidence
    if extracted_data.get("parties"):
        parties_confidence = sum(p.get("confidence", 0) for p in extracted_data["parties"]) / len(extracted_data["parties"])
        confidence_scores["parties"] = round(parties_confidence, 2)
    
    # Financial details confidence
    if extracted_data.get("financial_details"):
        financial = extracted_data["financial_details"]
        confidences = []
        
        if financial.get("total_value_confidence"):
            confidences.append(financial["total_value_confidence"])
        if financial.get("tax_information", {}).get("confidence"):
            confidences.append(financial["tax_information"]["confidence"])
            
        if confidences:
            confidence_scores["financial_details"] = round(sum(confidences) / len(confidences), 2)
    
    # Payment structure confidence
    if extracted_data.get("payment_structure"):
        payment = extracted_data["payment_structure"]
        confidences = []
        
        for key in ["terms_confidence", "schedule_confidence", "method_confidence"]:
            if payment.get(key):
                confidences.append(payment[key])
                
        if confidences:
            confidence_scores["payment_structure"] = round(sum(confidences) / len(confidences), 2)
    
    # SLA terms confidence
    if extracted_data.get("sla_terms"):
        sla = extracted_data["sla_terms"]
        confidences = []
        
        for key in ["response_time_confidence", "uptime_confidence", "penalties_confidence"]:
            if sla.get(key):
                confidences.append(sla[key])
                
        if confidences:
            confidence_scores["sla_terms"] = round(sum(confidences) / len(confidences), 2)
    
    # Account information confidence
    if extracted_data.get("account_information", {}).get("account_confidence"):
        confidence_scores["account_information"] = extracted_data["account_information"]["account_confidence"]
    
    return confidence_scores


@celery_app.task(name='health_check')
def health_check() -> Dict[str, str]:
    """Health check task for monitoring"""
    return {
        "status": "healthy",
        "timestamp": get_current_timestamp(),
        "worker": "contract_parser"
    }


@celery_app.task(name='cleanup_old_results')
def cleanup_old_results() -> Dict[str, Any]:
    """Clean up old processing results and temporary data"""
    contracts = get_contracts_collection()
    
    try:
        # Find contracts older than 30 days with failed status
        from datetime import datetime, timedelta
        cutoff_date = datetime.utcnow() - timedelta(days=30)
        
        result = contracts.delete_many({
            "status": "failed",
            "created_at": {"$lt": cutoff_date.isoformat()}
        })
        
        logger.info(f"Cleaned up {result.deleted_count} old failed contracts")
        
        return {
            "status": "completed",
            "deleted_count": result.deleted_count,
            "timestamp": get_current_timestamp()
        }
        
    except Exception as e:
        logger.error(f"Cleanup task failed: {str(e)}")
        return {
            "status": "failed",
            "error": str(e),
            "timestamp": get_current_timestamp()
        }
