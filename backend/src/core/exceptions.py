"""Custom exceptions for the application"""

class ContractParsingError(Exception):
    """Exception raised when contract parsing fails"""
    pass

class FileValidationError(Exception):
    """Exception raised when file validation fails"""
    pass

class ContractNotFoundError(Exception):
    """Exception raised when contract is not found"""
    pass

class ProcessingError(Exception):
    """Exception raised when processing fails"""
    pass

class DatabaseError(Exception):
    """Exception raised when database operations fail"""
    pass

class ExtractionError(Exception):
    """Exception raised when data extraction fails"""
    pass
