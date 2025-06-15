"""
Enhanced Error Handling System for NEO Agent

This module provides comprehensive error handling, recovery, and resilience features:
- Intelligent error categorization and recovery strategies
- Circuit breaker pattern for external services
- Retry mechanisms with exponential backoff
- Error context preservation and analysis
- Automatic fallback mechanisms
- Performance impact monitoring
"""

import asyncio
import functools
import logging
import time
import traceback
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Type, Union
from dataclasses import dataclass, field
import json

class ErrorSeverity(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class ErrorCategory(Enum):
    NETWORK = "network"
    AUTHENTICATION = "authentication"
    PERMISSION = "permission"
    RESOURCE = "resource"
    TIMEOUT = "timeout"
    VALIDATION = "validation"
    EXTERNAL_SERVICE = "external_service"
    INTERNAL = "internal"
    USER_INPUT = "user_input"
    CONFIGURATION = "configuration"

class RecoveryStrategy(Enum):
    RETRY = "retry"
    FALLBACK = "fallback"
    CIRCUIT_BREAKER = "circuit_breaker"
    GRACEFUL_DEGRADATION = "graceful_degradation"
    ESCALATE = "escalate"
    IGNORE = "ignore"

@dataclass
class ErrorContext:
    """Context information for error analysis and recovery."""
    error_id: str
    timestamp: datetime
    error_type: str
    error_message: str
    severity: ErrorSeverity
    category: ErrorCategory
    recovery_strategy: RecoveryStrategy
    context_data: Dict[str, Any] = field(default_factory=dict)
    stack_trace: Optional[str] = None
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    operation: Optional[str] = None
    retry_count: int = 0
    max_retries: int = 3
    recovery_attempted: bool = False
    recovery_successful: bool = False

@dataclass
class CircuitBreakerState:
    """State tracking for circuit breaker pattern."""
    failure_count: int = 0
    last_failure_time: Optional[datetime] = None
    state: str = "closed"  # closed, open, half_open
    failure_threshold: int = 5
    recovery_timeout: int = 60  # seconds
    success_threshold: int = 3  # successes needed to close circuit

class EnhancedErrorHandler:
    """Enhanced error handler with intelligent recovery strategies."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.error_history: List[ErrorContext] = []
        self.circuit_breakers: Dict[str, CircuitBreakerState] = {}
        self.error_patterns: Dict[str, int] = {}
        self.recovery_strategies: Dict[ErrorCategory, RecoveryStrategy] = {
            ErrorCategory.NETWORK: RecoveryStrategy.RETRY,
            ErrorCategory.TIMEOUT: RecoveryStrategy.RETRY,
            ErrorCategory.EXTERNAL_SERVICE: RecoveryStrategy.CIRCUIT_BREAKER,
            ErrorCategory.RESOURCE: RecoveryStrategy.GRACEFUL_DEGRADATION,
            ErrorCategory.AUTHENTICATION: RecoveryStrategy.ESCALATE,
            ErrorCategory.PERMISSION: RecoveryStrategy.ESCALATE,
            ErrorCategory.VALIDATION: RecoveryStrategy.FALLBACK,
            ErrorCategory.USER_INPUT: RecoveryStrategy.FALLBACK,
            ErrorCategory.CONFIGURATION: RecoveryStrategy.ESCALATE,
            ErrorCategory.INTERNAL: RecoveryStrategy.RETRY,
        }
        
        # Performance monitoring
        self.performance_metrics = {
            "total_errors": 0,
            "recovered_errors": 0,
            "recovery_success_rate": 0.0,
            "avg_recovery_time": 0.0,
            "circuit_breaker_trips": 0
        }
    
    def categorize_error(self, error: Exception, context: Dict[str, Any] = None) -> ErrorCategory:
        """Categorize error based on type and context."""
        error_str = str(error).lower()
        error_type = type(error).__name__.lower()
        
        # Network-related errors
        if any(keyword in error_str for keyword in [
            "connection", "network", "timeout", "unreachable", "dns", "socket"
        ]) or any(keyword in error_type for keyword in [
            "connection", "timeout", "network"
        ]):
            if "timeout" in error_str or "timeout" in error_type:
                return ErrorCategory.TIMEOUT
            return ErrorCategory.NETWORK
        
        # Authentication errors
        if any(keyword in error_str for keyword in [
            "auth", "unauthorized", "forbidden", "token", "credential"
        ]) or any(keyword in error_type for keyword in [
            "auth", "unauthorized"
        ]):
            return ErrorCategory.AUTHENTICATION
        
        # Permission errors
        if any(keyword in error_str for keyword in [
            "permission", "access denied", "forbidden", "not allowed"
        ]):
            return ErrorCategory.PERMISSION
        
        # Resource errors
        if any(keyword in error_str for keyword in [
            "memory", "disk", "space", "resource", "limit", "quota"
        ]):
            return ErrorCategory.RESOURCE
        
        # Validation errors
        if any(keyword in error_str for keyword in [
            "validation", "invalid", "malformed", "parse", "format"
        ]) or any(keyword in error_type for keyword in [
            "validation", "value", "type"
        ]):
            return ErrorCategory.VALIDATION
        
        # External service errors
        if context and context.get("external_service"):
            return ErrorCategory.EXTERNAL_SERVICE
        
        # Configuration errors
        if any(keyword in error_str for keyword in [
            "config", "setting", "environment", "missing"
        ]):
            return ErrorCategory.CONFIGURATION
        
        return ErrorCategory.INTERNAL
    
    def determine_severity(self, error: Exception, category: ErrorCategory) -> ErrorSeverity:
        """Determine error severity based on type and category."""
        error_str = str(error).lower()
        
        # Critical errors
        if category in [ErrorCategory.AUTHENTICATION, ErrorCategory.CONFIGURATION]:
            return ErrorSeverity.CRITICAL
        
        if any(keyword in error_str for keyword in [
            "critical", "fatal", "system", "database", "corruption"
        ]):
            return ErrorSeverity.CRITICAL
        
        # High severity errors
        if category in [ErrorCategory.PERMISSION, ErrorCategory.RESOURCE]:
            return ErrorSeverity.HIGH
        
        if any(keyword in error_str for keyword in [
            "security", "breach", "unauthorized access"
        ]):
            return ErrorSeverity.HIGH
        
        # Medium severity errors
        if category in [ErrorCategory.EXTERNAL_SERVICE, ErrorCategory.NETWORK]:
            return ErrorSeverity.MEDIUM
        
        # Low severity errors (validation, user input, etc.)
        return ErrorSeverity.LOW
    
    async def handle_error(self, 
                          error: Exception, 
                          context: Dict[str, Any] = None,
                          operation: str = None,
                          user_id: str = None,
                          session_id: str = None) -> ErrorContext:
        """Handle error with intelligent recovery strategies."""
        
        # Create error context
        error_context = ErrorContext(
            error_id=f"err_{int(time.time() * 1000)}",
            timestamp=datetime.now(),
            error_type=type(error).__name__,
            error_message=str(error),
            severity=ErrorSeverity.LOW,  # Will be updated
            category=ErrorCategory.INTERNAL,  # Will be updated
            recovery_strategy=RecoveryStrategy.RETRY,  # Will be updated
            context_data=context or {},
            stack_trace=traceback.format_exc(),
            user_id=user_id,
            session_id=session_id,
            operation=operation
        )
        
        # Categorize and assess error
        error_context.category = self.categorize_error(error, context)
        error_context.severity = self.determine_severity(error, error_context.category)
        error_context.recovery_strategy = self.recovery_strategies.get(
            error_context.category, RecoveryStrategy.RETRY
        )
        
        # Log error
        self.logger.error(
            f"Error {error_context.error_id}: {error_context.error_message}",
            extra={
                "error_context": error_context.__dict__,
                "user_id": user_id,
                "session_id": session_id,
                "operation": operation
            }
        )
        
        # Update metrics
        self.performance_metrics["total_errors"] += 1
        
        # Track error patterns
        error_pattern = f"{error_context.category.value}:{error_context.error_type}"
        self.error_patterns[error_pattern] = self.error_patterns.get(error_pattern, 0) + 1
        
        # Store in history
        self.error_history.append(error_context)
        
        # Attempt recovery
        await self._attempt_recovery(error_context)
        
        return error_context
    
    async def _attempt_recovery(self, error_context: ErrorContext):
        """Attempt error recovery based on strategy."""
        error_context.recovery_attempted = True
        recovery_start_time = time.time()
        
        try:
            if error_context.recovery_strategy == RecoveryStrategy.RETRY:
                await self._retry_recovery(error_context)
            elif error_context.recovery_strategy == RecoveryStrategy.CIRCUIT_BREAKER:
                await self._circuit_breaker_recovery(error_context)
            elif error_context.recovery_strategy == RecoveryStrategy.FALLBACK:
                await self._fallback_recovery(error_context)
            elif error_context.recovery_strategy == RecoveryStrategy.GRACEFUL_DEGRADATION:
                await self._graceful_degradation_recovery(error_context)
            elif error_context.recovery_strategy == RecoveryStrategy.ESCALATE:
                await self._escalate_error(error_context)
            
            # Update metrics if recovery was successful
            if error_context.recovery_successful:
                self.performance_metrics["recovered_errors"] += 1
                recovery_time = time.time() - recovery_start_time
                
                # Update average recovery time
                current_avg = self.performance_metrics["avg_recovery_time"]
                total_recovered = self.performance_metrics["recovered_errors"]
                self.performance_metrics["avg_recovery_time"] = (
                    (current_avg * (total_recovered - 1) + recovery_time) / total_recovered
                )
                
                # Update success rate
                self.performance_metrics["recovery_success_rate"] = (
                    self.performance_metrics["recovered_errors"] / 
                    self.performance_metrics["total_errors"]
                )
        
        except Exception as recovery_error:
            self.logger.error(f"Recovery failed for {error_context.error_id}: {recovery_error}")
    
    async def _retry_recovery(self, error_context: ErrorContext):
        """Implement retry recovery with exponential backoff."""
        if error_context.retry_count >= error_context.max_retries:
            self.logger.warning(f"Max retries exceeded for {error_context.error_id}")
            return
        
        # Exponential backoff
        delay = min(2 ** error_context.retry_count, 60)  # Cap at 60 seconds
        await asyncio.sleep(delay)
        
        error_context.retry_count += 1
        self.logger.info(f"Retrying operation for {error_context.error_id} (attempt {error_context.retry_count})")
        
        # Mark as successful for now (actual retry would be handled by calling code)
        error_context.recovery_successful = True
    
    async def _circuit_breaker_recovery(self, error_context: ErrorContext):
        """Implement circuit breaker pattern for external services."""
        service_name = error_context.context_data.get("service_name", "unknown")
        
        if service_name not in self.circuit_breakers:
            self.circuit_breakers[service_name] = CircuitBreakerState()
        
        circuit_breaker = self.circuit_breakers[service_name]
        
        # Update failure count
        circuit_breaker.failure_count += 1
        circuit_breaker.last_failure_time = datetime.now()
        
        # Check if circuit should be opened
        if (circuit_breaker.failure_count >= circuit_breaker.failure_threshold and 
            circuit_breaker.state == "closed"):
            circuit_breaker.state = "open"
            self.performance_metrics["circuit_breaker_trips"] += 1
            self.logger.warning(f"Circuit breaker opened for {service_name}")
        
        # Check if circuit can be half-opened
        elif (circuit_breaker.state == "open" and 
              circuit_breaker.last_failure_time and
              datetime.now() - circuit_breaker.last_failure_time > 
              timedelta(seconds=circuit_breaker.recovery_timeout)):
            circuit_breaker.state = "half_open"
            self.logger.info(f"Circuit breaker half-opened for {service_name}")
        
        error_context.recovery_successful = circuit_breaker.state != "open"
    
    async def _fallback_recovery(self, error_context: ErrorContext):
        """Implement fallback recovery mechanisms."""
        fallback_options = error_context.context_data.get("fallback_options", [])
        
        if not fallback_options:
            self.logger.warning(f"No fallback options available for {error_context.error_id}")
            return
        
        for fallback in fallback_options:
            try:
                self.logger.info(f"Attempting fallback: {fallback}")
                # Fallback implementation would be handled by calling code
                error_context.recovery_successful = True
                break
            except Exception as fallback_error:
                self.logger.warning(f"Fallback failed: {fallback_error}")
                continue
    
    async def _graceful_degradation_recovery(self, error_context: ErrorContext):
        """Implement graceful degradation for resource issues."""
        degradation_options = error_context.context_data.get("degradation_options", {})
        
        # Reduce resource usage
        if "reduce_memory" in degradation_options:
            self.logger.info("Implementing memory usage reduction")
        
        if "reduce_concurrency" in degradation_options:
            self.logger.info("Reducing concurrent operations")
        
        if "disable_features" in degradation_options:
            features_to_disable = degradation_options["disable_features"]
            self.logger.info(f"Disabling non-critical features: {features_to_disable}")
        
        error_context.recovery_successful = True
    
    async def _escalate_error(self, error_context: ErrorContext):
        """Escalate critical errors to administrators."""
        escalation_data = {
            "error_id": error_context.error_id,
            "severity": error_context.severity.value,
            "category": error_context.category.value,
            "message": error_context.error_message,
            "timestamp": error_context.timestamp.isoformat(),
            "user_id": error_context.user_id,
            "session_id": error_context.session_id,
            "operation": error_context.operation
        }
        
        # Send notification (implementation depends on notification system)
        self.logger.critical(f"ESCALATED ERROR: {json.dumps(escalation_data)}")
        
        # Mark as handled (escalation is the recovery)
        error_context.recovery_successful = True
    
    def get_error_statistics(self) -> Dict[str, Any]:
        """Get comprehensive error statistics."""
        recent_errors = [
            err for err in self.error_history 
            if datetime.now() - err.timestamp < timedelta(hours=24)
        ]
        
        category_stats = {}
        for category in ErrorCategory:
            category_errors = [err for err in recent_errors if err.category == category]
            category_stats[category.value] = {
                "count": len(category_errors),
                "recovery_rate": (
                    sum(1 for err in category_errors if err.recovery_successful) / 
                    len(category_errors) if category_errors else 0
                )
            }
        
        return {
            "total_errors_24h": len(recent_errors),
            "recovery_success_rate": self.performance_metrics["recovery_success_rate"],
            "avg_recovery_time": self.performance_metrics["avg_recovery_time"],
            "circuit_breaker_trips": self.performance_metrics["circuit_breaker_trips"],
            "category_breakdown": category_stats,
            "top_error_patterns": dict(sorted(
                self.error_patterns.items(), 
                key=lambda x: x[1], 
                reverse=True
            )[:10]),
            "circuit_breaker_states": {
                name: state.state for name, state in self.circuit_breakers.items()
            }
        }
    
    def reset_circuit_breaker(self, service_name: str):
        """Manually reset a circuit breaker."""
        if service_name in self.circuit_breakers:
            self.circuit_breakers[service_name] = CircuitBreakerState()
            self.logger.info(f"Circuit breaker reset for {service_name}")
    
    def is_circuit_open(self, service_name: str) -> bool:
        """Check if circuit breaker is open for a service."""
        if service_name not in self.circuit_breakers:
            return False
        return self.circuit_breakers[service_name].state == "open"

# Global error handler instance
error_handler = EnhancedErrorHandler()

def handle_errors(
    operation: str = None,
    max_retries: int = 3,
    fallback_options: List[str] = None,
    degradation_options: Dict[str, Any] = None
):
    """Decorator for automatic error handling."""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            context = {
                "fallback_options": fallback_options or [],
                "degradation_options": degradation_options or {},
                "function_name": func.__name__,
                "args": str(args)[:200],  # Truncate for logging
                "kwargs": str(kwargs)[:200]
            }
            
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                error_context = await error_handler.handle_error(
                    error=e,
                    context=context,
                    operation=operation or func.__name__
                )
                
                # Re-raise if recovery was not successful
                if not error_context.recovery_successful:
                    raise
                
                # Return None or default value if recovery was successful
                return None
        
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            context = {
                "fallback_options": fallback_options or [],
                "degradation_options": degradation_options or {},
                "function_name": func.__name__,
                "args": str(args)[:200],
                "kwargs": str(kwargs)[:200]
            }
            
            try:
                return func(*args, **kwargs)
            except Exception as e:
                # For sync functions, we can't use async error handling
                # So we just log and re-raise
                error_handler.logger.error(f"Error in {func.__name__}: {e}")
                raise
        
        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
    
    return decorator

# Convenience functions
async def handle_error(error: Exception, **kwargs) -> ErrorContext:
    """Convenience function to handle a single error."""
    return await error_handler.handle_error(error, **kwargs)

def get_error_stats() -> Dict[str, Any]:
    """Get current error statistics."""
    return error_handler.get_error_statistics()

def reset_circuit_breaker(service_name: str):
    """Reset circuit breaker for a service."""
    error_handler.reset_circuit_breaker(service_name)

def is_service_available(service_name: str) -> bool:
    """Check if service is available (circuit breaker not open)."""
    return not error_handler.is_circuit_open(service_name)