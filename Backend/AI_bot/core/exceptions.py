"""
Custom Exceptions for Real Estate AI Agent System

This module defines all custom exceptions used throughout the system,
providing clear error handling and debugging information.
"""

from typing import Any, Dict, Optional


class AgentSystemError(Exception):
    """Base exception for all agent system errors."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}
        self.error_code = getattr(self, 'ERROR_CODE', 'UNKNOWN_ERROR')
    
    def __str__(self):
        if self.details:
            return f"{self.message} - Details: {self.details}"
        return self.message


class AgentError(AgentSystemError):
    """Base exception for agent-specific errors."""
    ERROR_CODE = "AGENT_ERROR"


class AgentTimeoutError(AgentError):
    """Raised when an agent operation exceeds the configured timeout."""
    ERROR_CODE = "AGENT_TIMEOUT"
    
    def __init__(self, message: str, timeout_seconds: int, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, details)
        self.timeout_seconds = timeout_seconds


class AgentCommunicationError(AgentError):
    """Raised when there are issues with inter-agent communication."""
    ERROR_CODE = "AGENT_COMMUNICATION_ERROR"


class AgentInitializationError(AgentError):
    """Raised when an agent fails to initialize properly."""
    ERROR_CODE = "AGENT_INITIALIZATION_ERROR"


class AgentConfigurationError(AgentError):
    """Raised when there are issues with agent configuration."""
    ERROR_CODE = "AGENT_CONFIGURATION_ERROR"


class ValidationError(AgentSystemError):
    """Raised when input validation fails."""
    ERROR_CODE = "VALIDATION_ERROR"
    
    def __init__(self, message: str, field: Optional[str] = None, value: Optional[Any] = None):
        super().__init__(message)
        self.field = field
        self.value = value


class DataSourceError(AgentSystemError):
    """Raised when there are issues with external data sources."""
    ERROR_CODE = "DATA_SOURCE_ERROR"
    
    def __init__(self, message: str, source: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, details)
        self.source = source


class WorkflowError(AgentSystemError):
    """Raised when there are issues with workflow execution."""
    ERROR_CODE = "WORKFLOW_ERROR"
    
    def __init__(self, message: str, workflow_id: str, step: Optional[str] = None):
        super().__init__(message)
        self.workflow_id = workflow_id
        self.step = step


class WorkflowTimeoutError(WorkflowError):
    """Raised when a workflow exceeds its execution time limit."""
    ERROR_CODE = "WORKFLOW_TIMEOUT"
    
    def __init__(self, message: str, workflow_id: str, timeout_seconds: int):
        super().__init__(message, workflow_id)
        self.timeout_seconds = timeout_seconds


class WorkflowValidationError(WorkflowError):
    """Raised when workflow validation fails."""
    ERROR_CODE = "WORKFLOW_VALIDATION_ERROR"


class AuthenticationError(AgentSystemError):
    """Raised when authentication fails."""
    ERROR_CODE = "AUTHENTICATION_ERROR"
    
    def __init__(self, message: str, user_id: Optional[str] = None):
        super().__init__(message)
        self.user_id = user_id


class AuthorizationError(AgentSystemError):
    """Raised when authorization fails."""
    ERROR_CODE = "AUTHORIZATION_ERROR"
    
    def __init__(self, message: str, user_id: str, required_permission: str):
        super().__init__(message)
        self.user_id = user_id
        self.required_permission = required_permission


class RateLimitError(AgentSystemError):
    """Raised when rate limits are exceeded."""
    ERROR_CODE = "RATE_LIMIT_ERROR"
    
    def __init__(self, message: str, retry_after: Optional[int] = None):
        super().__init__(message)
        self.retry_after = retry_after


class ResourceNotFoundError(AgentSystemError):
    """Raised when a requested resource is not found."""
    ERROR_CODE = "RESOURCE_NOT_FOUND"
    
    def __init__(self, message: str, resource_type: str, resource_id: str):
        super().__init__(message)
        self.resource_type = resource_type
        self.resource_id = resource_id


class DatabaseError(AgentSystemError):
    """Raised when there are database-related errors."""
    ERROR_CODE = "DATABASE_ERROR"
    
    def __init__(self, message: str, operation: str, table: Optional[str] = None):
        super().__init__(message)
        self.operation = operation
        self.table = table


class ExternalServiceError(AgentSystemError):
    """Raised when external service calls fail."""
    ERROR_CODE = "EXTERNAL_SERVICE_ERROR"
    
    def __init__(self, message: str, service: str, status_code: Optional[int] = None):
        super().__init__(message)
        self.service = service
        self.status_code = status_code


class ModelError(AgentSystemError):
    """Raised when there are issues with AI model operations."""
    ERROR_CODE = "MODEL_ERROR"
    
    def __init__(self, message: str, model: str, operation: str):
        super().__init__(message)
        self.model = model
        self.operation = operation


class ConfigurationError(AgentSystemError):
    """Raised when there are configuration-related errors."""
    ERROR_CODE = "CONFIGURATION_ERROR"
    
    def __init__(self, message: str, config_key: Optional[str] = None):
        super().__init__(message)
        self.config_key = config_key


class SerializationError(AgentSystemError):
    """Raised when serialization/deserialization fails."""
    ERROR_CODE = "SERIALIZATION_ERROR"
    
    def __init__(self, message: str, data_type: str, operation: str):
        super().__init__(message)
        self.data_type = data_type
        self.operation = operation


# Error mapping for easy lookup
ERROR_MAPPING = {
    "AGENT_ERROR": AgentError,
    "AGENT_TIMEOUT": AgentTimeoutError,
    "AGENT_COMMUNICATION_ERROR": AgentCommunicationError,
    "AGENT_INITIALIZATION_ERROR": AgentInitializationError,
    "AGENT_CONFIGURATION_ERROR": AgentConfigurationError,
    "VALIDATION_ERROR": ValidationError,
    "DATA_SOURCE_ERROR": DataSourceError,
    "WORKFLOW_ERROR": WorkflowError,
    "WORKFLOW_TIMEOUT": WorkflowTimeoutError,
    "WORKFLOW_VALIDATION_ERROR": WorkflowValidationError,
    "AUTHENTICATION_ERROR": AuthenticationError,
    "AUTHORIZATION_ERROR": AuthorizationError,
    "RATE_LIMIT_ERROR": RateLimitError,
    "RESOURCE_NOT_FOUND": ResourceNotFoundError,
    "DATABASE_ERROR": DatabaseError,
    "EXTERNAL_SERVICE_ERROR": ExternalServiceError,
    "MODEL_ERROR": ModelError,
    "CONFIGURATION_ERROR": ConfigurationError,
    "SERIALIZATION_ERROR": SerializationError,
}


def create_error(error_code: str, message: str, **kwargs) -> AgentSystemError:
    """
    Factory function to create appropriate exception instances.
    
    Args:
        error_code: The error code to look up
        message: The error message
        **kwargs: Additional arguments for the exception
        
    Returns:
        An instance of the appropriate exception class
        
    Raises:
        ValueError: If the error code is not recognized
    """
    if error_code not in ERROR_MAPPING:
        raise ValueError(f"Unknown error code: {error_code}")
    
    exception_class = ERROR_MAPPING[error_code]
    return exception_class(message, **kwargs)
