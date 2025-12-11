"""
Monitoring and alerting system for ABParts.
Provides health checks, metrics collection, and alerting capabilities.
"""

import logging
import time
import os
import json
import socket
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable
import redis
from fastapi import Request, Response
from sqlalchemy import text
from sqlalchemy.orm import Session

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("abparts.monitoring")

# Constants
HEALTH_CHECK_INTERVAL = 60  # seconds
METRICS_COLLECTION_INTERVAL = 30  # seconds
ALERT_THRESHOLD_CPU = 80  # percentage
ALERT_THRESHOLD_MEMORY = 80  # percentage
ALERT_THRESHOLD_DISK = 80  # percentage
ALERT_THRESHOLD_API_LATENCY = 2000  # milliseconds
ALERT_THRESHOLD_DB_LATENCY = 1000  # milliseconds


class HealthStatus:
    """Health status constants."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"


class MetricsCollector:
    """Collects system and application metrics."""
    
    def __init__(self):
        """Initialize metrics collector."""
        self.metrics = {
            "system": {
                "cpu_usage": 0.0,
                "memory_usage": 0.0,
                "disk_usage": 0.0,
            },
            "application": {
                "requests_per_minute": 0,
                "error_rate": 0.0,
                "average_response_time": 0.0,
            },
            "database": {
                "connection_pool_usage": 0.0,
                "average_query_time": 0.0,
                "active_connections": 0,
            },
            "redis": {
                "memory_usage": 0.0,
                "connected_clients": 0,
                "ops_per_second": 0,
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        self.request_count = 0
        self.error_count = 0
        self.response_times = []
        self.last_reset = datetime.utcnow()
    
    def collect_system_metrics(self) -> Dict[str, float]:
        """Collect system metrics (CPU, memory, disk)."""
        try:
            # This is a simplified implementation
            # In production, use psutil or similar libraries
            
            # CPU usage (simplified)
            try:
                with open('/proc/loadavg', 'r') as f:
                    load = float(f.read().split()[0])
                    cpu_count = os.cpu_count() or 1
                    cpu_usage = (load / cpu_count) * 100
            except:
                cpu_usage = 0.0
            
            # Memory usage (simplified)
            try:
                with open('/proc/meminfo', 'r') as f:
                    lines = f.readlines()
                    total = int(lines[0].split()[1])
                    free = int(lines[1].split()[1])
                    memory_usage = ((total - free) / total) * 100
            except:
                memory_usage = 0.0
            
            # Disk usage (simplified)
            try:
                stat = os.statvfs('/')
                total = stat.f_blocks * stat.f_frsize
                free = stat.f_bfree * stat.f_frsize
                disk_usage = ((total - free) / total) * 100
            except:
                disk_usage = 0.0
            
            self.metrics["system"] = {
                "cpu_usage": round(cpu_usage, 2),
                "memory_usage": round(memory_usage, 2),
                "disk_usage": round(disk_usage, 2),
            }
            
            return self.metrics["system"]
        except Exception as e:
            logger.error(f"Error collecting system metrics: {e}")
            return {
                "cpu_usage": 0.0,
                "memory_usage": 0.0,
                "disk_usage": 0.0,
            }
    
    def collect_database_metrics(self, db: Session) -> Dict[str, Any]:
        """Collect database metrics."""
        try:
            start_time = time.time()
            
            # Execute simple query to measure latency
            db.execute(text("SELECT 1"))
            query_time = time.time() - start_time
            
            # Get connection pool stats (if using SQLAlchemy)
            try:
                engine = db.get_bind()
                pool = engine.pool
                pool_size = pool.size()
                checkedin = pool.checkedin()
                checkout = pool.checkedout()
                pool_usage = checkout / pool_size if pool_size > 0 else 0
            except:
                pool_usage = 0.0
                checkedin = 0
                checkout = 0
            
            self.metrics["database"] = {
                "connection_pool_usage": round(pool_usage * 100, 2),
                "average_query_time": round(query_time * 1000, 2),  # ms
                "active_connections": checkout,
            }
            
            return self.metrics["database"]
        except Exception as e:
            logger.error(f"Error collecting database metrics: {e}")
            return {
                "connection_pool_usage": 0.0,
                "average_query_time": 0.0,
                "active_connections": 0,
            }
    
    def collect_redis_metrics(self, redis_client: redis.Redis) -> Dict[str, Any]:
        """Collect Redis metrics."""
        try:
            info = redis_client.info()
            
            self.metrics["redis"] = {
                "memory_usage": round(info.get("used_memory", 0) / (1024 * 1024), 2),  # MB
                "connected_clients": info.get("connected_clients", 0),
                "ops_per_second": info.get("instantaneous_ops_per_sec", 0),
            }
            
            return self.metrics["redis"]
        except Exception as e:
            logger.error(f"Error collecting Redis metrics: {e}")
            return {
                "memory_usage": 0.0,
                "connected_clients": 0,
                "ops_per_second": 0,
            }
    
    def track_request(self, response_time: float, is_error: bool = False):
        """Track API request metrics."""
        self.request_count += 1
        self.response_times.append(response_time)
        if is_error:
            self.error_count += 1
        
        # Reset counters every minute
        now = datetime.utcnow()
        if (now - self.last_reset).total_seconds() >= 60:
            self._calculate_request_metrics()
            self.last_reset = now
    
    def _calculate_request_metrics(self):
        """Calculate request metrics based on collected data."""
        if self.request_count > 0:
            avg_response_time = sum(self.response_times) / len(self.response_times) if self.response_times else 0
            error_rate = (self.error_count / self.request_count) * 100 if self.request_count > 0 else 0
            
            self.metrics["application"] = {
                "requests_per_minute": self.request_count,
                "error_rate": round(error_rate, 2),
                "average_response_time": round(avg_response_time * 1000, 2),  # ms
            }
        
        # Reset counters
        self.request_count = 0
        self.error_count = 0
        self.response_times = []
    
    def get_all_metrics(self) -> Dict[str, Any]:
        """Get all collected metrics."""
        self.metrics["timestamp"] = datetime.utcnow().isoformat()
        return self.metrics


class HealthChecker:
    """Performs health checks on system components."""
    
    def __init__(self, db_session_factory, redis_url: Optional[str] = None):
        """Initialize health checker."""
        self.db_session_factory = db_session_factory
        self.redis_url = redis_url
        self.health_status = {
            "status": HealthStatus.HEALTHY,
            "database": HealthStatus.HEALTHY,
            "redis": HealthStatus.HEALTHY if redis_url else "not_configured",
            "api": HealthStatus.HEALTHY,
            "timestamp": datetime.utcnow().isoformat(),
            "details": {}
        }
    
    def check_database_health(self) -> str:
        """Check database health."""
        try:
            db = self.db_session_factory()
            start_time = time.time()
            db.execute(text("SELECT 1"))
            query_time = time.time() - start_time
            
            status = HealthStatus.HEALTHY
            if query_time > 1.0:  # More than 1 second for a simple query
                status = HealthStatus.DEGRADED
            
            self.health_status["database"] = status
            self.health_status["details"]["database"] = {
                "latency_ms": round(query_time * 1000, 2),
                "connection_successful": True
            }
            
            db.close()
            return status
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            self.health_status["database"] = HealthStatus.UNHEALTHY
            self.health_status["details"]["database"] = {
                "error": str(e),
                "connection_successful": False
            }
            return HealthStatus.UNHEALTHY
    
    def check_redis_health(self) -> str:
        """Check Redis health."""
        if not self.redis_url:
            return "not_configured"
        
        try:
            redis_client = redis.StrictRedis.from_url(self.redis_url, decode_responses=True)
            start_time = time.time()
            redis_client.ping()
            ping_time = time.time() - start_time
            
            status = HealthStatus.HEALTHY
            if ping_time > 0.1:  # More than 100ms for a ping
                status = HealthStatus.DEGRADED
            
            self.health_status["redis"] = status
            self.health_status["details"]["redis"] = {
                "latency_ms": round(ping_time * 1000, 2),
                "connection_successful": True
            }
            
            return status
        except Exception as e:
            logger.error(f"Redis health check failed: {e}")
            self.health_status["redis"] = HealthStatus.UNHEALTHY
            self.health_status["details"]["redis"] = {
                "error": str(e),
                "connection_successful": False
            }
            return HealthStatus.UNHEALTHY
    
    def check_api_health(self) -> str:
        """Check API health (simplified)."""
        # In a real implementation, this might check external dependencies
        # or perform more complex self-diagnostics
        
        # For now, we'll just check if the process is running
        status = HealthStatus.HEALTHY
        self.health_status["api"] = status
        self.health_status["details"]["api"] = {
            "uptime_seconds": self._get_process_uptime()
        }
        
        return status
    
    def _get_process_uptime(self) -> float:
        """Get process uptime in seconds."""
        try:
            with open('/proc/self/stat', 'r') as f:
                stats = f.read().split()
                start_time = float(stats[21])
                uptime = time.time() - (start_time / os.sysconf(os.sysconf_names['SC_CLK_TCK']))
                return round(uptime, 2)
        except:
            return 0.0
    
    def check_all_health(self) -> Dict[str, Any]:
        """Check health of all components."""
        db_status = self.check_database_health()
        redis_status = self.check_redis_health()
        api_status = self.check_api_health()
        
        # Determine overall status
        if db_status == HealthStatus.UNHEALTHY or api_status == HealthStatus.UNHEALTHY:
            overall_status = HealthStatus.UNHEALTHY
        elif db_status == HealthStatus.DEGRADED or redis_status == HealthStatus.DEGRADED:
            overall_status = HealthStatus.DEGRADED
        else:
            overall_status = HealthStatus.HEALTHY
        
        self.health_status["status"] = overall_status
        self.health_status["timestamp"] = datetime.utcnow().isoformat()
        
        return self.health_status


class AlertManager:
    """Manages alerts based on metrics and health checks."""
    
    def __init__(self, alert_handlers: Optional[Dict[str, Callable]] = None):
        """Initialize alert manager."""
        self.alert_handlers = alert_handlers or {}
        self.active_alerts = {}
        self.resolved_alerts = []
        self.alert_history = []
    
    def add_alert_handler(self, alert_type: str, handler: Callable):
        """Add an alert handler."""
        self.alert_handlers[alert_type] = handler
    
    def check_metrics_for_alerts(self, metrics: Dict[str, Any]):
        """Check metrics for alert conditions."""
        alerts = []
        
        # Check system metrics
        system = metrics.get("system", {})
        if system.get("cpu_usage", 0) > ALERT_THRESHOLD_CPU:
            alerts.append(self._create_alert(
                "high_cpu_usage",
                f"High CPU usage: {system.get('cpu_usage')}%",
                "system",
                "warning" if system.get("cpu_usage", 0) < 90 else "critical"
            ))
        
        if system.get("memory_usage", 0) > ALERT_THRESHOLD_MEMORY:
            alerts.append(self._create_alert(
                "high_memory_usage",
                f"High memory usage: {system.get('memory_usage')}%",
                "system",
                "warning" if system.get("memory_usage", 0) < 90 else "critical"
            ))
        
        if system.get("disk_usage", 0) > ALERT_THRESHOLD_DISK:
            alerts.append(self._create_alert(
                "high_disk_usage",
                f"High disk usage: {system.get('disk_usage')}%",
                "system",
                "warning" if system.get("disk_usage", 0) < 90 else "critical"
            ))
        
        # Check application metrics
        app = metrics.get("application", {})
        if app.get("error_rate", 0) > 5.0:
            alerts.append(self._create_alert(
                "high_error_rate",
                f"High API error rate: {app.get('error_rate')}%",
                "application",
                "warning" if app.get("error_rate", 0) < 10 else "critical"
            ))
        
        if app.get("average_response_time", 0) > ALERT_THRESHOLD_API_LATENCY:
            alerts.append(self._create_alert(
                "high_api_latency",
                f"High API latency: {app.get('average_response_time')}ms",
                "application",
                "warning" if app.get("average_response_time", 0) < 5000 else "critical"
            ))
        
        # Check database metrics
        db = metrics.get("database", {})
        if db.get("average_query_time", 0) > ALERT_THRESHOLD_DB_LATENCY:
            alerts.append(self._create_alert(
                "high_db_latency",
                f"High database latency: {db.get('average_query_time')}ms",
                "database",
                "warning" if db.get("average_query_time", 0) < 2000 else "critical"
            ))
        
        if db.get("connection_pool_usage", 0) > 80:
            alerts.append(self._create_alert(
                "high_db_connection_usage",
                f"High database connection pool usage: {db.get('connection_pool_usage')}%",
                "database",
                "warning" if db.get("connection_pool_usage", 0) < 90 else "critical"
            ))
        
        # Process alerts
        for alert in alerts:
            self._process_alert(alert)
    
    def check_health_for_alerts(self, health: Dict[str, Any]):
        """Check health status for alert conditions."""
        if health["status"] == HealthStatus.UNHEALTHY:
            components = []
            if health["database"] == HealthStatus.UNHEALTHY:
                components.append("database")
            if health["redis"] == HealthStatus.UNHEALTHY:
                components.append("redis")
            if health["api"] == HealthStatus.UNHEALTHY:
                components.append("api")
            
            component_str = ", ".join(components)
            alert = self._create_alert(
                "system_unhealthy",
                f"System is unhealthy. Affected components: {component_str}",
                "system",
                "critical"
            )
            self._process_alert(alert)
        
        elif health["status"] == HealthStatus.DEGRADED:
            components = []
            if health["database"] == HealthStatus.DEGRADED:
                components.append("database")
            if health["redis"] == HealthStatus.DEGRADED:
                components.append("redis")
            
            component_str = ", ".join(components)
            alert = self._create_alert(
                "system_degraded",
                f"System performance is degraded. Affected components: {component_str}",
                "system",
                "warning"
            )
            self._process_alert(alert)
    
    def _create_alert(self, alert_id: str, message: str, category: str, severity: str) -> Dict[str, Any]:
        """Create an alert object."""
        return {
            "id": f"{alert_id}_{int(time.time())}",
            "alert_type": alert_id,
            "message": message,
            "category": category,
            "severity": severity,
            "timestamp": datetime.utcnow().isoformat(),
            "status": "active"
        }
    
    def _process_alert(self, alert: Dict[str, Any]):
        """Process an alert and trigger handlers."""
        alert_type = alert["alert_type"]
        
        # Check if this alert type is already active
        if alert_type in self.active_alerts:
            # Update existing alert
            self.active_alerts[alert_type]["count"] += 1
            self.active_alerts[alert_type]["last_occurrence"] = alert["timestamp"]
            
            # Only trigger handler if severity increased
            if alert["severity"] == "critical" and self.active_alerts[alert_type]["severity"] == "warning":
                self.active_alerts[alert_type]["severity"] = "critical"
                self._trigger_alert_handler(alert)
        else:
            # New alert
            self.active_alerts[alert_type] = {
                **alert,
                "count": 1,
                "first_occurrence": alert["timestamp"],
                "last_occurrence": alert["timestamp"]
            }
            self._trigger_alert_handler(alert)
        
        # Add to history
        self.alert_history.append(alert)
        
        # Trim history if needed
        if len(self.alert_history) > 1000:
            self.alert_history = self.alert_history[-1000:]
    
    def _trigger_alert_handler(self, alert: Dict[str, Any]):
        """Trigger the appropriate alert handler."""
        alert_type = alert["alert_type"]
        if alert_type in self.alert_handlers:
            try:
                self.alert_handlers[alert_type](alert)
            except Exception as e:
                logger.error(f"Error in alert handler for {alert_type}: {e}")
        
        # Always log the alert
        log_level = logging.CRITICAL if alert["severity"] == "critical" else logging.WARNING
        logger.log(log_level, f"ALERT: {alert['message']} [{alert['severity']}]")
    
    def resolve_alert(self, alert_type: str):
        """Resolve an active alert."""
        if alert_type in self.active_alerts:
            alert = self.active_alerts.pop(alert_type)
            alert["status"] = "resolved"
            alert["resolved_at"] = datetime.utcnow().isoformat()
            self.resolved_alerts.append(alert)
            
            # Trim resolved alerts if needed
            if len(self.resolved_alerts) > 1000:
                self.resolved_alerts = self.resolved_alerts[-1000:]
            
            logger.info(f"Alert resolved: {alert['message']}")
    
    def get_active_alerts(self) -> List[Dict[str, Any]]:
        """Get all active alerts."""
        return list(self.active_alerts.values())
    
    def get_alert_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get alert history."""
        return self.alert_history[-limit:]


class MonitoringSystem:
    """Main monitoring system that coordinates health checks, metrics, and alerts."""
    
    def __init__(self, db_session_factory, redis_url: Optional[str] = None):
        """Initialize monitoring system."""
        self.db_session_factory = db_session_factory
        self.redis_url = redis_url
        self.metrics_collector = MetricsCollector()
        self.health_checker = HealthChecker(db_session_factory, redis_url)
        self.alert_manager = AlertManager()
        
        # Set up default alert handlers
        self._setup_default_alert_handlers()
        
        # Background threads
        self.health_check_thread = None
        self.metrics_collection_thread = None
        self.running = False
    
    def _setup_default_alert_handlers(self):
        """Set up default alert handlers."""
        # In a production system, these might send emails, SMS, or integrate with systems like PagerDuty
        def log_critical_alert(alert):
            logger.critical(f"CRITICAL ALERT: {alert['message']}")
        
        # Register handlers for critical alerts
        critical_alerts = [
            "high_cpu_usage", "high_memory_usage", "high_disk_usage",
            "high_error_rate", "high_api_latency", "high_db_latency",
            "system_unhealthy"
        ]
        
        for alert_type in critical_alerts:
            self.alert_manager.add_alert_handler(alert_type, log_critical_alert)
    
    def start(self):
        """Start the monitoring system."""
        if self.running:
            return
        
        self.running = True
        
        # Start health check thread
        self.health_check_thread = threading.Thread(
            target=self._health_check_loop,
            daemon=True
        )
        self.health_check_thread.start()
        
        # Start metrics collection thread
        self.metrics_collection_thread = threading.Thread(
            target=self._metrics_collection_loop,
            daemon=True
        )
        self.metrics_collection_thread.start()
        
        logger.info("Monitoring system started")
    
    def stop(self):
        """Stop the monitoring system."""
        self.running = False
        logger.info("Monitoring system stopping")
    
    def _health_check_loop(self):
        """Background thread for periodic health checks."""
        while self.running:
            try:
                health = self.health_checker.check_all_health()
                self.alert_manager.check_health_for_alerts(health)
                
                # Resolve alerts if system is healthy again
                if health["status"] == HealthStatus.HEALTHY:
                    self.alert_manager.resolve_alert("system_unhealthy")
                    self.alert_manager.resolve_alert("system_degraded")
            except Exception as e:
                logger.error(f"Error in health check loop: {e}")
            
            # Sleep until next check
            time.sleep(HEALTH_CHECK_INTERVAL)
    
    def _metrics_collection_loop(self):
        """Background thread for periodic metrics collection."""
        while self.running:
            try:
                # Collect system metrics
                self.metrics_collector.collect_system_metrics()
                
                # Collect database metrics
                try:
                    db = self.db_session_factory()
                    self.metrics_collector.collect_database_metrics(db)
                    db.close()
                except Exception as e:
                    logger.error(f"Error collecting database metrics: {e}")
                
                # Collect Redis metrics
                if self.redis_url:
                    try:
                        redis_client = redis.StrictRedis.from_url(self.redis_url, decode_responses=True)
                        self.metrics_collector.collect_redis_metrics(redis_client)
                    except Exception as e:
                        logger.error(f"Error collecting Redis metrics: {e}")
                
                # Check for alerts
                metrics = self.metrics_collector.get_all_metrics()
                self.alert_manager.check_metrics_for_alerts(metrics)
                
                # Resolve alerts if metrics are back to normal
                system = metrics.get("system", {})
                if system.get("cpu_usage", 0) < ALERT_THRESHOLD_CPU:
                    self.alert_manager.resolve_alert("high_cpu_usage")
                if system.get("memory_usage", 0) < ALERT_THRESHOLD_MEMORY:
                    self.alert_manager.resolve_alert("high_memory_usage")
                if system.get("disk_usage", 0) < ALERT_THRESHOLD_DISK:
                    self.alert_manager.resolve_alert("high_disk_usage")
                
            except Exception as e:
                logger.error(f"Error in metrics collection loop: {e}")
            
            # Sleep until next collection
            time.sleep(METRICS_COLLECTION_INTERVAL)
    
    def track_request(self, response_time: float, is_error: bool = False):
        """Track API request for metrics."""
        self.metrics_collector.track_request(response_time, is_error)
    
    def get_health(self) -> Dict[str, Any]:
        """Get current health status."""
        return self.health_checker.check_all_health()
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get current metrics."""
        return self.metrics_collector.get_all_metrics()
    
    def get_active_alerts(self) -> List[Dict[str, Any]]:
        """Get active alerts."""
        return self.alert_manager.get_active_alerts()
    
    def get_alert_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get alert history."""
        return self.alert_manager.get_alert_history(limit)


# Global monitoring system instance
_monitoring_system = None


def get_monitoring_system(db_session_factory=None, redis_url=None):
    """Get or create the monitoring system singleton."""
    global _monitoring_system
    if _monitoring_system is None and db_session_factory is not None:
        _monitoring_system = MonitoringSystem(db_session_factory, redis_url)
        _monitoring_system.start()
    return _monitoring_system


def track_request_middleware(request: Request, response: Response):
    """Middleware to track request metrics."""
    monitoring = get_monitoring_system()
    if monitoring:
        response_time = request.state.elapsed_time if hasattr(request.state, "elapsed_time") else 0
        is_error = response.status_code >= 400
        monitoring.track_request(response_time, is_error)


def setup_monitoring_routes(app, db_session_factory, redis_url=None):
    """Set up monitoring routes and initialize the monitoring system."""
    from fastapi import Depends, HTTPException, status
    from .auth import get_current_active_user, get_current_admin_user
    
    # Initialize monitoring system
    monitoring_system = get_monitoring_system(db_session_factory, redis_url)
    
    @app.get("/monitoring/health", tags=["Monitoring"])
    async def get_health():
        """Get system health status."""
        return monitoring_system.get_health()
    
    @app.get("/monitoring/metrics", tags=["Monitoring"])
    async def get_metrics(current_user = Depends(get_current_admin_user)):
        """Get system metrics (admin only)."""
        return monitoring_system.get_metrics()
    
    @app.get("/monitoring/alerts", tags=["Monitoring"])
    async def get_alerts(current_user = Depends(get_current_admin_user)):
        """Get active alerts (admin only)."""
        return {
            "active_alerts": monitoring_system.get_active_alerts(),
            "recent_history": monitoring_system.get_alert_history(10)
        }
    
    @app.get("/monitoring/alert-history", tags=["Monitoring"])
    async def get_alert_history(
        limit: int = 100,
        current_user = Depends(get_current_admin_user)
    ):
        """Get alert history (admin only)."""
        return monitoring_system.get_alert_history(limit)
    
    logger.info("Monitoring routes set up")