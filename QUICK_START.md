# 🚀 Quick Start Guide

**Get started with your Thai Language Model learning journey in 5 minutes!**

## 🎯 **Quick Launch**

```bash
# Navigate to the learning directory
cd /home/chanthaphan/project/learning

# Start the interactive learning system
python learn.py
```

## 📚 **Learning Modules Available**

### **Phase 1: Foundation** 🏗️
- **Module 1.1**: Python Package Architecture ✅
- **Module 1.2**: Configuration Management ✅

### **Phase 2: Machine Learning** 🧠  
- **Module 2.1**: Transformers & LoRA ✅
- **Module 2.2**: Model Training & Fine-tuning 🔄

### **Phase 3: API Development** 🌐
- **Module 3.1**: FastAPI Fundamentals 🔄
- **Module 3.2**: Advanced API Features 🔄

### **Phase 4: Deployment** 🐳
- **Module 4.1**: Docker Mastery 🔄
- **Module 4.2**: Production Deployment 🔄

## 🛠️ **Tools Available**

### **Progress Tracker** 📊
```bash
python learning/progress_tracker.py
```
- Track completed modules
- Add learning notes
- See progress overview

### **Individual Modules** 🎓
```bash
# Run specific modules directly
python learning/module_1_1_package_architecture.py
python learning/module_1_2_configuration.py
python learning/module_2_1_transformers_lora.py
```

## ⚡ **Quick Commands**

### **Test Your Setup**
```bash
# Verify package imports work
python -c "from thai_model.core.config import ModelConfig; print('✅ Setup working!')"

# Check your environment
python -c "import sys; print(f'Python: {sys.executable}')"
```

### **Explore Configuration**
```bash
# View config files
cat config/model_config.yaml
cat config/training_config.yaml

# Test config loading
python -c "
from thai_model.core.config import ModelConfig
config = ModelConfig.from_yaml('config/model_config.yaml')
print(f'Model: {config.model_name}')
"
```

### **Start API Server**
```bash
# Quick API launch
python scripts/api_server.py

# Or use the detailed startup script  
python scripts/start_api.sh
```

## 🎯 **Learning Tips**

### **For Beginners**
1. Start with **Module 1.1** (Package Architecture)
2. Complete modules in order for best understanding
3. Use the progress tracker to stay motivated
4. Take notes on key concepts

### **For Experienced Developers**
1. Jump to modules that interest you most
2. Focus on **Module 2.1** (Transformers) for ML concepts
3. Check **Module 3.1** (FastAPI) for API development
4. Use individual module scripts for targeted learning

### **Hands-on Practice**
- Modify configuration files and observe changes
- Experiment with different model parameters
- Test API endpoints with curl or Postman
- Run the Docker containers locally

## 📖 **Documentation**

### **Main Documentation**
- `LEARNING_PATH.md` - Complete curriculum with weekly schedule
- `README.md` - Project overview and features
- `docs/` - Detailed guides and references

### **Code Documentation**
- `thai_model/` - Main package with inline documentation
- `config/` - YAML configuration examples  
- `deployment/` - Docker and production setups

## 🆘 **Getting Help**

### **Common Issues**
1. **Import Errors**: Ensure you're in the virtual environment
   ```bash
   source llm-env/bin/activate  # Activate virtual environment
   ```

2. **Missing Dependencies**: Install required packages
   ```bash
   pip install -e .  # Install in development mode
   ```

3. **Configuration Errors**: Check YAML syntax
   ```bash
   python -c "import yaml; yaml.safe_load(open('config/model_config.yaml'))"
   ```

### **Next Steps**
1. Complete the foundation modules (1.1, 1.2)
2. Dive into machine learning concepts (2.1, 2.2)  
3. Build and deploy APIs (3.1, 3.2, 4.1, 4.2)
4. Track your progress and add notes

---

**🚀 Ready to become a Thai Language Model expert? Start your journey now!**

```bash
cd learning && python learn.py
```