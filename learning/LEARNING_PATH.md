# 🎓 Thai Language Model - Complete Learning Path

**Master your Thai Language Model project step by step, from basics to advanced deployment and optimization.**

---

## 📚 **Learning Structure Overview**

This curriculum is designed to take you from understanding the basics to becoming an expert in:
- Python Package Development
- Machine Learning Model Fine-tuning
- API Development with FastAPI
- Production Deployment
- DevOps and Monitoring

---

## 🏗️ **Phase 1: Foundation (Week 1-2)**

### **Module 1.1: Python Package Architecture** 🐍
**Goal**: Understand modern Python project structure

#### **Learning Objectives**
- [ ] Understand `pyproject.toml` vs `setup.py`
- [ ] Master Python module imports and `__init__.py` files
- [ ] Learn package distribution and versioning
- [ ] Understand virtual environments and dependency management

#### **Hands-on Exercises**
```bash
# 1. Explore the package structure
cd /home/chanthaphan/project
python -c "import thai_model; print(thai_model.__version__)"

# 2. Test imports
python -c "from thai_model.core.config import ModelConfig; print('✅ Import successful')"

# 3. Install in development mode
pip install -e .
```

#### **Key Files to Study**
- `pyproject.toml` - Modern Python project configuration
- `thai_model/__init__.py` - Package initialization
- `thai_model/core/__init__.py` - Module organization

---

### **Module 1.2: Configuration Management** ⚙️
**Goal**: Master YAML-based configuration and dataclasses

#### **Learning Objectives**
- [ ] Understand dataclasses vs regular classes
- [ ] Learn YAML configuration patterns
- [ ] Master environment-specific configs
- [ ] Implement configuration validation

#### **Hands-on Exercises**
```python
# 1. Load and modify configuration
from thai_model.core.config import ModelConfig
config = ModelConfig.from_yaml("config/model_config.yaml")
print(f"Model: {config.model_name}")

# 2. Create custom configuration
custom_config = ModelConfig(
    model_name="custom-model",
    max_length=1024,
    temperature=0.8
)
custom_config.save("config/custom_config.yaml")
```

#### **Key Files to Study**
- `thai_model/core/config.py` - Configuration classes
- `config/model_config.yaml` - Model settings
- `config/training_config.yaml` - Training parameters

---

## 🤖 **Phase 2: Machine Learning Core (Week 3-4)**

### **Module 2.1: Understanding Transformers & LoRA** 🧠
**Goal**: Deep dive into the model architecture and fine-tuning

#### **Learning Objectives**
- [ ] Understand transformer architecture (Attention mechanism)
- [ ] Learn LoRA (Low-Rank Adaptation) technique
- [ ] Master tokenization for Thai language
- [ ] Understand model loading and inference

#### **Hands-on Exercises**
```python
# 1. Explore the model
from transformers import AutoTokenizer, AutoModelForCausalLM

tokenizer = AutoTokenizer.from_pretrained("Qwen/Qwen2.5-1.5B-Instruct")
text = "สวัสดี โลก"
tokens = tokenizer.encode(text)
print(f"Tokens: {tokens}")
print(f"Decoded: {tokenizer.decode(tokens)}")

# 2. Test model inference
from thai_model.core.model import ThaiModel
from thai_model.core.config import ModelConfig

config = ModelConfig.from_yaml("config/model_config.yaml")
# Note: This requires the model to be downloaded/available
```

#### **Key Files to Study**
- `thai_model/core/model.py` - Model wrapper class
- `thai_model/core/tokenizer.py` - Thai tokenization
- `models/qwen_thai_lora/` - Fine-tuned model checkpoints

---

### **Module 2.2: Model Training & Fine-tuning** 📈
**Goal**: Learn how to fine-tune models for Thai language

#### **Learning Objectives**
- [ ] Understand dataset preparation for Thai
- [ ] Learn LoRA configuration parameters
- [ ] Master training loops and optimization
- [ ] Implement model evaluation metrics

#### **Hands-on Exercises**
```python
# 1. Prepare training data
# Study the data preparation pipeline
# Understand Thai text preprocessing

# 2. Configure LoRA training
from peft import LoraConfig
lora_config = LoraConfig(
    r=16,
    lora_alpha=32,
    target_modules=["q_proj", "v_proj"],
    lora_dropout=0.1,
)

# 3. Monitor training progress
# Learn to use tensorboard/wandb for tracking
```

#### **Key Files to Study**
- `thai_model/training/` - Training pipeline (when implemented)
- `data/` directories - Training data structure
- Training configuration in `config/training_config.yaml`

---

## 🌐 **Phase 3: API Development (Week 5-6)**

### **Module 3.1: FastAPI Fundamentals** 🚀
**Goal**: Master modern API development with FastAPI

#### **Learning Objectives**
- [ ] Understand async/await programming
- [ ] Learn FastAPI routing and middleware
- [ ] Master request/response models with Pydantic
- [ ] Implement API documentation with OpenAPI

#### **Hands-on Exercises**
```python
# 1. Start the API server
cd /home/chanthaphan/project
python scripts/api_server.py

# 2. Test API endpoints
curl -X POST "http://localhost:8000/v1/chat/completions" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "thai-model",
    "messages": [{"role": "user", "content": "สวัสดี"}]
  }'

# 3. Explore API documentation
# Visit http://localhost:8000/docs
```

#### **Key Files to Study**
- `thai_model/api/fastapi_server.py` - Main API server
- `thai_model/api/models.py` - Pydantic request/response models
- `scripts/api_server.py` - Server launcher

---

### **Module 3.2: Advanced API Features** ⚡
**Goal**: Implement production-ready API features

#### **Learning Objectives**
- [ ] Implement streaming responses
- [ ] Add authentication and rate limiting
- [ ] Master error handling and logging
- [ ] Learn API versioning strategies

#### **Hands-on Exercises**
```python
# 1. Test streaming responses
import requests
response = requests.post(
    "http://localhost:8000/v1/chat/completions",
    json={
        "model": "thai-model",
        "messages": [{"role": "user", "content": "เล่าเรื่องสั้นให้ฟัง"}],
        "stream": True
    },
    stream=True
)

for line in response.iter_lines():
    if line:
        print(line.decode('utf-8'))

# 2. Add custom middleware
# Learn to implement logging, CORS, authentication
```

---

## 🐳 **Phase 4: Containerization & Deployment (Week 7-8)**

### **Module 4.1: Docker Mastery** 📦
**Goal**: Containerize the application for consistent deployment

#### **Learning Objectives**
- [ ] Understand Docker images vs containers
- [ ] Master multi-stage Docker builds
- [ ] Learn Docker Compose for orchestration
- [ ] Optimize images for production

#### **Hands-on Exercises**
```bash
# 1. Build Docker image
cd /home/chanthaphan/project/deployment/docker
docker build -t thai-model:latest -f Dockerfile.cpu .

# 2. Run container
docker run -p 8000:8000 thai-model:latest

# 3. Use Docker Compose
docker-compose up -d

# 4. Check logs
docker logs <container_id>
```

#### **Key Files to Study**
- `deployment/docker/Dockerfile` - Main Docker image
- `deployment/docker/Dockerfile.cpu` - CPU-optimized image
- `deployment/docker/docker-compose.yml` - Multi-service setup

---

### **Module 4.2: Production Deployment** 🏭
**Goal**: Deploy to production with proper DevOps practices

#### **Learning Objectives**
- [ ] Learn reverse proxy with Nginx
- [ ] Implement service management with systemd
- [ ] Set up monitoring with Prometheus
- [ ] Master environment management

#### **Hands-on Exercises**
```bash
# 1. Configure Nginx reverse proxy
sudo cp deployment/nginx/thai-model-api.nginx /etc/nginx/sites-available/
sudo ln -s /etc/nginx/sites-available/thai-model-api.nginx /etc/nginx/sites-enabled/
sudo systemctl reload nginx

# 2. Set up systemd service
sudo cp deployment/systemd/thai-model-api.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable thai-model-api
sudo systemctl start thai-model-api

# 3. Monitor with Prometheus
# Set up Prometheus using deployment/monitoring/prometheus.yml
```

#### **Key Files to Study**
- `deployment/nginx/thai-model-api.nginx` - Nginx configuration
- `deployment/systemd/thai-model-api.service` - Systemd service
- `deployment/monitoring/prometheus.yml` - Monitoring setup

---

## 📊 **Phase 5: Advanced Topics (Week 9-10)**

### **Module 5.1: Performance Optimization** ⚡
**Goal**: Optimize for production performance

#### **Learning Objectives**
- [ ] Learn model quantization techniques
- [ ] Implement caching strategies
- [ ] Master batch processing
- [ ] Optimize memory usage

#### **Hands-on Exercises**
```python
# 1. Model optimization
# Learn about INT8 quantization, ONNX conversion
# Implement model caching

# 2. API performance tuning
# Add Redis caching
# Implement connection pooling
# Load testing with locust/ab
```

---

### **Module 5.2: Monitoring & Observability** 📈
**Goal**: Implement comprehensive monitoring

#### **Learning Objectives**
- [ ] Set up application metrics
- [ ] Implement distributed tracing
- [ ] Create custom dashboards
- [ ] Set up alerting

#### **Hands-on Exercises**
```python
# 1. Add custom metrics
from prometheus_client import Counter, Histogram
request_count = Counter('requests_total', 'Total requests')
response_time = Histogram('response_time_seconds', 'Response time')

# 2. Implement health checks
# Add /health and /metrics endpoints

# 3. Create Grafana dashboards
# Visualize model performance metrics
```

---

## 🎯 **Learning Schedule & Milestones**

### **Week 1-2: Foundation**
- **Day 1-3**: Python package structure and imports
- **Day 4-7**: Configuration management and YAML
- **Day 8-10**: Virtual environments and dependency management
- **Day 11-14**: Practice building and testing the package

### **Week 3-4: Machine Learning**
- **Day 1-5**: Transformer architecture and tokenization
- **Day 6-10**: LoRA fine-tuning theory and practice
- **Day 11-14**: Model evaluation and optimization

### **Week 5-6: API Development**
- **Day 1-7**: FastAPI fundamentals and async programming
- **Day 8-14**: Advanced features and production readiness

### **Week 7-8: Deployment**
- **Day 1-7**: Docker containerization
- **Day 8-14**: Production deployment and DevOps

### **Week 9-10: Advanced Topics**
- **Day 1-7**: Performance optimization
- **Day 8-14**: Monitoring and observability

---

## 📋 **Daily Practice Routine**

### **Morning (1 hour): Theory**
- Read documentation and code
- Watch relevant tutorials
- Take notes on key concepts

### **Afternoon (2 hours): Hands-on**
- Work through exercises
- Modify and experiment with code
- Build small projects

### **Evening (30 minutes): Review**
- Review what you learned
- Plan next day's learning
- Update learning progress

---

## 🛠️ **Essential Tools to Master**

### **Development Environment**
- [ ] VS Code with Python extensions
- [ ] Git for version control
- [ ] Virtual environments (venv/conda)
- [ ] Jupyter notebooks for experimentation

### **Python Libraries**
- [ ] **torch** - Deep learning framework
- [ ] **transformers** - Hugging Face transformers
- [ ] **fastapi** - Modern API framework
- [ ] **pydantic** - Data validation
- [ ] **peft** - Parameter-efficient fine-tuning

### **DevOps Tools**
- [ ] **Docker** - Containerization
- [ ] **nginx** - Web server/reverse proxy
- [ ] **systemd** - Service management
- [ ] **prometheus** - Monitoring

---

## 🎓 **Assessment & Certification**

### **Module Completion Criteria**
For each module, you should be able to:
1. Explain the core concepts clearly
2. Complete all hands-on exercises
3. Modify the code for different use cases
4. Debug common issues independently

### **Final Project Ideas**
1. **Custom Fine-tuning**: Fine-tune for a specific Thai domain (legal, medical, etc.)
2. **Multi-modal API**: Extend API to handle images + text
3. **Chatbot Interface**: Build a complete chat application
4. **Performance Benchmark**: Compare different optimization techniques

---

## 📚 **Additional Resources**

### **Documentation**
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Transformers Documentation](https://huggingface.co/docs/transformers/)
- [Docker Documentation](https://docs.docker.com/)
- [Prometheus Documentation](https://prometheus.io/docs/)

### **Books**
- "Designing Data-Intensive Applications" by Martin Kleppmann
- "Natural Language Processing with Transformers" by Lewis Tunstall
- "Building Machine Learning Powered Applications" by Emmanuel Ameisen

### **Online Courses**
- Hugging Face NLP Course
- FastAPI Course by Testdriven.io
- Docker Mastery Course

---

## 🎯 **Success Metrics**

By the end of this learning path, you should be able to:
- [ ] Build and deploy a production-ready ML API
- [ ] Fine-tune language models for specific tasks
- [ ] Set up comprehensive monitoring and logging
- [ ] Implement CI/CD pipelines
- [ ] Scale applications using container orchestration
- [ ] Debug and optimize performance issues

---

**Ready to start your journey? Let's begin with Module 1.1: Python Package Architecture!** 🚀