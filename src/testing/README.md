# Testing Module Documentation

## Overview
The Testing Module provides comprehensive testing capabilities for the Thai Language Model project. This module ensures your trained model works correctly and performs well on various tasks.

## 📁 Test Files Structure

```
src/testing/
├── __init__.py              # Module initialization
├── test_simple.py           # Quick model functionality test
├── test_model.py            # Comprehensive multi-case testing
├── test_streaming.py        # Server connectivity testing
├── evaluate_model.py        # Performance evaluation with metrics
├── manual_test.py           # Interactive testing interface
└── run_all_tests.py         # Complete test suite runner
```

## 🧪 Testing Types

### 1. Simple Model Test (`test_simple.py`)
- **Purpose**: Quick verification that the model loads and generates text
- **Runtime**: ~13 seconds
- **Usage**: `./llm-env/bin/python src/testing/test_simple.py`
- **What it tests**:
  - Model loading (base model + LoRA adapter)
  - Basic text generation
  - Thai language processing

### 2. Comprehensive Model Test (`test_model.py`)
- **Purpose**: Detailed testing with multiple Thai news articles
- **Runtime**: ~21 seconds
- **Usage**: `./llm-env/bin/python src/testing/test_model.py`
- **What it tests**:
  - Multiple test cases (Technology, Health, Environment)
  - Summarization quality on different topics
  - Model consistency across various inputs

### 3. Streaming Connection Test (`test_streaming.py`)
- **Purpose**: Verify server connectivity for web interfaces
- **Runtime**: ~5 seconds
- **Usage**: `./llm-env/bin/python src/testing/test_streaming.py`
- **What it tests**:
  - Ollama server connection (external models)
  - vLLM server connection (your trained model)
  - Available model listing

### 4. Model Evaluation (`evaluate_model.py`)
- **Purpose**: Performance metrics and detailed analysis
- **Runtime**: ~20 seconds
- **Usage**: `./llm-env/bin/python src/testing/evaluate_model.py`
- **What it provides**:
  - Compression ratio analysis
  - Generation time measurements
  - Structured evaluation report (JSON)
  - Performance statistics

### 5. Manual Interactive Test (`manual_test.py`)
- **Purpose**: Interactive testing for custom inputs
- **Usage**: 
  - Interactive: `./llm-env/bin/python src/testing/manual_test.py`
  - Command line: `./llm-env/bin/python src/testing/manual_test.py "your text here"`
- **Features**:
  - Real-time testing with custom Thai text
  - Sample text suggestions
  - Character count analysis

### 6. Complete Test Suite (`run_all_tests.py`)
- **Purpose**: Run all tests automatically with reporting
- **Runtime**: ~59 seconds total
- **Usage**: `./llm-env/bin/python src/testing/run_all_tests.py`
- **Features**:
  - Automated test execution
  - Pass/fail reporting
  - Execution time tracking
  - Summary statistics

## 📊 Test Results Analysis

### Current Model Performance
Based on recent test runs:

- ✅ **Model Loading**: Successful (base + LoRA adapter)
- ✅ **Text Generation**: Working (Thai language output)
- ✅ **Multiple Topics**: Handles Technology, Health, Environment
- ✅ **Server Connections**: Ollama ✅, vLLM ❌ (not running)

### Performance Metrics
- **Average Generation Time**: 3.5-4.0 seconds per summary
- **Compression Ratio**: 0.73-0.78 (good text reduction)
- **Model Size**: 17MB LoRA adapter + 3GB base model
- **Memory Usage**: Fits on GPU with float16 precision

### Quality Observations
- ✅ Generates fluent Thai text
- ⚠️ Sometimes hallucinations occur (common in fine-tuned models)
- ✅ Maintains Thai cultural context
- ⚠️ Occasional topic drift (needs more training data)

## 🔧 Testing Best Practices

### 1. Regular Testing Workflow
```bash
# Quick check during development
./llm-env/bin/python src/testing/test_simple.py

# Comprehensive evaluation before deployment
./llm-env/bin/python src/testing/run_all_tests.py

# Interactive testing for specific cases
./llm-env/bin/python src/testing/manual_test.py
```

### 2. Performance Monitoring
```bash
# Generate evaluation reports
./llm-env/bin/python src/testing/evaluate_model.py

# Check generated reports
ls -la evaluation_report_*.json
```

### 3. Troubleshooting

#### Model Loading Issues
- Verify model path: `./models/qwen_thai_lora/`
- Check adapter files exist: `adapter_config.json`, `adapter_model.safetensors`
- Ensure sufficient GPU memory

#### Poor Generation Quality
- Adjust generation parameters (temperature, top_p)
- Increase max_new_tokens for longer summaries
- Consider additional training rounds

#### Server Connection Issues
- Ollama: Check `OLLAMA_HOST` environment variable
- vLLM: Ensure server is running on correct port
- Network: Verify firewall/port accessibility

## 🎯 Quality Criteria

### What Good Test Results Look Like:
- ✅ All tests pass within expected time limits
- ✅ Generated summaries are relevant to input
- ✅ Thai grammar and vocabulary are appropriate
- ✅ Compression ratios between 0.6-0.9
- ✅ Generation times under 10 seconds per case

### Red Flags:
- ❌ Model fails to load or crashes
- ❌ Generated text is gibberish or wrong language
- ❌ Extremely slow generation (>30s per summary)
- ❌ Very poor compression (>1.0 ratio = expansion)
- ❌ Consistent hallucinations unrelated to input

## 📈 Continuous Improvement

### Metrics to Track:
1. **BLEU/ROUGE Scores** (against reference summaries)
2. **Generation Speed** (tokens per second)
3. **Memory Usage** (GPU/CPU consumption)
4. **User Satisfaction** (manual evaluation)

### Future Enhancements:
- Automated ROUGE evaluation against gold standard
- Batch testing for performance optimization  
- A/B testing between model versions
- Integration with CI/CD for automated testing

## 🏁 Testing Checklist

Before deploying your model:
- [ ] All unit tests pass (`run_all_tests.py`)
- [ ] Manual testing with domain-specific text
- [ ] Performance evaluation report generated
- [ ] Server connectivity verified
- [ ] Memory usage within acceptable limits
- [ ] Generation quality manually verified

Your Thai Language Model is ready for deployment when all these criteria are met!