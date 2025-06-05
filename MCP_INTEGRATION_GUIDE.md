# MCP Integration for Legal Intelligence Platform

## 🔗 Connecting to Your Existing MCP Setup

### 1. Add to MCP Server Registry
```json
{
  "legal-intelligence": {
    "command": "python",
    "args": ["/Users/mathieuwauters/Downloads/legal-intelligence-platform/src/mcp_server.py"],
    "env": {
      "PYTHONPATH": "/Users/mathieuwauters/Downloads/legal-intelligence-platform"
    }
  }
}
```

### 2. Create MCP Server for Debugging
```python
# src/mcp_server.py
import json
import sys
from typing import Dict, Any

class LegalIntelligenceMCP:
    def __init__(self):
        self.ocr_debugger = OCRDebugger()
        self.graph_debugger = GraphQueryDebugger()
        self.training_debugger = TrainingSimulatorDebugger()
    
    async def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        method = request.get('method')
        
        if method == 'debug_ocr':
            return await self.debug_ocr(request['params'])
        elif method == 'debug_graph':
            return await self.debug_graph_query(request['params'])
        elif method == 'debug_training':
            return await self.debug_training_session(request['params'])
        
    async def debug_ocr(self, params):
        """Debug OCR accuracy in real-time"""
        image_path = params['image_path']
        results = self.ocr_debugger.debug_ocr_pipeline(image_path)
        return {
            'accuracy': results['accuracy_metrics'],
            'debug_images': results['preprocessing_steps']
        }
```

### 3. Real-Time Debugging Dashboard
```python
# monitoring/realtime_dashboard.py
import gradio as gr
from src.debug import OCRDebugger, GraphQueryDebugger

def create_debugging_dashboard():
    ocr_debug = OCRDebugger()
    graph_debug = GraphQueryDebugger()
    
    with gr.Blocks() as dashboard:
        gr.Markdown("# Legal Intelligence Platform - Real-Time Debug")
        
        with gr.Tab("OCR Debugging"):
            image_input = gr.Image(type="filepath")
            ocr_button = gr.Button("Debug OCR")
            ocr_output = gr.JSON()
            
            ocr_button.click(
                fn=ocr_debug.debug_ocr_pipeline,
                inputs=image_input,
                outputs=ocr_output
            )
        
        with gr.Tab("Graph Performance"):
            query_input = gr.Textbox(label="Cypher Query")
            graph_button = gr.Button("Profile Query")
            graph_output = gr.JSON()
            
            graph_button.click(
                fn=graph_debug.profile_query,
                inputs=query_input,
                outputs=graph_output
            )
    
    return dashboard

if __name__ == "__main__":
    dashboard = create_debugging_dashboard()
    dashboard.launch(server_name="0.0.0.0", server_port=7860)
```

### 4. Git Repository Setup
```bash
cd /Users/mathieuwauters/Downloads/legal-intelligence-platform

# Initialize git (already done)
git add .
git commit -m "Add debugging framework and Claude integration"

# Create .gitignore
cat > .gitignore << EOF
# Environment
.env
venv/
__pycache__/

# Data
*.db
*.log
debug_output/
graph_debug/
training_debug/

# Models
models/
*.gguf
*.bin

# IDE
.vscode/
.idea/
*.swp

# OS
.DS_Store
Thumbs.db
EOF

git add .gitignore
git commit -m "Add gitignore"

# Set up remote (replace with your repo)
git remote add origin https://github.com/yourusername/legal-intelligence-platform.git
git push -u origin main
```

## 🚀 Quick Launch Commands

```bash
# 1. Start all services
./launch.sh

# 2. Open debugging dashboard
open http://localhost:7860

# 3. Start Claude CLI in evidence mode
python claude-cli/claude_persistent_cli.py --evidence-mode

# 4. Monitor GPU usage
watch -n 1 nvidia-smi

# 5. View real-time logs
tail -f *.log
```

## 💾 Thread Memory Compaction (Updated)

```json
{
  "project": "legal-intelligence-platform",
  "location": "/Users/mathieuwauters/Downloads/legal-intelligence-platform",
  "git_initialized": true,
  "components": {
    "ocr": ["tesseract", "paddleocr", "debugging_framework"],
    "graph": ["neo4j", "performance_profiler"],
    "llm": ["claude_api", "persistent_memory", "zero_temperature"],
    "training": ["gamification", "ux_debugger"],
    "monitoring": ["realtime_dashboard", "mcp_integration"]
  },
  "claude_integration": {
    "cli_tool": "claude_persistent_cli.py",
    "features": ["unlimited_threads", "file_persistence", "evidence_mode"],
    "api_required": true,
    "separate_from_claude_max": true
  },
  "debugging_priorities": [
    "ocr_accuracy",
    "graph_query_performance",
    "attorney_training_ux"
  ],
  "next_steps": [
    "get_anthropic_api_key",
    "update_env_file",
    "run_setup_script",
    "test_claude_cli"
  ]
}
```
