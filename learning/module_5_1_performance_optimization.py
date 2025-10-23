#!/usr/bin/env python3
"""
Module 5.1: Performance Optimization
==================================

Interactive learning script for optimizing ML model performance including
GPU optimization, memory management, batching, and inference acceleration.
"""

import sys
import os
import time
import psutil
from pathlib import Path
from typing import List, Dict, Any
import json

def print_header(title):
    """Print a formatted header."""
    print(f"\n{'='*60}")
    print(f"🎓 {title}")
    print(f"{'='*60}\n")

def print_step(step_num, description):
    """Print a formatted step."""
    print(f"📚 Step {step_num}: {description}")
    print("-" * 40)

def get_system_info():
    """Get system performance information."""
    info = {
        'cpu_count': psutil.cpu_count(),
        'cpu_percent': psutil.cpu_percent(interval=1),
        'memory': psutil.virtual_memory(),
        'disk': psutil.disk_usage('/'),
    }
    
    # Try to get GPU info if available
    try:
        import torch
        if torch.cuda.is_available():
            info['gpu_count'] = torch.cuda.device_count()
            info['gpu_name'] = torch.cuda.get_device_name(0)
            info['gpu_memory'] = torch.cuda.get_device_properties(0).total_memory
        else:
            info['gpu_available'] = False
    except ImportError:
        info['torch_available'] = False
    
    return info

def explain_performance_concepts():
    """Explain key performance optimization concepts."""
    print("""
🚀 Performance Optimization Hierarchy:

1️⃣ HARDWARE OPTIMIZATION:
   • GPU vs CPU selection
   • Memory allocation strategies
   • Batch size optimization
   • Multi-processing/threading

2️⃣ MODEL OPTIMIZATION:
   • Model quantization (INT8, FP16)
   • Pruning and distillation  
   • ONNX conversion
   • TensorRT/OpenVINO optimization

3️⃣ INFERENCE OPTIMIZATION:
   • Dynamic batching
   • Request queuing
   • Model caching
   • Prediction pipelines

4️⃣ SYSTEM OPTIMIZATION:
   • Connection pooling
   • Memory management
   • Async processing
   • Resource monitoring

🎯 Performance Metrics to Track:
   • Latency (response time)
   • Throughput (requests/second)
   • Memory usage (RAM/VRAM)
   • CPU/GPU utilization
   • Queue depth and wait times
""")

def demonstrate_batching_optimization():
    """Demonstrate batching strategies for better performance."""
    print_step("Batching", "Dynamic Batching for Better Throughput")
    
    # Simulate single vs batch processing
    print("🧪 Simulating single vs batch processing:")
    
    def simulate_model_inference(batch_size: int, num_samples: int = 100):
        """Simulate model inference with different batch sizes."""
        # Simulate processing time (batch processing is more efficient)
        base_time = 0.01  # Base processing time per item
        batch_overhead = 0.005 * batch_size  # Slight overhead for larger batches
        
        total_time = 0
        batches_processed = 0
        
        for i in range(0, num_samples, batch_size):
            current_batch_size = min(batch_size, num_samples - i)
            # Simulate that batch processing is more efficient
            batch_time = base_time * current_batch_size * (0.7 if batch_size > 1 else 1.0) + batch_overhead
            total_time += batch_time
            batches_processed += 1
        
        return {
            'total_time': total_time,
            'batches_processed': batches_processed,
            'avg_time_per_item': total_time / num_samples,
            'throughput': num_samples / total_time
        }
    
    batch_sizes = [1, 4, 8, 16, 32]
    results = []
    
    for batch_size in batch_sizes:
        result = simulate_model_inference(batch_size)
        results.append({
            'batch_size': batch_size,
            **result
        })
        
        print(f"Batch Size {batch_size:2d}: "
              f"{result['throughput']:.1f} items/sec, "
              f"{result['avg_time_per_item']*1000:.1f}ms per item")
    
    # Find optimal batch size
    best_batch = max(results, key=lambda x: x['throughput'])
    print(f"\n🏆 Best throughput: Batch size {best_batch['batch_size']} "
          f"({best_batch['throughput']:.1f} items/sec)")
    
    print(f"\n💡 Dynamic Batching Implementation:")
    print("""
class DynamicBatcher:
    def __init__(self, max_batch_size=32, max_wait_time=0.01):
        self.max_batch_size = max_batch_size
        self.max_wait_time = max_wait_time
        self.queue = []
        
    async def add_request(self, request):
        self.queue.append(request)
        if len(self.queue) >= self.max_batch_size:
            return await self.process_batch()
        
        # Wait for more requests or timeout
        await asyncio.sleep(self.max_wait_time)
        if self.queue:
            return await self.process_batch()
    
    async def process_batch(self):
        batch = self.queue[:self.max_batch_size]
        self.queue = self.queue[self.max_batch_size:]
        return await self.model.predict_batch(batch)
""")

def demonstrate_memory_optimization():
    """Demonstrate memory optimization techniques."""
    print_step("Memory", "Memory Management and Optimization")
    
    # Get current memory usage
    process = psutil.Process()
    initial_memory = process.memory_info().rss / 1024 / 1024  # MB
    
    print(f"🔍 Initial memory usage: {initial_memory:.1f} MB")
    
    print(f"\n💾 Memory Optimization Strategies:")
    
    strategies = {
        "Model Quantization": {
            "description": "Reduce model precision (FP32 → FP16 → INT8)",
            "savings": "2x-4x memory reduction",
            "tradeoff": "Slight accuracy loss"
        },
        "Gradient Checkpointing": {
            "description": "Trade computation for memory during training",
            "savings": "50-80% memory reduction",
            "tradeoff": "20-30% slower training"
        },
        "Model Sharding": {
            "description": "Split large models across devices",
            "savings": "Linear scaling with devices",
            "tradeoff": "Communication overhead"
        },
        "Dynamic Loading": {
            "description": "Load model weights on-demand", 
            "savings": "90% base memory reduction",
            "tradeoff": "Loading latency"
        },
        "Memory Pooling": {
            "description": "Reuse allocated memory buffers",
            "savings": "Eliminates allocation overhead",
            "tradeoff": "More complex code"
        }
    }
    
    for strategy, details in strategies.items():
        print(f"\n🛠️ {strategy}:")
        print(f"   📝 {details['description']}")
        print(f"   💾 Savings: {details['savings']}")
        print(f"   ⚖️ Tradeoff: {details['tradeoff']}")
    
    print(f"\n🔧 Memory Monitoring Code Example:")
    print("""
import psutil
import torch

class MemoryMonitor:
    def __init__(self):
        self.process = psutil.Process()
    
    def get_memory_usage(self):
        # System memory
        system_mem = psutil.virtual_memory()
        process_mem = self.process.memory_info().rss / 1024**3  # GB
        
        result = {
            'system_total': system_mem.total / 1024**3,
            'system_available': system_mem.available / 1024**3,
            'process_memory': process_mem
        }
        
        # GPU memory if available
        if torch.cuda.is_available():
            result['gpu_allocated'] = torch.cuda.memory_allocated() / 1024**3
            result['gpu_reserved'] = torch.cuda.memory_reserved() / 1024**3
        
        return result
    
    def log_memory(self, step_name):
        memory = self.get_memory_usage()
        print(f"{step_name}: Process={memory['process_memory']:.2f}GB")
        if 'gpu_allocated' in memory:
            print(f"  GPU: {memory['gpu_allocated']:.2f}GB allocated")
""")

def demonstrate_gpu_optimization():
    """Demonstrate GPU optimization techniques."""
    print_step("GPU", "GPU Optimization Strategies")
    
    # Check GPU availability
    gpu_available = False
    try:
        import torch
        gpu_available = torch.cuda.is_available()
        if gpu_available:
            gpu_count = torch.cuda.device_count()
            gpu_name = torch.cuda.get_device_name(0)
            print(f"🎮 GPU Available: {gpu_name} (x{gpu_count})")
        else:
            print("🔍 No GPU detected - showing CPU optimization instead")
    except ImportError:
        print("📦 PyTorch not available - showing theoretical concepts")
    
    print(f"\n🚀 GPU Optimization Techniques:")
    
    optimizations = {
        "Mixed Precision (AMP)": {
            "code": """
# Automatic Mixed Precision
from torch.cuda.amp import autocast, GradScaler

scaler = GradScaler()

with autocast():
    outputs = model(inputs)
    loss = criterion(outputs, targets)

scaler.scale(loss).backward()
scaler.step(optimizer)
scaler.update()
""",
            "benefit": "1.5-2x speedup, 50% memory reduction"
        },
        
        "Tensor Parallelism": {
            "code": """
# Multi-GPU model parallelism
import torch.nn as nn
from torch.nn.parallel import DataParallel

model = MyModel()
if torch.cuda.device_count() > 1:
    model = DataParallel(model)
model.cuda()
""",
            "benefit": "Scale to multiple GPUs"
        },
        
        "CUDA Streams": {
            "code": """
# Overlapping computation and memory transfer
stream = torch.cuda.Stream()

with torch.cuda.stream(stream):
    # Async operations
    output = model(input.cuda(non_blocking=True))

torch.cuda.synchronize()  # Wait for completion
""",
            "benefit": "Hide memory transfer latency"
        },
        
        "TensorRT Optimization": {
            "code": """
# TensorRT inference optimization
import torch_tensorrt

# Compile model for specific input shape
optimized_model = torch_tensorrt.compile(
    model,
    inputs=[torch.randn(1, 3, 224, 224).cuda()],
    enabled_precisions={torch.float, torch.half}
)
""",
            "benefit": "2-5x inference speedup"
        }
    }
    
    for technique, details in optimizations.items():
        print(f"\n🔧 {technique}:")
        print(f"   💚 Benefit: {details['benefit']}")
        print(f"   📝 Code:")
        for line in details['code'].strip().split('\n'):
            print(f"      {line}")

def demonstrate_caching_strategies():
    """Demonstrate caching strategies for better performance."""
    print_step("Caching", "Intelligent Caching Strategies")
    
    print(f"🗄️ Multi-Level Caching Architecture:")
    print("""
┌─────────────────────────────────────────────────┐
│                L1: Memory Cache                 │
│            (Recent predictions)                 │
│              ⏱️ ~0.1ms access                    │
└─────────────────┬───────────────────────────────┘
                  │ Cache miss
┌─────────────────▼───────────────────────────────┐
│                L2: Redis Cache                  │
│           (Shared across instances)             │
│              ⏱️ ~1ms access                      │
└─────────────────┬───────────────────────────────┘
                  │ Cache miss
┌─────────────────▼───────────────────────────────┐
│              L3: Model Inference                │
│            (Generate new prediction)            │
│              ⏱️ ~100ms+ processing               │
└─────────────────────────────────────────────────┘
""")
    
    print(f"\n🛠️ Implementation Example:")
    print("""
import hashlib
import json
from typing import Any, Optional

class MultiLevelCache:
    def __init__(self, max_memory_size=1000):
        self.memory_cache = {}  # L1: In-memory
        self.memory_order = []  # LRU tracking
        self.max_memory_size = max_memory_size
        
    def _hash_input(self, input_data: Any) -> str:
        \"\"\"Create deterministic hash of input.\"\"\"
        serialized = json.dumps(input_data, sort_keys=True)
        return hashlib.sha256(serialized.encode()).hexdigest()
    
    def get(self, input_data: Any) -> Optional[Any]:
        cache_key = self._hash_input(input_data)
        
        # L1: Check memory cache
        if cache_key in self.memory_cache:
            # Move to front (LRU)
            self.memory_order.remove(cache_key)
            self.memory_order.append(cache_key)
            return self.memory_cache[cache_key]
        
        # L2: Check Redis (if available)
        redis_result = self._get_from_redis(cache_key)
        if redis_result:
            self._store_in_memory(cache_key, redis_result)
            return redis_result
            
        return None  # Cache miss - need to compute
    
    def store(self, input_data: Any, result: Any):
        cache_key = self._hash_input(input_data)
        
        # Store in both levels
        self._store_in_memory(cache_key, result)
        self._store_in_redis(cache_key, result)
    
    def _store_in_memory(self, key: str, value: Any):
        # Implement LRU eviction
        if len(self.memory_cache) >= self.max_memory_size:
            oldest_key = self.memory_order.pop(0)
            del self.memory_cache[oldest_key]
        
        self.memory_cache[key] = value
        self.memory_order.append(key)
""")

def demonstrate_profiling_tools():
    """Demonstrate profiling and monitoring tools."""
    print_step("Profiling", "Performance Profiling and Monitoring")
    
    print(f"🔍 Performance Profiling Tools:")
    
    tools = {
        "Python cProfile": {
            "use_case": "Function-level performance analysis",
            "command": "python -m cProfile -o profile.stats script.py",
            "pros": "Built-in, detailed function timing",
            "cons": "High overhead, Python-only"
        },
        "py-spy": {
            "use_case": "Low-overhead sampling profiler",
            "command": "py-spy record -o profile.svg -- python script.py",
            "pros": "Very low overhead, running processes",
            "cons": "Sampling-based, may miss short functions"
        },
        "PyTorch Profiler": {
            "use_case": "Deep learning model profiling",
            "command": "torch.profiler.profile() context manager",
            "pros": "GPU profiling, kernel-level analysis",
            "cons": "PyTorch-specific"
        },
        "NVIDIA Nsight": {
            "use_case": "CUDA kernel optimization",
            "command": "nsys profile python script.py",
            "pros": "Hardware-level GPU analysis",
            "cons": "NVIDIA GPUs only, complex setup"
        }
    }
    
    for tool, details in tools.items():
        print(f"\n🛠️ {tool}:")
        print(f"   🎯 Use case: {details['use_case']}")
        print(f"   💻 Command: {details['command']}")
        print(f"   ✅ Pros: {details['pros']}")
        print(f"   ❌ Cons: {details['cons']}")
    
    print(f"\n📊 Simple Profiling Example:")
    print("""
import time
import functools
from typing import Callable

def profile_time(func: Callable) -> Callable:
    \"\"\"Decorator to measure function execution time.\"\"\"
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        result = func(*args, **kwargs)
        end_time = time.perf_counter()
        
        execution_time = end_time - start_time
        print(f"⏱️ {func.__name__}: {execution_time:.4f}s")
        
        return result
    return wrapper

@profile_time
def slow_function():
    time.sleep(0.1)  # Simulate work
    return "completed"

# Usage
result = slow_function()  # Prints: ⏱️ slow_function: 0.1001s
""")

def run_performance_benchmark():
    """Run a simple performance benchmark."""
    print_step("Benchmark", "Performance Benchmarking")
    
    print("🧪 Running simple performance tests...")
    
    # CPU benchmark
    def cpu_intensive_task(n=1000000):
        """Simple CPU-bound task."""
        result = 0
        for i in range(n):
            result += i ** 0.5
        return result
    
    # Memory benchmark  
    def memory_intensive_task(size=10000000):
        """Simple memory allocation task."""
        data = [i for i in range(size)]
        return len(data)
    
    # Run benchmarks
    start_time = time.perf_counter()
    cpu_result = cpu_intensive_task()
    cpu_time = time.perf_counter() - start_time
    
    start_time = time.perf_counter()
    mem_result = memory_intensive_task()
    mem_time = time.perf_counter() - start_time
    
    # Get system info
    system_info = get_system_info()
    
    print(f"🖥️ System Information:")
    print(f"   CPU Cores: {system_info['cpu_count']}")
    print(f"   CPU Usage: {system_info['cpu_percent']:.1f}%")
    print(f"   Memory: {system_info['memory'].used / 1024**3:.1f}GB / {system_info['memory'].total / 1024**3:.1f}GB")
    
    if 'gpu_count' in system_info:
        print(f"   GPU: {system_info['gpu_name']}")
        print(f"   GPU Memory: {system_info['gpu_memory'] / 1024**3:.1f}GB")
    
    print(f"\n🏃 Benchmark Results:")
    print(f"   CPU Task: {cpu_time:.3f}s")
    print(f"   Memory Task: {mem_time:.3f}s")
    
    # Performance scoring (arbitrary baseline)
    cpu_score = 1000 / cpu_time  # Higher is better
    mem_score = 1000 / mem_time
    
    print(f"\n📊 Performance Scores:")
    print(f"   CPU Score: {cpu_score:.0f}")
    print(f"   Memory Score: {mem_score:.0f}")
    
    if cpu_score > 500:
        print("   💚 CPU Performance: Excellent")
    elif cpu_score > 200:
        print("   💛 CPU Performance: Good") 
    else:
        print("   ❤️ CPU Performance: Needs improvement")

def main():
    print_header("Module 5.1: Performance Optimization")
    
    # Step 1: Performance concepts overview
    explain_performance_concepts()
    input("\n🔍 Press Enter to continue to batching optimization...")
    
    # Step 2: Batching optimization
    demonstrate_batching_optimization()
    input("\n🔍 Press Enter to continue to memory optimization...")
    
    # Step 3: Memory optimization
    demonstrate_memory_optimization()
    input("\n🔍 Press Enter to continue to GPU optimization...")
    
    # Step 4: GPU optimization
    demonstrate_gpu_optimization()
    input("\n🔍 Press Enter to continue to caching strategies...")
    
    # Step 5: Caching strategies
    demonstrate_caching_strategies()
    input("\n🔍 Press Enter to continue to profiling tools...")
    
    # Step 6: Profiling and monitoring
    demonstrate_profiling_tools()
    input("\n🔍 Press Enter to run performance benchmark...")
    
    # Step 7: Performance benchmark
    run_performance_benchmark()
    input("\n🔍 Press Enter to see summary...")
    
    # Summary
    print_step("Summary", "What You Learned")
    
    print("""
🎯 Key Performance Optimization Concepts Covered:
  • Dynamic batching for improved throughput
  • Memory management and quantization techniques
  • GPU optimization with mixed precision and parallelism
  • Multi-level caching strategies (memory + Redis)
  • Performance profiling tools and techniques
  • Benchmarking and performance measurement

📊 Optimization Hierarchy (Impact vs Effort):
  1. 🟢 Easy wins: Batching, caching, connection pooling
  2. 🟡 Medium effort: Mixed precision, model quantization
  3. 🔴 Advanced: Custom CUDA kernels, distributed inference

🛠️ Production Performance Checklist:
  ✅ Implement dynamic batching
  ✅ Add multi-level caching  
  ✅ Enable mixed precision (FP16)
  ✅ Monitor memory usage
  ✅ Set up performance alerts
  ✅ Profile regularly in production
  ✅ Benchmark different configurations

💡 Performance Engineering Best Practices:
  • Measure first, optimize second
  • Focus on bottlenecks with highest impact
  • Test optimizations under realistic load
  • Monitor performance continuously in production
  • Keep optimization complexity reasonable

🔍 Hands-on Exercises:
  1. Implement dynamic batching for your model
  2. Set up Redis caching for predictions
  3. Profile your application with py-spy
  4. Compare FP32 vs FP16 inference performance
  5. Create custom performance monitoring dashboards
    
🚀 Ready for Module 5.2: Monitoring & Observability!
""")

if __name__ == "__main__":
    main()