"""API routers and endpoints for contract intelligence system"""

from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, Query
from fastapi.responses import StreamingResponse, JSONResponse
from typing import List, Optional, Dict, Any
import logging
from io import BytesIO

from src.database.models import get_contracts_collection
from src.tasks.celery import parse_contract
from src.core.utils import generate_contract_id, validate_file, get_current_timestamp
from src.core.config import MAX_FILE_SIZE
from src.core.exceptions import FileValidationError, ContractNotFoundError

logger = logging.getLogger(__name__)

# Create API router
router = APIRouter(prefix="/api/v1", tags=["contracts"])


@router.post("/contracts/upload", response_model=Dict[str, str])
async def upload_contract(file: UploadFile = File(...)):
    """
    Upload a contract PDF for processing
    
    Args:
        file: PDF file to upload
        
    Returns:
        Dictionary with contract_id for tracking
        
    Raises:
        HTTPException: If file validation fails
    """
    try:
        logger.info(f"Received file upload: {file.filename}")
        
        # Read file data
        file_data = await file.read()
        
        # Validate file
        validate_file(file_data, file.filename or "", MAX_FILE_SIZE)
        
        # Generate contract ID
        contract_id = generate_contract_id()
        
        # Store contract in database
        contracts = get_contracts_collection()
        contract_doc = {
            "contract_id": contract_id,
            "filename": file.filename,
            "file_size": len(file_data),
            "status": "pending",
            "progress": 0,
            "original_file": file_data,
            "upload_date": get_current_timestamp(),
            "created_at": get_current_timestamp(),
            "updated_at": get_current_timestamp()
        }
        
        contracts.insert_one(contract_doc)
        logger.info(f"Stored contract {contract_id} in database")
        
        # Start async processing
        parse_contract.delay(contract_id)
        logger.info(f"Started async processing for contract {contract_id}")
        
        return {
            "contract_id": contract_id,
            "message": "Contract uploaded successfully and processing started",
            "filename": file.filename
        }
        
    except FileValidationError as e:
        logger.warning(f"File validation failed: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Upload failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


@router.get("/contracts/{contract_id}/status", response_model=Dict[str, Any])
def get_contract_status(contract_id: str):
    """
    Get processing status for a contract
    
    Args:
        contract_id: Unique contract identifier
        
    Returns:
        Dictionary with status information
        
    Raises:
        HTTPException: If contract not found
    """
    try:
        contracts = get_contracts_collection()
        contract = contracts.find_one({"contract_id": contract_id})
        
        if not contract:
            raise ContractNotFoundError(f"Contract {contract_id} not found")
        
        response_data = {
            "contract_id": contract_id,
            "status": contract["status"],
            "progress": contract["progress"],
            "filename": contract.get("filename"),
            "upload_date": contract.get("upload_date"),
            "updated_at": contract.get("updated_at")
        }
        
        # Include error details if failed
        if contract["status"] == "failed" and contract.get("error"):
            response_data["error"] = contract["error"]
        
        # Include processing completion time if completed
        if contract["status"] == "completed" and contract.get("processing_completed_at"):
            response_data["processing_completed_at"] = contract["processing_completed_at"]
        
        return response_data
        
    except ContractNotFoundError:
        raise HTTPException(status_code=404, detail=f"Contract {contract_id} not found")
    except Exception as e:
        logger.error(f"Failed to get status for contract {contract_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve contract status")


@router.get("/contracts/{contract_id}", response_model=Dict[str, Any])
def get_contract_data(contract_id: str):
    """
    Get extracted data for a completed contract
    
    Args:
        contract_id: Unique contract identifier
        
    Returns:
        Dictionary with extracted contract data and scores
        
    Raises:
        HTTPException: If contract not found or not ready
    """
    try:
        contracts = get_contracts_collection()
        contract = contracts.find_one({"contract_id": contract_id})
        
        if not contract:
            raise ContractNotFoundError(f"Contract {contract_id} not found")
        
        if contract["status"] != "completed":
            raise HTTPException(
                status_code=400,
                detail=f"Contract processing not completed. Current status: {contract['status']}"
            )
        
        # Prepare response data
        response_data = {
            "contract_id": contract_id,
            "filename": contract.get("filename"),
            "status": contract["status"],
            "score": contract.get("score", 0),
            "extracted_data": contract.get("extracted_data", {}),
            "gaps": contract.get("gaps", []),
            "confidence_scores": contract.get("confidence_scores", {}),
            "processing_completed_at": contract.get("processing_completed_at"),
            "file_size": contract.get("file_size"),
            "upload_date": contract.get("upload_date")
        }
        
        return response_data
        
    except ContractNotFoundError:
        raise HTTPException(status_code=404, detail=f"Contract {contract_id} not found")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get data for contract {contract_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve contract data")


@router.get("/contracts", response_model=Dict[str, Any])
def list_contracts(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(10, ge=1, le=100, description="Number of contracts per page"),
    status: Optional[str] = Query(None, description="Filter by status"),
    sort_by: str = Query("upload_date", description="Sort field"),
    sort_order: str = Query("desc", regex="^(asc|desc)$", description="Sort order")
):
    """
    Get paginated list of contracts with optional filtering and sorting
    
    Args:
        page: Page number (starting from 1)
        limit: Number of contracts per page
        status: Optional status filter
        sort_by: Field to sort by
        sort_order: Sort order (asc or desc)
        
    Returns:
        Dictionary with paginated contract list and metadata
    """
    try:
        contracts = get_contracts_collection()
        
        # Build query
        query = {}
        if status:
            if status not in ["pending", "processing", "completed", "failed"]:
                raise HTTPException(status_code=400, detail="Invalid status filter")
            query["status"] = status
        
        # Count total documents
        total_count = contracts.count_documents(query)
        
        # Calculate pagination
        skip = (page - 1) * limit
        total_pages = (total_count + limit - 1) // limit
        
        # Build sort criteria
        sort_direction = 1 if sort_order == "asc" else -1
        sort_criteria = [(sort_by, sort_direction)]
        
        # Get contracts
        cursor = contracts.find(query, {
            "original_file": 0  # Exclude binary data from list
        }).sort(sort_criteria).skip(skip).limit(limit)
        
        contract_list = []
        for contract in cursor:
            contract_summary = {
                "contract_id": contract["contract_id"],
                "filename": contract.get("filename"),
                "status": contract["status"],
                "progress": contract["progress"],
                "score": contract.get("score"),
                "upload_date": contract.get("upload_date"),
                "updated_at": contract.get("updated_at"),
                "file_size": contract.get("file_size"),
                "gaps_count": len(contract.get("gaps", []))
            }
            
            # Add error for failed contracts
            if contract["status"] == "failed" and contract.get("error"):
                contract_summary["error"] = contract["error"]
            
            contract_list.append(contract_summary)
        
        return {
            "contracts": contract_list,
            "pagination": {
                "current_page": page,
                "total_pages": total_pages,
                "total_count": total_count,
                "page_size": limit,
                "has_next": page < total_pages,
                "has_prev": page > 1
            },
            "filters": {
                "status": status,
                "sort_by": sort_by,
                "sort_order": sort_order
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to list contracts: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve contracts list")


@router.get("/contracts/{contract_id}/download")
def download_contract(contract_id: str):
    """
    Download original contract file
    
    Args:
        contract_id: Unique contract identifier
        
    Returns:
        StreamingResponse with PDF file
        
    Raises:
        HTTPException: If contract not found
    """
    try:
        contracts = get_contracts_collection()
        contract = contracts.find_one({"contract_id": contract_id})
        
        if not contract:
            raise ContractNotFoundError(f"Contract {contract_id} not found")
        
        if "original_file" not in contract:
            raise HTTPException(status_code=404, detail="Original file not found")
        
        # Create file stream
        file_stream = BytesIO(contract["original_file"])
        filename = contract.get("filename", f"{contract_id}.pdf")
        
        return StreamingResponse(
            BytesIO(contract["original_file"]),
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename=\"{filename}\"",
                "Content-Length": str(len(contract["original_file"]))
            }
        )
        
    except ContractNotFoundError:
        raise HTTPException(status_code=404, detail=f"Contract {contract_id} not found")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to download contract {contract_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to download contract")


@router.delete("/contracts/{contract_id}")
def delete_contract(contract_id: str):
    """
    Delete a contract and its data
    
    Args:
        contract_id: Unique contract identifier
        
    Returns:
        Confirmation message
        
    Raises:
        HTTPException: If contract not found
    """
    try:
        contracts = get_contracts_collection()
        result = contracts.delete_one({"contract_id": contract_id})
        
        if result.deleted_count == 0:
            raise ContractNotFoundError(f"Contract {contract_id} not found")
        
        logger.info(f"Deleted contract {contract_id}")
        
        return {
            "message": f"Contract {contract_id} deleted successfully",
            "contract_id": contract_id
        }
        
    except ContractNotFoundError:
        raise HTTPException(status_code=404, detail=f"Contract {contract_id} not found")
    except Exception as e:
        logger.error(f"Failed to delete contract {contract_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to delete contract")


@router.get("/health", response_model=Dict[str, str])
def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "contract-intelligence-parser",
        "timestamp": get_current_timestamp()
    }


# Statistics endpoint (bonus feature)
@router.get("/contracts/stats", response_model=Dict[str, Any])
def get_contract_statistics():
    """
    Get contract processing statistics
    
    Returns:
        Dictionary with various statistics
    """
    try:
        contracts = get_contracts_collection()
        
        # Count by status
        pipeline = [
            {"$group": {
                "_id": "$status",
                "count": {"$sum": 1},
                "avg_score": {"$avg": "$score"}
            }}
        ]
        
        status_stats = list(contracts.aggregate(pipeline))
        
        # Overall stats
        total_contracts = contracts.count_documents({})
        completed_contracts = contracts.count_documents({"status": "completed"})
        
        # Average score for completed contracts
        avg_score_pipeline = [
            {"$match": {"status": "completed", "score": {"$exists": True}}},
            {"$group": {"_id": None, "avg_score": {"$avg": "$score"}}}
        ]
        
        avg_score_result = list(contracts.aggregate(avg_score_pipeline))
        avg_score = round(avg_score_result[0]["avg_score"], 1) if avg_score_result else 0
        
        return {
            "total_contracts": total_contracts,
            "completed_contracts": completed_contracts,
            "completion_rate": round((completed_contracts / total_contracts * 100), 1) if total_contracts > 0 else 0,
            "average_score": avg_score,
            "status_breakdown": {stat["_id"]: stat["count"] for stat in status_stats},
            "timestamp": get_current_timestamp()
        }
        
    except Exception as e:
        logger.error(f"Failed to get statistics: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve statistics")
