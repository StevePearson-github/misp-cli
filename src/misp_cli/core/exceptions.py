"""Custom exceptions for MISP CLI."""

from typing import Any, Dict, Optional


class MISPError(Exception):
    """Base exception for MISP CLI errors."""
    
    def __init__(
        self,
        message: str,
        exit_code: int = 1,
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message)
        self.message = message
        self.exit_code = exit_code
        self.details = details or {}
    
    def __str__(self) -> str:
        return self.message


class MISPConfigurationError(MISPError):
    """Configuration file or environment errors."""
    
    def __init__(
        self,
        message: str,
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message, exit_code=2, details=details)


class MISPAPIError(MISPError):
    """MISP API response errors."""
    
    def __init__(
        self,
        message: str,
        status_code: int,
        response_body: Optional[str] = None,
        error_type: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message, exit_code=3, details=details)
        self.status_code = status_code
        self.response_body = response_body
        self.error_type = error_type or "API Error"
    
    def __str__(self) -> str:
        base = super().__str__()
        return f"{self.error_type}: {base}"


class MISPConnectionError(MISPError):
    """Network connection errors."""
    
    def __init__(
        self,
        message: str,
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message, exit_code=4, details=details)


class MISPAuthenticationError(MISPAPIError):
    """Authentication/authorization errors."""
    
    # Permission-related error messages
    PERMISSION_ERRORS = {
        "Permission denied": "You don't have permission to perform this action. Contact your MISP administrator to request the required role/permissions.",
        "Access denied": "Access denied. Your current role may not have sufficient privileges.",
        "Role": "Your user role doesn't have the required permissions.",
        "Admin": "This action requires administrator privileges.",
        "readonly": "The system is in read-only mode. Changes are not allowed.",
    }
    
    def __init__(
        self,
        message: str,
        status_code: int = 401,
        response_body: Optional[str] = None,
        error_type: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        # Enhance message with suggestions for permission errors
        enhanced_message = message
        for error_pattern, suggestion in self.PERMISSION_ERRORS.items():
            if error_pattern.lower() in message.lower():
                enhanced_message = f"{message}\nSuggestion: {suggestion}"
                break
        
        super().__init__(
            enhanced_message,
            status_code=status_code,
            response_body=response_body,
            error_type=error_type or "Authentication Error",
            details=details,
        )
        self.exit_code = 5
    
    def __str__(self) -> str:
        base = super().__str__()
        # Clean up duplicate suggestions
        lines = base.split('\n')
        if len(lines) > 1:
            return f"{lines[0]}\n{lines[1]}"
        return base


class MISPValidationError(MISPError):
    """Input validation errors."""
    
    def __init__(
        self,
        message: str,
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message, exit_code=6, details=details)


class MISPNotFoundError(MISPAPIError):
    """Resource not found errors."""
    
    def __init__(
        self,
        resource_type: str,
        resource_id: str,
        response_body: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        message = f"{resource_type} '{resource_id}' not found"
        super().__init__(
            message,
            status_code=404,
            response_body=response_body,
            error_type="Not Found",
            details=details,
        )
        self.exit_code = 7
        self.resource_type = resource_type
        self.resource_id = resource_id


class MISPRateLimitError(MISPAPIError):
    """Rate limiting errors."""
    
    def __init__(
        self,
        message: str = "Rate limit exceeded",
        retry_after: int = 60,
        status_code: int = 429,
        response_body: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            message,
            status_code=status_code,
            response_body=response_body,
            error_type="Rate Limit Exceeded",
            details=details,
        )
        self.retry_after = retry_after
        self.exit_code = 8
    
    def __str__(self) -> str:
        base = super().__str__()
        return f"{base} (retry after {self.retry_after}s)"


class MISPOutputError(MISPError):
    """Output formatting errors."""
    
    def __init__(
        self,
        message: str,
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message, exit_code=9, details=details)
