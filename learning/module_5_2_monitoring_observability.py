#!/usr/bin/env python3
"""
Module 5.2: Monitoring & Observability
====================================

Interactive learning script for implementing comprehensive monitoring,
logging, alerting, and observability for ML applications in production.
"""

import sys
import os
import time
import json
import logging
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional
import psutil

def print_header(title):
    """Print a formatted header."""
    print(f"\n{'='*60}")
    print(f"🎓 {title}")
    print(f"{'='*60}\n")

def print_step(step_num, description):
    """Print a formatted step."""
    print(f"📚 Step {step_num}: {description}")
    print("-" * 40)

def explain_observability_pillars():
    """Explain the three pillars of observability."""
    print("""
🏛️ The Three Pillars of Observability:

1️⃣ METRICS 📊
   • Quantitative measurements over time
   • Examples: Response time, throughput, error rate
   • Tools: Prometheus, Grafana, CloudWatch
   • Good for: Alerting, trends, SLI/SLO tracking

2️⃣ LOGS 📝  
   • Discrete event records with timestamp
   • Examples: Request logs, error messages, audit trails
   • Tools: ELK Stack, Fluentd, Splunk
   • Good for: Debugging, compliance, forensics

3️⃣ TRACES 🔍
   • Request flow across distributed systems  
   • Examples: Microservice call chains, latency breakdown
   • Tools: Jaeger, Zipkin, AWS X-Ray
   • Good for: Performance analysis, bottleneck identification

🎯 ML-Specific Observability Needs:
   • Model performance drift detection
   • Input/output data monitoring
   • Resource utilization (GPU/CPU/Memory)
   • Prediction latency and accuracy
   • Model version and experiment tracking
   • Bias and fairness monitoring

💡 Observability vs Monitoring:
   • Monitoring: "Is the system working?"
   • Observability: "Why is it not working?"
""")

def setup_structured_logging():
    """Demonstrate structured logging for ML applications."""
    print_step("Logging", "Structured Logging for ML Applications")
    
    print("📝 Structured Logging Best Practices:")
    
    # Create a custom logger with structured format
    class MLLogger:
        def __init__(self, name: str, level=logging.INFO):
            self.logger = logging.getLogger(name)
            self.logger.setLevel(level)
            
            # Clear existing handlers
            self.logger.handlers.clear()
            
            # Create structured formatter
            formatter = logging.Formatter(
                '{"timestamp": "%(asctime)s", "level": "%(levelname)s", '
                '"logger": "%(name)s", "message": "%(message)s", '
                '"module": "%(module)s", "function": "%(funcName)s", '
                '"line": %(lineno)d}'
            )
            
            # Console handler
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(formatter)
            self.logger.addHandler(console_handler)
        
        def prediction_log(self, model_name: str, input_shape: tuple, 
                          latency: float, confidence: float, 
                          user_id: Optional[str] = None):
            """Log prediction events with structured data."""
            extra_data = {
                'event_type': 'prediction',
                'model_name': model_name,
                'input_shape': input_shape,
                'latency_ms': latency * 1000,
                'confidence': confidence,
                'user_id': user_id
            }
            
            message = (f"Prediction completed: model={model_name}, "
                      f"latency={latency*1000:.1f}ms, confidence={confidence:.3f}")
            
            # In practice, you'd include extra_data in the log record
            self.logger.info(message)
        
        def error_log(self, error: Exception, context: Dict[str, Any]):
            """Log errors with context for debugging."""
            error_data = {
                'event_type': 'error',
                'error_type': type(error).__name__,
                'error_message': str(error),
                'context': context
            }
            
            message = f"Error occurred: {type(error).__name__}: {error}"
            self.logger.error(message)
        
        def performance_log(self, operation: str, duration: float, 
                           metadata: Dict[str, Any]):
            """Log performance metrics."""
            perf_data = {
                'event_type': 'performance',
                'operation': operation,
                'duration_ms': duration * 1000,
                'metadata': metadata
            }
            
            message = f"Performance: {operation} took {duration*1000:.1f}ms"
            self.logger.info(message)
    
    # Demonstrate the logger
    print("\n🧪 Structured Logging Example:")
    
    ml_logger = MLLogger("thai_model")
    
    # Simulate some events
    print("\n📋 Sample log entries:")
    
    # Prediction log
    ml_logger.prediction_log(
        model_name="qwen-thai-8b",
        input_shape=(1, 512),
        latency=0.15,
        confidence=0.94,
        user_id="user_123"
    )
    
    # Performance log
    ml_logger.performance_log(
        operation="model_loading",
        duration=2.5,
        metadata={"model_size_mb": 4500, "device": "cuda:0"}
    )
    
    # Error log
    try:
        # Simulate an error
        raise ValueError("Invalid input format")
    except ValueError as e:
        ml_logger.error_log(e, {
            "input_data": "corrupted_input",
            "model_version": "v1.2.3",
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
    
    print(f"\n💡 Structured Logging Benefits:")
    print("""
✅ Machine-readable JSON format
✅ Consistent field names across services
✅ Easy filtering and aggregation
✅ Better debugging with context
✅ Integration with log analysis tools
""")

def demonstrate_metrics_collection():
    """Demonstrate metrics collection for ML applications."""
    print_step("Metrics", "Application and ML Metrics Collection")
    
    print("📊 ML Application Metrics Categories:")
    
    # Simple metrics collector
    class MLMetrics:
        def __init__(self):
            self.counters = {}
            self.gauges = {}
            self.histograms = {}
            self.timers = {}
        
        def increment_counter(self, name: str, value: int = 1, tags: Dict[str, str] = None):
            """Increment a counter metric."""
            key = f"{name}:{tags}" if tags else name
            self.counters[key] = self.counters.get(key, 0) + value
        
        def set_gauge(self, name: str, value: float, tags: Dict[str, str] = None):
            """Set a gauge metric (current value)."""
            key = f"{name}:{tags}" if tags else name
            self.gauges[key] = value
        
        def record_histogram(self, name: str, value: float, tags: Dict[str, str] = None):
            """Record a value in a histogram."""
            key = f"{name}:{tags}" if tags else name
            if key not in self.histograms:
                self.histograms[key] = []
            self.histograms[key].append(value)
        
        def start_timer(self, name: str):
            """Start a timer for measuring duration."""
            self.timers[name] = time.perf_counter()
        
        def stop_timer(self, name: str, tags: Dict[str, str] = None):
            """Stop timer and record duration."""
            if name in self.timers:
                duration = time.perf_counter() - self.timers[name]
                self.record_histogram(f"{name}_duration", duration, tags)
                del self.timers[name]
                return duration
            return None
        
        def get_summary(self) -> Dict[str, Any]:
            """Get metrics summary."""
            summary = {
                'counters': self.counters,
                'gauges': self.gauges,
                'histograms': {}
            }
            
            # Calculate histogram statistics
            for name, values in self.histograms.items():
                if values:
                    summary['histograms'][name] = {
                        'count': len(values),
                        'min': min(values),
                        'max': max(values),
                        'avg': sum(values) / len(values),
                        'p50': sorted(values)[len(values)//2],
                        'p95': sorted(values)[int(len(values)*0.95)] if len(values) > 1 else values[0]
                    }
            
            return summary
    
    # Demonstrate metrics collection
    print("\n🧪 Metrics Collection Example:")
    
    metrics = MLMetrics()
    
    # Simulate some application activity
    print("\n📈 Simulating ML application metrics...")
    
    # Request metrics
    for i in range(10):
        metrics.increment_counter("http_requests_total", tags={"method": "POST", "endpoint": "/predict"})
        
        # Simulate prediction latency
        import random
        latency = random.uniform(0.05, 0.3)
        metrics.record_histogram("prediction_latency", latency, tags={"model": "qwen-thai"})
        
        # Model confidence
        confidence = random.uniform(0.7, 0.99)
        metrics.record_histogram("prediction_confidence", confidence)
        
        # Simulate some errors
        if random.random() < 0.1:  # 10% error rate
            metrics.increment_counter("http_requests_total", tags={"method": "POST", "endpoint": "/predict", "status": "500"})
    
    # System metrics
    process = psutil.Process()
    memory_mb = process.memory_info().rss / 1024 / 1024
    cpu_percent = psutil.cpu_percent(interval=0.1)
    
    metrics.set_gauge("memory_usage_mb", memory_mb)
    metrics.set_gauge("cpu_usage_percent", cpu_percent)
    
    # Get and display summary
    summary = metrics.get_summary()
    
    print(f"\n📊 Metrics Summary:")
    print(f"Counters: {len(summary['counters'])} metrics")
    print(f"Gauges: {len(summary['gauges'])} metrics")
    print(f"Histograms: {len(summary['histograms'])} metrics")
    
    print(f"\n🔍 Sample Metrics:")
    for name, value in list(summary['counters'].items())[:3]:
        print(f"  Counter - {name}: {value}")
    
    for name, value in list(summary['gauges'].items())[:3]:
        print(f"  Gauge - {name}: {value:.2f}")
    
    for name, stats in list(summary['histograms'].items())[:2]:
        print(f"  Histogram - {name}:")
        print(f"    Count: {stats['count']}, Avg: {stats['avg']:.3f}, P95: {stats['p95']:.3f}")

def setup_alerting_rules():
    """Demonstrate alerting rules and thresholds."""
    print_step("Alerting", "Intelligent Alerting and Thresholds")
    
    print("🚨 ML Application Alerting Strategy:")
    
    class AlertManager:
        def __init__(self):
            self.rules = {}
            self.alert_history = []
        
        def add_rule(self, name: str, condition: callable, 
                    severity: str, description: str, 
                    threshold_time: int = 60):
            """Add an alerting rule."""
            self.rules[name] = {
                'condition': condition,
                'severity': severity, 
                'description': description,
                'threshold_time': threshold_time,
                'last_triggered': None,
                'triggered_count': 0
            }
        
        def check_alerts(self, metrics: Dict[str, Any]):
            """Check all alerting rules against current metrics."""
            current_time = time.time()
            triggered_alerts = []
            
            for rule_name, rule in self.rules.items():
                try:
                    if rule['condition'](metrics):
                        # Check if we should trigger (avoid spam)
                        if (rule['last_triggered'] is None or 
                            current_time - rule['last_triggered'] > rule['threshold_time']):
                            
                            alert = {
                                'rule': rule_name,
                                'severity': rule['severity'],
                                'description': rule['description'],
                                'timestamp': datetime.now(timezone.utc).isoformat(),
                                'metrics': metrics
                            }
                            
                            triggered_alerts.append(alert)
                            self.alert_history.append(alert)
                            rule['last_triggered'] = current_time
                            rule['triggered_count'] += 1
                            
                except Exception as e:
                    print(f"❌ Error checking rule {rule_name}: {e}")
            
            return triggered_alerts
        
        def get_alert_summary(self):
            """Get alerting summary."""
            return {
                'total_rules': len(self.rules),
                'total_alerts': len(self.alert_history),
                'recent_alerts': self.alert_history[-5:],  # Last 5 alerts
                'rule_stats': {name: rule['triggered_count'] for name, rule in self.rules.items()}
            }
    
    # Set up alerting rules
    print("\n🔧 Setting up alerting rules:")
    
    alert_manager = AlertManager()
    
    # High latency alert
    alert_manager.add_rule(
        name="high_prediction_latency",
        condition=lambda m: m.get('avg_latency', 0) > 0.5,  # > 500ms
        severity="warning",
        description="Prediction latency is above 500ms"
    )
    
    # Low confidence alert  
    alert_manager.add_rule(
        name="low_model_confidence",
        condition=lambda m: m.get('avg_confidence', 1.0) < 0.7,  # < 70%
        severity="critical",
        description="Model confidence is below 70%"
    )
    
    # High error rate alert
    alert_manager.add_rule(
        name="high_error_rate", 
        condition=lambda m: m.get('error_rate', 0) > 0.05,  # > 5%
        severity="critical",
        description="Error rate is above 5%"
    )
    
    # Resource usage alert
    alert_manager.add_rule(
        name="high_memory_usage",
        condition=lambda m: m.get('memory_usage_mb', 0) > 8000,  # > 8GB
        severity="warning", 
        description="Memory usage is above 8GB"
    )
    
    # Model drift alert (simulated)
    alert_manager.add_rule(
        name="model_drift_detected",
        condition=lambda m: m.get('drift_score', 0) > 0.3,  # Drift threshold
        severity="critical",
        description="Model drift detected - retrain recommended"
    )
    
    print(f"✅ Added {len(alert_manager.rules)} alerting rules")
    
    # Simulate checking alerts
    print(f"\n🧪 Testing alerting with sample metrics:")
    
    sample_metrics = {
        'avg_latency': 0.8,  # High latency - should trigger
        'avg_confidence': 0.65,  # Low confidence - should trigger  
        'error_rate': 0.02,  # Normal error rate
        'memory_usage_mb': 9000,  # High memory - should trigger
        'drift_score': 0.1  # Normal drift
    }
    
    triggered_alerts = alert_manager.check_alerts(sample_metrics)
    
    print(f"\n🚨 Triggered Alerts ({len(triggered_alerts)}):")
    for alert in triggered_alerts:
        print(f"  • {alert['severity'].upper()}: {alert['rule']}")
        print(f"    {alert['description']}")
        print(f"    Time: {alert['timestamp']}")
    
    # Show alert summary
    summary = alert_manager.get_alert_summary()
    print(f"\n📊 Alert Summary:")
    print(f"  Total rules: {summary['total_rules']}")
    print(f"  Total alerts fired: {summary['total_alerts']}")

def demonstrate_distributed_tracing():
    """Demonstrate distributed tracing for ML pipelines."""
    print_step("Tracing", "Distributed Tracing for ML Pipelines")
    
    print("🔍 Distributed Tracing Concepts:")
    
    # Simple tracing implementation
    import uuid
    from contextlib import contextmanager
    
    class Span:
        def __init__(self, operation_name: str, parent_span_id: str = None):
            self.span_id = str(uuid.uuid4())[:8]
            self.parent_span_id = parent_span_id
            self.operation_name = operation_name
            self.start_time = time.perf_counter()
            self.end_time = None
            self.tags = {}
            self.logs = []
        
        def set_tag(self, key: str, value: Any):
            """Set a tag on the span."""
            self.tags[key] = value
        
        def log(self, message: str, **kwargs):
            """Add a log entry to the span."""
            log_entry = {
                'timestamp': time.perf_counter(),
                'message': message,
                **kwargs
            }
            self.logs.append(log_entry)
        
        def finish(self):
            """Finish the span."""
            self.end_time = time.perf_counter()
        
        def duration(self) -> float:
            """Get span duration in seconds."""
            if self.end_time:
                return self.end_time - self.start_time
            return time.perf_counter() - self.start_time
        
        def to_dict(self) -> Dict[str, Any]:
            """Convert span to dictionary."""
            return {
                'span_id': self.span_id,
                'parent_span_id': self.parent_span_id,
                'operation_name': self.operation_name,
                'start_time': self.start_time,
                'end_time': self.end_time,
                'duration_ms': self.duration() * 1000,
                'tags': self.tags,
                'logs': self.logs
            }
    
    class Tracer:
        def __init__(self):
            self.active_spans = []
            self.completed_spans = []
        
        @contextmanager
        def start_span(self, operation_name: str, **tags):
            """Start a new span."""
            parent_span_id = self.active_spans[-1].span_id if self.active_spans else None
            span = Span(operation_name, parent_span_id)
            
            # Set tags
            for key, value in tags.items():
                span.set_tag(key, value)
            
            self.active_spans.append(span)
            
            try:
                yield span
            finally:
                span.finish()
                self.active_spans.remove(span)
                self.completed_spans.append(span)
        
        def get_trace_summary(self) -> List[Dict[str, Any]]:
            """Get summary of all completed spans."""
            return [span.to_dict() for span in self.completed_spans]
    
    # Demonstrate tracing
    print(f"\n🧪 ML Pipeline Tracing Example:")
    
    tracer = Tracer()
    
    # Simulate an ML prediction pipeline with tracing
    def simulate_ml_pipeline():
        """Simulate a complete ML prediction pipeline."""
        
        with tracer.start_span("prediction_request", user_id="user_123", model="qwen-thai") as root_span:
            root_span.log("Received prediction request")
            
            # Input preprocessing
            with tracer.start_span("preprocessing", input_type="text") as prep_span:
                prep_span.log("Starting tokenization")
                time.sleep(0.01)  # Simulate tokenization
                prep_span.set_tag("token_count", 245)
                prep_span.log("Tokenization completed")
                
                prep_span.log("Starting input validation")
                time.sleep(0.005)  # Simulate validation
                prep_span.log("Input validation completed")
            
            # Model inference
            with tracer.start_span("model_inference", model_name="qwen-thai-8b", device="cuda:0") as model_span:
                model_span.log("Loading model weights")
                time.sleep(0.02)  # Simulate model loading
                
                model_span.log("Starting forward pass")
                time.sleep(0.15)  # Simulate inference
                model_span.set_tag("batch_size", 1)
                model_span.set_tag("sequence_length", 512)
                model_span.log("Forward pass completed")
                
                # Simulate attention analysis
                with tracer.start_span("attention_analysis") as attn_span:
                    attn_span.log("Analyzing attention weights")
                    time.sleep(0.01)  # Simulate analysis
                    attn_span.set_tag("attention_heads", 32)
                    attn_span.log("Attention analysis completed")
            
            # Post-processing
            with tracer.start_span("postprocessing", output_format="json") as post_span:
                post_span.log("Starting response formatting")
                time.sleep(0.008)  # Simulate formatting
                post_span.set_tag("confidence_score", 0.94)
                post_span.log("Response formatting completed")
                
                post_span.log("Starting response validation")
                time.sleep(0.003)  # Simulate validation
                post_span.log("Response validation completed")
            
            root_span.log("Prediction request completed successfully")
    
    # Run the simulation
    simulate_ml_pipeline()
    
    # Display trace results
    trace_summary = tracer.get_trace_summary()
    
    print(f"\n📊 Trace Summary ({len(trace_summary)} spans):")
    
    # Sort by start time to show chronological order
    sorted_spans = sorted(trace_summary, key=lambda x: x['start_time'])
    
    for span in sorted_spans:
        indent = "  " * (1 if span['parent_span_id'] else 0)
        if span['parent_span_id']:
            indent += "└─ "
        
        print(f"{indent}{span['operation_name']}: {span['duration_ms']:.1f}ms")
        
        # Show important tags
        if span['tags']:
            for key, value in span['tags'].items():
                print(f"{indent}   {key}: {value}")
    
    # Calculate total time
    root_spans = [s for s in sorted_spans if not s['parent_span_id']]
    if root_spans:
        total_time = root_spans[0]['duration_ms']
        print(f"\n⏱️ Total request time: {total_time:.1f}ms")

def setup_health_checks():
    """Demonstrate comprehensive health checking."""
    print_step("Health", "Application Health Monitoring")
    
    print("🏥 Health Check Categories:")
    
    class HealthChecker:
        def __init__(self):
            self.checks = {}
        
        def add_check(self, name: str, check_func: callable, 
                     timeout: float = 5.0, critical: bool = True):
            """Add a health check."""
            self.checks[name] = {
                'func': check_func,
                'timeout': timeout,
                'critical': critical,
                'last_result': None,
                'last_check': None
            }
        
        def run_check(self, name: str) -> Dict[str, Any]:
            """Run a single health check."""
            if name not in self.checks:
                return {'status': 'error', 'message': f'Check {name} not found'}
            
            check = self.checks[name]
            start_time = time.perf_counter()
            
            try:
                # Run check with timeout
                result = check['func']()
                duration = time.perf_counter() - start_time
                
                check_result = {
                    'status': 'healthy' if result.get('healthy', False) else 'unhealthy',
                    'duration_ms': duration * 1000,
                    'timestamp': datetime.now(timezone.utc).isoformat(),
                    'critical': check['critical'],
                    **result
                }
                
                check['last_result'] = check_result
                check['last_check'] = time.time()
                
                return check_result
                
            except Exception as e:
                duration = time.perf_counter() - start_time
                error_result = {
                    'status': 'error',
                    'error': str(e),
                    'duration_ms': duration * 1000,
                    'timestamp': datetime.now(timezone.utc).isoformat(),
                    'critical': check['critical']
                }
                
                check['last_result'] = error_result
                return error_result
        
        def run_all_checks(self) -> Dict[str, Any]:
            """Run all health checks."""
            results = {}
            overall_healthy = True
            critical_failures = []
            
            for name in self.checks:
                result = self.run_check(name)
                results[name] = result
                
                if result['status'] != 'healthy':
                    if self.checks[name]['critical']:
                        critical_failures.append(name)
                        overall_healthy = False
            
            return {
                'status': 'healthy' if overall_healthy else 'unhealthy',
                'checks': results,
                'critical_failures': critical_failures,
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
    
    # Set up health checks
    print(f"\n🔧 Setting up health checks:")
    
    health_checker = HealthChecker()
    
    # Database connectivity check
    def check_database():
        """Simulate database health check.""" 
        # Simulate database ping
        time.sleep(0.01)  # Simulate network latency
        return {
            'healthy': True,
            'message': 'Database connection successful',
            'connection_pool_size': 10,
            'active_connections': 3
        }
    
    # Model availability check
    def check_model():
        """Check if ML model is loaded and ready."""
        # Simulate model check
        time.sleep(0.005)
        return {
            'healthy': True,
            'message': 'Model loaded successfully',
            'model_name': 'qwen-thai-8b',
            'model_size_mb': 4500,
            'warmup_completed': True
        }
    
    # GPU availability check  
    def check_gpu():
        """Check GPU health and availability."""
        try:
            import torch
            if torch.cuda.is_available():
                return {
                    'healthy': True,
                    'message': 'GPU available',
                    'gpu_count': torch.cuda.device_count(),
                    'gpu_memory_free': '12GB',  # Simulated
                    'cuda_version': torch.version.cuda
                }
            else:
                return {
                    'healthy': False,
                    'message': 'No GPU available',
                    'fallback': 'CPU inference enabled'
                }
        except ImportError:
            return {
                'healthy': False,
                'message': 'PyTorch not available'
            }
    
    # Disk space check
    def check_disk_space():
        """Check available disk space."""
        disk_usage = psutil.disk_usage('/')
        free_percent = (disk_usage.free / disk_usage.total) * 100
        
        return {
            'healthy': free_percent > 10,  # Alert if less than 10% free
            'message': f'Disk space: {free_percent:.1f}% free',
            'free_gb': disk_usage.free / (1024**3),
            'total_gb': disk_usage.total / (1024**3)
        }
    
    # Memory usage check
    def check_memory():
        """Check memory usage."""
        memory = psutil.virtual_memory()
        available_percent = (memory.available / memory.total) * 100
        
        return {
            'healthy': available_percent > 20,  # Alert if less than 20% available
            'message': f'Memory: {available_percent:.1f}% available', 
            'available_gb': memory.available / (1024**3),
            'total_gb': memory.total / (1024**3)
        }
    
    # Add all checks
    health_checker.add_check('database', check_database, critical=True)
    health_checker.add_check('model', check_model, critical=True) 
    health_checker.add_check('gpu', check_gpu, critical=False)  # Not critical
    health_checker.add_check('disk', check_disk_space, critical=True)
    health_checker.add_check('memory', check_memory, critical=True)
    
    print(f"✅ Added {len(health_checker.checks)} health checks")
    
    # Run health checks
    print(f"\n🧪 Running health checks:")
    
    health_report = health_checker.run_all_checks()
    
    print(f"\n🏥 Health Report:")
    print(f"Overall Status: {health_report['status'].upper()}")
    
    if health_report['critical_failures']:
        print(f"❌ Critical Failures: {', '.join(health_report['critical_failures'])}")
    
    print(f"\n📋 Individual Checks:")
    for check_name, result in health_report['checks'].items():
        status_icon = "✅" if result['status'] == 'healthy' else "❌" if result['status'] == 'unhealthy' else "⚠️"
        critical_mark = "🔴" if health_checker.checks[check_name]['critical'] else "🟡"
        
        print(f"  {status_icon} {critical_mark} {check_name}: {result.get('message', result['status'])}")
        print(f"    Duration: {result['duration_ms']:.1f}ms")

def main():
    print_header("Module 5.2: Monitoring & Observability")
    
    # Step 1: Observability pillars overview  
    explain_observability_pillars()
    input("\n🔍 Press Enter to continue to structured logging...")
    
    # Step 2: Structured logging
    setup_structured_logging()
    input("\n🔍 Press Enter to continue to metrics collection...")
    
    # Step 3: Metrics collection
    demonstrate_metrics_collection()
    input("\n🔍 Press Enter to continue to alerting setup...")
    
    # Step 4: Alerting
    setup_alerting_rules()
    input("\n🔍 Press Enter to continue to distributed tracing...")
    
    # Step 5: Distributed tracing
    demonstrate_distributed_tracing()
    input("\n🔍 Press Enter to continue to health monitoring...")
    
    # Step 6: Health monitoring
    setup_health_checks()
    input("\n🔍 Press Enter to see summary...")
    
    # Summary
    print_step("Summary", "What You Learned")
    
    print("""
🎯 Comprehensive Observability Concepts Covered:
  • Three pillars: Metrics, Logs, Traces
  • Structured logging with context and correlation IDs
  • Application and ML-specific metrics collection
  • Intelligent alerting with proper thresholds
  • Distributed tracing for complex ML pipelines
  • Multi-dimensional health monitoring

🛠️ Production Observability Stack:
  📊 Metrics: Prometheus + Grafana
  📝 Logs: ELK Stack (Elasticsearch, Logstash, Kibana)
  🔍 Traces: Jaeger or Zipkin
  🚨 Alerts: AlertManager + PagerDuty
  🏥 Health: Custom endpoints + Kubernetes probes

🎯 ML-Specific Observability:
  • Model performance drift detection
  • Prediction latency and confidence monitoring  
  • Input/output data distribution tracking
  • Resource utilization (GPU/CPU/Memory)
  • A/B test and canary deployment monitoring
  • Bias and fairness metrics

💡 Observability Best Practices:
  • Start with SLIs (Service Level Indicators)
  • Define meaningful SLOs (Service Level Objectives)
  • Use structured logging with correlation IDs
  • Implement proper alert fatigue management
  • Monitor business metrics, not just technical ones
  • Practice chaos engineering to validate monitoring

🔍 Production Checklist:
  ✅ Structured logging with correlation IDs
  ✅ Key business and technical metrics
  ✅ Intelligent alerting with proper thresholds
  ✅ Distributed tracing for complex requests
  ✅ Comprehensive health checks
  ✅ Monitoring dashboards for different audiences
  ✅ On-call runbooks and incident response
  ✅ Regular monitoring system health checks

🎓 Advanced Topics to Explore:
  • OpenTelemetry for standardized observability
  • Custom Grafana dashboards and alerts
  • ML model drift detection algorithms
  • Chaos engineering and fault injection
  • Cost monitoring and optimization
  • Security monitoring and audit logging

🚀 Congratulations! You've completed the Thai Model Learning Path!
    You now have comprehensive knowledge of:
    • Python packaging and configuration management
    • Transformers, LoRA, and model training
    • FastAPI development and advanced features  
    • Docker containerization and deployment
    • Performance optimization techniques
    • Production monitoring and observability

💪 Next Steps:
  1. Apply these concepts to your own ML projects
  2. Contribute to open source ML projects
  3. Build a production ML system from scratch
  4. Share your knowledge with the ML community!
""")

if __name__ == "__main__":
    main()