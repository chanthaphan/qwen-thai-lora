# 🛠️ Scripts Directory

This directory contains all executable scripts for the Thai Model project, organized by functionality.

## 📁 **Directory Structure**

```
scripts/
├── README.md                    # This file
├── setup/                       # Setup and configuration scripts
│   ├── setup.sh                # Basic project setup
│   ├── setup_openai_key.sh     # OpenAI API key configuration
│   ├── setup_postgres.sh       # PostgreSQL setup (original)
│   └── setup_postgres_fixed.sh # PostgreSQL setup (enhanced)
├── deprecated/                  # Old/deprecated scripts
│   └── manage-old.sh           # Previous version of manage.sh
├── api_server.py               # FastAPI server launcher
├── launch_gui.sh               # GUI interface launcher
├── manage_vllm.sh              # vLLM server management
└── start_api.sh                # API server startup
```

## 🚀 **Main Scripts**

### **Setup Scripts** (`setup/`)
- **`setup.sh`** - Basic project initialization and dependencies
- **`setup_openai_key.sh`** - Interactive OpenAI API key configuration
- **`setup_postgres.sh`** - PostgreSQL database setup (original version)
- **`setup_postgres_fixed.sh`** - Enhanced PostgreSQL setup with proper authentication

### **Server Management**
- **`api_server.py`** - Python FastAPI server with OpenAI-compatible endpoints
- **`start_api.sh`** - Quick API server startup script
- **`manage_vllm.sh`** - Comprehensive vLLM server management (start/stop/status)
- **`launch_gui.sh`** - Launch GUI chat interface

## ⚡ **Quick Usage**

### **Setup Commands**
```bash
# Basic project setup
./scripts/setup/setup.sh

# Configure OpenAI API key
./scripts/setup/setup_openai_key.sh

# Setup PostgreSQL database
./scripts/setup/setup_postgres_fixed.sh
```

### **Server Commands**
```bash
# Start API server
./scripts/start_api.sh

# Manage vLLM server
./scripts/manage_vllm.sh start
./scripts/manage_vllm.sh status
./scripts/manage_vllm.sh stop

# Launch GUI interface
./scripts/launch_gui.sh
```

## 🎯 **Integration with Main Manager**

Most scripts are integrated with the main `./manage.sh` command:

```bash
# Uses scripts/setup/setup_openai_key.sh
./manage.sh setup-openai

# Uses scripts/setup/setup_postgres_fixed.sh  
./manage.sh setup-postgres

# Uses scripts/manage_vllm.sh
./manage.sh api

# Uses scripts/start_api.sh and others
./manage.sh chat-cli
./manage.sh chat-web
```

## 📋 **Script Categories**

| Category | Scripts | Purpose |
|----------|---------|---------|
| **Setup** | `setup/*.sh` | Initial configuration and dependencies |
| **Servers** | `*api*.py/sh`, `manage_vllm.sh` | Backend service management |
| **Interfaces** | `launch_gui.sh` | User interface launchers |
| **Deprecated** | `deprecated/*.sh` | Old versions (kept for reference) |

## 🔧 **Maintenance**

- **Setup scripts** are called during initial project configuration
- **Server scripts** are used for ongoing operations  
- **Deprecated scripts** are kept for reference but not actively used
- All scripts maintain executable permissions (`chmod +x`)

## 📝 **Adding New Scripts**

When adding new scripts:
1. Place them in appropriate subdirectory (`setup/`, etc.)
2. Make them executable: `chmod +x script_name.sh`
3. Update this README with description
4. Integrate with `./manage.sh` if needed
5. Update relevant documentation

---

**💡 Tip:** Most users should use `./manage.sh` commands instead of calling these scripts directly, as the manager provides better error handling and user experience.