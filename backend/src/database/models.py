"""Database models and connection management"""

from pymongo import MongoClient
from pymongo.database import Database
from pymongo.collection import Collection
from typing import Optional
import logging
from src.core.config import MONGO_URI

logger = logging.getLogger(__name__)

class MongoDB:
    """MongoDB connection manager"""
    
    def __init__(self, uri: str = MONGO_URI):
        self.uri = uri
        self.client: Optional[MongoClient] = None
        self.db: Optional[Database] = None
        
    def connect(self) -> Database:
        """Connect to MongoDB"""
        try:
            self.client = MongoClient(self.uri, serverSelectionTimeoutMS=5000)
            # Test the connection with shorter timeout
            self.client.admin.command('ping')
            self.db = self.client.get_default_database()
            logger.info("Connected to MongoDB successfully")
            return self.db
        except Exception as e:
            logger.warning(f"MongoDB connection failed: {e}")
            logger.info("Starting without MongoDB - some features will be unavailable")
            # Don't raise exception, allow app to start
            return None
            
    def disconnect(self):
        """Disconnect from MongoDB"""
        if self.client:
            self.client.close()
            logger.info("Disconnected from MongoDB")
    
    def get_collection(self, collection_name: str) -> Collection:
        """Get a collection from the database"""
        if not self.db:
            self.connect()
        return self.db[collection_name]

# Global MongoDB instance
mongodb = MongoDB()

# Collections
def get_contracts_collection() -> Collection:
    """Get the contracts collection"""
    return mongodb.get_collection("contracts")

def get_files_collection() -> Collection:
    """Get the files collection (for GridFS if needed)"""
    return mongodb.get_collection("files")

# Contract document schema example:
CONTRACT_SCHEMA = {
    "contract_id": str,        # Unique identifier
    "filename": str,           # Original filename
    "file_size": int,          # File size in bytes
    "upload_date": str,        # ISO datetime string
    "status": str,             # "pending", "processing", "completed", "failed"
    "progress": int,           # 0-100
    "original_file": bytes,    # Binary file data
    "extracted_data": dict,    # Parsed contract data
    "score": int,              # Overall score 0-100
    "gaps": list,              # Missing fields
    "error": str,              # Error message if failed
    "confidence_scores": dict,  # Confidence per field
    "created_at": str,         # ISO datetime string
    "updated_at": str,         # ISO datetime string
}
