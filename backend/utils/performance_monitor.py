"""
Performance Monitoring System for NEO Agent

This module provides comprehensive performance monitoring and optimization:
- Real-time performance metrics collection
- Resource usage tracking (CPU, memory, disk, network)
- Response time monitoring
- Throughput analysis
- Performance bottleneck detection
- Automatic optimization suggestions
- Performance alerts and notifications
"""

import asyncio
import time
import threading
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from collections import deque
import json

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False

@dataclass
class PerformanceMetric:
    """Individual performance metric data point."""
    timestamp: datetime
    metric_name: str
    value: float
    unit: str
    tags: Dict[str, str] = field(default_factory=dict)

@dataclass
class ResourceUsage:
    """System resource usage snapshot."""
    timestamp: datetime
    cpu_percent: float
    memory_percent: float
    memory_used_mb: float
    memory_available_mb: float
    disk_usage_percent: float
    disk_free_gb: float
    network_bytes_sent: int = 0
    network_bytes_recv: int = 0

@dataclass
class OperationMetrics:
    """Metrics for a specific operation."""
    operation_name: str
    total_calls: int = 0
    successful_calls: int = 0
    failed_calls: int = 0
    total_duration: float = 0.0
    min_duration: float = float('inf')
    max_duration: float = 0.0
    avg_duration: float = 0.0
    last_call_time: Optional[datetime] = None
    error_rate: float = 0.0
    throughput_per_second: float = 0.0

class PerformanceMonitor:
    """Comprehensive performance monitoring system."""
    
    def __init__(self, max_history_size: int = 1000):
        self.logger = logging.getLogger(__name__)
        self.max_history_size = max_history_size
        
        # Metrics storage
        self.metrics_history: deque = deque(maxlen=max_history_size)
        self.resource_history: deque = deque(maxlen=max_history_size)
        self.operation_metrics: Dict[str, OperationMetrics] = {}
        
        # Monitoring state
        self.monitoring_active = False
        self.monitoring_interval = 10  # seconds
        self.monitoring_thread: Optional[threading.Thread] = None
        
        # Performance thresholds
        self.thresholds = {
            "cpu_percent": 80.0,
            "memory_percent": 85.0,
            "disk_usage_percent": 90.0,
            "response_time_ms": 5000.0,
            "error_rate": 0.05  # 5%
        }
        
        # Alert callbacks
        self.alert_callbacks: List[Callable] = []
        
        # Performance optimization suggestions
        self.optimization_suggestions: List[str] = []
        
        # Start monitoring if psutil is available
        if PSUTIL_AVAILABLE:
            self.start_monitoring()
    
    def start_monitoring(self):
        """Start background performance monitoring."""
        if self.monitoring_active:
            return
        
        self.monitoring_active = True
        self.monitoring_thread = threading.Thread(
            target=self._monitoring_loop,
            daemon=True
        )
        self.monitoring_thread.start()
        self.logger.info("Performance monitoring started")
    
    def stop_monitoring(self):
        """Stop background performance monitoring."""
        self.monitoring_active = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=5)
        self.logger.info("Performance monitoring stopped")
    
    def _monitoring_loop(self):
        """Background monitoring loop."""
        while self.monitoring_active:
            try:
                self._collect_system_metrics()
                self._analyze_performance()
                time.sleep(self.monitoring_interval)
            except Exception as e:
                self.logger.error(f"Error in monitoring loop: {e}")
                time.sleep(self.monitoring_interval)
    
    def _collect_system_metrics(self):
        """Collect system resource metrics."""
        if not PSUTIL_AVAILABLE:
            return
        
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # Memory usage
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            memory_used_mb = memory.used / (1024 * 1024)
            memory_available_mb = memory.available / (1024 * 1024)
            
            # Disk usage
            disk = psutil.disk_usage('/')
            disk_usage_percent = (disk.used / disk.total) * 100
            disk_free_gb = disk.free / (1024 * 1024 * 1024)
            
            # Network I/O
            network = psutil.net_io_counters()
            network_bytes_sent = network.bytes_sent
            network_bytes_recv = network.bytes_recv
            
            # Create resource usage snapshot
            resource_usage = ResourceUsage(
                timestamp=datetime.now(),
                cpu_percent=cpu_percent,
                memory_percent=memory_percent,
                memory_used_mb=memory_used_mb,
                memory_available_mb=memory_available_mb,
                disk_usage_percent=disk_usage_percent,
                disk_free_gb=disk_free_gb,
                network_bytes_sent=network_bytes_sent,
                network_bytes_recv=network_bytes_recv
            )
            
            self.resource_history.append(resource_usage)
            
            # Record individual metrics
            self.record_metric("cpu_percent", cpu_percent, "percent")
            self.record_metric("memory_percent", memory_percent, "percent")
            self.record_metric("memory_used", memory_used_mb, "MB")
            self.record_metric("disk_usage_percent", disk_usage_percent, "percent")
            self.record_metric("disk_free", disk_free_gb, "GB")
            
        except Exception as e:
            self.logger.error(f"Error collecting system metrics: {e}")
    
    def record_metric(self, name: str, value: float, unit: str, tags: Dict[str, str] = None):
        """Record a performance metric."""
        metric = PerformanceMetric(
            timestamp=datetime.now(),
            metric_name=name,
            value=value,
            unit=unit,
            tags=tags or {}
        )
        
        self.metrics_history.append(metric)
    
    def start_operation(self, operation_name: str) -> str:
        """Start timing an operation."""
        operation_id = f"{operation_name}_{int(time.time() * 1000)}"
        
        # Initialize operation metrics if not exists
        if operation_name not in self.operation_metrics:
            self.operation_metrics[operation_name] = OperationMetrics(
                operation_name=operation_name
            )
        
        # Store start time
        setattr(self, f"_start_time_{operation_id}", time.time())
        
        return operation_id
    
    def end_operation(self, operation_id: str, success: bool = True, error: str = None):
        """End timing an operation and record metrics."""
        start_time_attr = f"_start_time_{operation_id}"
        
        if not hasattr(self, start_time_attr):
            self.logger.warning(f"No start time found for operation {operation_id}")
            return
        
        start_time = getattr(self, start_time_attr)
        duration = time.time() - start_time
        
        # Extract operation name from operation_id
        operation_name = operation_id.rsplit('_', 1)[0]
        
        # Update operation metrics
        metrics = self.operation_metrics[operation_name]
        metrics.total_calls += 1
        metrics.total_duration += duration
        metrics.last_call_time = datetime.now()
        
        if success:
            metrics.successful_calls += 1
        else:
            metrics.failed_calls += 1
        
        # Update duration statistics
        metrics.min_duration = min(metrics.min_duration, duration)
        metrics.max_duration = max(metrics.max_duration, duration)
        metrics.avg_duration = metrics.total_duration / metrics.total_calls
        
        # Update error rate
        metrics.error_rate = metrics.failed_calls / metrics.total_calls
        
        # Calculate throughput (operations per second over last minute)
        recent_calls = self._count_recent_calls(operation_name, 60)
        metrics.throughput_per_second = recent_calls / 60.0
        
        # Record metric
        self.record_metric(
            f"operation_duration_{operation_name}",
            duration * 1000,  # Convert to milliseconds
            "ms",
            {"operation": operation_name, "success": str(success)}
        )
        
        # Clean up start time
        delattr(self, start_time_attr)
        
        # Check for performance issues
        self._check_operation_performance(operation_name, duration, success)
    
    def _count_recent_calls(self, operation_name: str, seconds: int) -> int:
        """Count recent calls for an operation within specified seconds."""
        if operation_name not in self.operation_metrics:
            return 0
        
        metrics = self.operation_metrics[operation_name]
        if not metrics.last_call_time:
            return 0
        
        # This is a simplified implementation
        # In a real system, you'd track individual call timestamps
        cutoff_time = datetime.now() - timedelta(seconds=seconds)
        
        # For now, estimate based on average call rate
        if metrics.last_call_time > cutoff_time:
            return min(metrics.total_calls, int(metrics.throughput_per_second * seconds))
        
        return 0
    
    def _check_operation_performance(self, operation_name: str, duration: float, success: bool):
        """Check operation performance against thresholds."""
        duration_ms = duration * 1000
        
        # Check response time threshold
        if duration_ms > self.thresholds["response_time_ms"]:
            self._trigger_alert(
                "high_response_time",
                f"Operation {operation_name} took {duration_ms:.2f}ms (threshold: {self.thresholds['response_time_ms']}ms)"
            )
        
        # Check error rate
        metrics = self.operation_metrics[operation_name]
        if metrics.error_rate > self.thresholds["error_rate"]:
            self._trigger_alert(
                "high_error_rate",
                f"Operation {operation_name} has error rate {metrics.error_rate:.2%} (threshold: {self.thresholds['error_rate']:.2%})"
            )
    
    def _analyze_performance(self):
        """Analyze current performance and generate insights."""
        if not self.resource_history:
            return
        
        latest_resource = self.resource_history[-1]
        
        # Check resource thresholds
        if latest_resource.cpu_percent > self.thresholds["cpu_percent"]:
            self._trigger_alert(
                "high_cpu_usage",
                f"CPU usage is {latest_resource.cpu_percent:.1f}% (threshold: {self.thresholds['cpu_percent']}%)"
            )
        
        if latest_resource.memory_percent > self.thresholds["memory_percent"]:
            self._trigger_alert(
                "high_memory_usage",
                f"Memory usage is {latest_resource.memory_percent:.1f}% (threshold: {self.thresholds['memory_percent']}%)"
            )
        
        if latest_resource.disk_usage_percent > self.thresholds["disk_usage_percent"]:
            self._trigger_alert(
                "high_disk_usage",
                f"Disk usage is {latest_resource.disk_usage_percent:.1f}% (threshold: {self.thresholds['disk_usage_percent']}%)"
            )
        
        # Generate optimization suggestions
        self._generate_optimization_suggestions()
    
    def _generate_optimization_suggestions(self):
        """Generate performance optimization suggestions."""
        suggestions = []
        
        if not self.resource_history:
            return
        
        latest_resource = self.resource_history[-1]
        
        # CPU optimization suggestions
        if latest_resource.cpu_percent > 70:
            suggestions.append("Consider reducing concurrent operations or optimizing CPU-intensive tasks")
        
        # Memory optimization suggestions
        if latest_resource.memory_percent > 75:
            suggestions.append("Consider implementing memory caching strategies or reducing memory footprint")
        
        # Disk optimization suggestions
        if latest_resource.disk_usage_percent > 80:
            suggestions.append("Consider cleaning up temporary files or implementing log rotation")
        
        # Operation-specific suggestions
        for operation_name, metrics in self.operation_metrics.items():
            if metrics.avg_duration > 2.0:  # 2 seconds
                suggestions.append(f"Operation '{operation_name}' is slow (avg: {metrics.avg_duration:.2f}s) - consider optimization")
            
            if metrics.error_rate > 0.02:  # 2%
                suggestions.append(f"Operation '{operation_name}' has high error rate ({metrics.error_rate:.2%}) - investigate causes")
        
        # Update suggestions (keep only recent unique suggestions)
        for suggestion in suggestions:
            if suggestion not in self.optimization_suggestions:
                self.optimization_suggestions.append(suggestion)
        
        # Keep only last 10 suggestions
        self.optimization_suggestions = self.optimization_suggestions[-10:]
    
    def _trigger_alert(self, alert_type: str, message: str):
        """Trigger performance alert."""
        alert_data = {
            "type": alert_type,
            "message": message,
            "timestamp": datetime.now().isoformat(),
            "severity": "warning"
        }
        
        self.logger.warning(f"Performance Alert: {message}")
        
        # Call registered alert callbacks
        for callback in self.alert_callbacks:
            try:
                callback(alert_data)
            except Exception as e:
                self.logger.error(f"Error in alert callback: {e}")
    
    def add_alert_callback(self, callback: Callable):
        """Add callback for performance alerts."""
        self.alert_callbacks.append(callback)
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get comprehensive performance summary."""
        summary = {
            "timestamp": datetime.now().isoformat(),
            "monitoring_active": self.monitoring_active,
            "system_resources": {},
            "operations": {},
            "alerts": [],
            "optimization_suggestions": self.optimization_suggestions.copy()
        }
        
        # Latest system resources
        if self.resource_history:
            latest = self.resource_history[-1]
            summary["system_resources"] = {
                "cpu_percent": latest.cpu_percent,
                "memory_percent": latest.memory_percent,
                "memory_used_mb": latest.memory_used_mb,
                "memory_available_mb": latest.memory_available_mb,
                "disk_usage_percent": latest.disk_usage_percent,
                "disk_free_gb": latest.disk_free_gb
            }
        
        # Operation metrics
        for operation_name, metrics in self.operation_metrics.items():
            summary["operations"][operation_name] = {
                "total_calls": metrics.total_calls,
                "successful_calls": metrics.successful_calls,
                "failed_calls": metrics.failed_calls,
                "avg_duration_ms": metrics.avg_duration * 1000,
                "min_duration_ms": metrics.min_duration * 1000 if metrics.min_duration != float('inf') else 0,
                "max_duration_ms": metrics.max_duration * 1000,
                "error_rate": metrics.error_rate,
                "throughput_per_second": metrics.throughput_per_second,
                "last_call": metrics.last_call_time.isoformat() if metrics.last_call_time else None
            }
        
        return summary
    
    def get_metrics_for_period(self, hours: int = 1) -> List[PerformanceMetric]:
        """Get metrics for a specific time period."""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        return [
            metric for metric in self.metrics_history
            if metric.timestamp > cutoff_time
        ]
    
    def get_resource_trend(self, metric_name: str, hours: int = 1) -> List[Tuple[datetime, float]]:
        """Get trend data for a specific resource metric."""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        trend_data = []
        for resource in self.resource_history:
            if resource.timestamp > cutoff_time:
                value = getattr(resource, metric_name, None)
                if value is not None:
                    trend_data.append((resource.timestamp, value))
        
        return trend_data
    
    def reset_metrics(self):
        """Reset all collected metrics."""
        self.metrics_history.clear()
        self.resource_history.clear()
        self.operation_metrics.clear()
        self.optimization_suggestions.clear()
        self.logger.info("Performance metrics reset")
    
    def export_metrics(self, format: str = "json") -> str:
        """Export metrics in specified format."""
        data = {
            "export_timestamp": datetime.now().isoformat(),
            "summary": self.get_performance_summary(),
            "metrics_history": [
                {
                    "timestamp": metric.timestamp.isoformat(),
                    "name": metric.metric_name,
                    "value": metric.value,
                    "unit": metric.unit,
                    "tags": metric.tags
                }
                for metric in self.metrics_history
            ],
            "resource_history": [
                {
                    "timestamp": resource.timestamp.isoformat(),
                    "cpu_percent": resource.cpu_percent,
                    "memory_percent": resource.memory_percent,
                    "memory_used_mb": resource.memory_used_mb,
                    "disk_usage_percent": resource.disk_usage_percent,
                    "disk_free_gb": resource.disk_free_gb
                }
                for resource in self.resource_history
            ]
        }
        
        if format.lower() == "json":
            return json.dumps(data, indent=2)
        else:
            raise ValueError(f"Unsupported export format: {format}")

# Global performance monitor instance
performance_monitor = PerformanceMonitor()

def monitor_performance(operation_name: str = None):
    """Decorator for automatic performance monitoring."""
    def decorator(func: Callable) -> Callable:
        op_name = operation_name or func.__name__
        
        if asyncio.iscoroutinefunction(func):
            async def async_wrapper(*args, **kwargs):
                operation_id = performance_monitor.start_operation(op_name)
                try:
                    result = await func(*args, **kwargs)
                    performance_monitor.end_operation(operation_id, success=True)
                    return result
                except Exception as e:
                    performance_monitor.end_operation(operation_id, success=False, error=str(e))
                    raise
            return async_wrapper
        else:
            def sync_wrapper(*args, **kwargs):
                operation_id = performance_monitor.start_operation(op_name)
                try:
                    result = func(*args, **kwargs)
                    performance_monitor.end_operation(operation_id, success=True)
                    return result
                except Exception as e:
                    performance_monitor.end_operation(operation_id, success=False, error=str(e))
                    raise
            return sync_wrapper
    
    return decorator

# Convenience functions
def get_performance_summary() -> Dict[str, Any]:
    """Get current performance summary."""
    return performance_monitor.get_performance_summary()

def record_metric(name: str, value: float, unit: str = "", tags: Dict[str, str] = None):
    """Record a custom performance metric."""
    performance_monitor.record_metric(name, value, unit, tags)

def add_performance_alert_callback(callback: Callable):
    """Add callback for performance alerts."""
    performance_monitor.add_alert_callback(callback)