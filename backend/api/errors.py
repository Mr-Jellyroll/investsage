
from typing import Optional, Dict, Any
from datetime import datetime

from .models import AnalysisResponse

class InvestSageError(Exception):

    def __init__(
        self, 
        message: str, 
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message)
        self.message = message
        self.error_code = error_code or "UNKNOWN_ERROR"
        self.details = details or {}
        self.timestamp = datetime.now().isoformat()

    def to_dict(self) -> Dict[str, Any]:
        """Convert error to dictionary format"""
        return {
            "error_code": self.error_code,
            "message": self.message,
            "details": self.details,
            "timestamp": self.timestamp
        }

class ValidationError(InvestSageError):
    """Raised when input validation fails"""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code="VALIDATION_ERROR",
            details=details
        )

class DatabaseError(InvestSageError):
    """Raised when database operations fail"""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code="DATABASE_ERROR",
            details=details
        )

class AnalysisError(InvestSageError):
    """Raised when analysis operations fail"""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code="ANALYSIS_ERROR",
            details=details
        )

class ResourceNotFoundError(InvestSageError):
    """Raised when a requested resource is not found"""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code="RESOURCE_NOT_FOUND",
            details=details
        )

class ConfigurationError(InvestSageError):
    """Raised when there's a configuration issue"""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code="CONFIGURATION_ERROR",
            details=details
        )

class RateLimitError(InvestSageError):
    """Raised when rate limits are exceeded"""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code="RATE_LIMIT_EXCEEDED",
            details=details
        )

def handle_error(error: Exception) -> Dict[str, Any]:
    """
    Convert any error to a standardized error response format
    
    Args:
        error: The exception to handle
        
    Returns:
        Dict containing standardized error information
    """
    if isinstance(error, InvestSageError):
        return error.to_dict()
    
    # Handle unexpected errors
    return InvestSageError(
        message=str(error),
        error_code="INTERNAL_ERROR",
        details={"type": error.__class__.__name__}
    ).to_dict()

def create_error_response(
    error: Exception,
    include_traceback: bool = False
) -> Dict[str, Any]:

    error_dict = handle_error(error)
    
    response = {
        "success": False,
        "error": error_dict["message"],
        "error_code": error_dict["error_code"],
        "timestamp": error_dict["timestamp"]
    }
    
    # Include additional details in development
    if include_traceback:
        import traceback
        response["traceback"] = traceback.format_exc()
        response["details"] = error_dict["details"]
    
    return response