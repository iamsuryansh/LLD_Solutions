"""
REST API layer for Log Feeding Service
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
import json

from ..services import LogFeedingService
from ..models import LogLevel
from ..filters import LogFilter, LevelFilter, ServiceFilter, TimeRangeFilter, CompositeFilter


class LogAPIHandler:
    """Handles REST API requests for log operations"""
    
    def __init__(self, log_service: LogFeedingService):
        self.log_service = log_service
    
    def post_log(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        POST /logs
        Ingest a single log entry
        
        Request body:
        {
            "level": "ERROR",
            "message": "Database connection failed", 
            "service": "user-service",
            "metadata": {"error_code": 500}
        }
        """
        try:
            level = LogLevel(request_data['level'])
            message = request_data['message']
            service = request_data['service']
            metadata = request_data.get('metadata', {})
            
            log_id = self.log_service.ingest_log(level, message, service, metadata)
            
            return {
                "status": "success",
                "log_id": log_id,
                "message": "Log ingested successfully"
            }
        except Exception as e:
            return {
                "status": "error", 
                "message": f"Failed to ingest log: {str(e)}"
            }
    
    def post_batch_logs(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        POST /logs/batch
        Ingest multiple log entries
        
        Request body:
        {
            "logs": [
                {"level": "INFO", "message": "...", "service": "..."},
                {"level": "ERROR", "message": "...", "service": "..."}
            ]
        }
        """
        try:
            logs = request_data['logs']
            log_ids = self.log_service.batch_ingest_logs(logs)
            
            return {
                "status": "success",
                "log_ids": log_ids,
                "count": len(log_ids),
                "message": f"Ingested {len(log_ids)} logs successfully"
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to ingest batch logs: {str(e)}"
            }
    
    def get_logs(self, query_params: Dict[str, str]) -> Dict[str, Any]:
        """
        GET /logs?service=user-service&level=ERROR&start_time=...&end_time=...&keywords=...
        Query logs with various filters
        """
        try:
            filters = []
            
            # Service filter
            if 'service' in query_params:
                service_filter = ServiceFilter({query_params['service']})
                filters.append(service_filter)
            
            # Level filter  
            if 'level' in query_params:
                level = LogLevel(query_params['level'])
                level_filter = LevelFilter({level})
                filters.append(level_filter)
            
            # Time range filter
            start_time = None
            end_time = None
            if 'start_time' in query_params:
                start_time = datetime.fromisoformat(query_params['start_time'])
            if 'end_time' in query_params:
                end_time = datetime.fromisoformat(query_params['end_time'])
            
            if start_time or end_time:
                time_filter = TimeRangeFilter(start_time, end_time)
                filters.append(time_filter)
            
            # Get logs based on primary filter
            if 'service' in query_params:
                logs = self.log_service.get_logs_by_service(
                    query_params['service'], start_time, end_time)
            elif 'level' in query_params:
                level = LogLevel(query_params['level'])
                logs = self.log_service.get_logs_by_level(level, start_time, end_time)
            else:
                # Get recent logs if no specific filter
                minutes = int(query_params.get('minutes', 60))
                logs = self.log_service.get_recent_logs(minutes)
            
            # Apply additional filters
            if len(filters) > 1:
                composite_filter = CompositeFilter(filters)
                logs = composite_filter.apply(logs)
            
            # Pagination
            page = int(query_params.get('page', 1))
            limit = int(query_params.get('limit', 100))
            start_idx = (page - 1) * limit
            end_idx = start_idx + limit
            
            paginated_logs = logs[start_idx:end_idx]
            
            return {
                "status": "success",
                "logs": [self._log_to_dict(log) for log in paginated_logs],
                "total": len(logs),
                "page": page,
                "limit": limit,
                "has_more": end_idx < len(logs)
            }
        
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to query logs: {str(e)}"
            }
    
    def get_log_stats(self, query_params: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        GET /logs/stats
        Get log statistics
        """
        try:
            stats = self.log_service.get_log_stats()
            return {
                "status": "success",
                "stats": stats
            }
        except Exception as e:
            return {
                "status": "error", 
                "message": f"Failed to get stats: {str(e)}"
            }
    
    def _log_to_dict(self, log_entry) -> Dict[str, Any]:
        """Convert LogEntry to dictionary for JSON serialization"""
        return {
            "log_id": log_entry.log_id,
            "level": log_entry.level.value,
            "message": log_entry.message,
            "service": log_entry.service, 
            "timestamp": log_entry.timestamp.isoformat(),
            "metadata": log_entry.metadata
        }


# REST API Route Handlers (Framework-agnostic)
class RESTAPIRoutes:
    """Defines REST API routes and HTTP methods"""
    
    def __init__(self, api_handler: LogAPIHandler):
        self.handler = api_handler
        self.routes = {
            ('POST', '/logs'): self.handler.post_log,
            ('POST', '/logs/batch'): self.handler.post_batch_logs,
            ('GET', '/logs'): self.handler.get_logs,
            ('GET', '/logs/stats'): self.handler.get_log_stats
        }
    
    def handle_request(self, method: str, path: str, 
                      request_data: Optional[Dict] = None,
                      query_params: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Generic request handler that can be adapted to any web framework
        """
        route_key = (method, path)
        
        if route_key not in self.routes:
            return {
                "status": "error",
                "message": f"Route {method} {path} not found",
                "error_code": 404
            }
        
        handler_func = self.routes[route_key]
        
        try:
            if method == 'GET':
                return handler_func(query_params or {})
            else:
                return handler_func(request_data or {})
        except Exception as e:
            return {
                "status": "error",
                "message": f"Internal server error: {str(e)}",
                "error_code": 500
            }