#!/bin/bash
# Setup script for Legal Intelligence Platform with Claude Integration

echo "🚀 Legal Intelligence Platform Setup"
echo "===================================="

# Check if running on macOS with RTX 4090 (eGPU setup)
if [[ "$OSTYPE" == "darwin"* ]]; then
    echo "⚠️  macOS detected - ensure eGPU is properly configured"
fi

# Create required directories
echo "📁 Creating project structure..."
mkdir -p {src/{core,debug,models,api,ui},k8s,monitoring,tests,scripts,claude-cli}

# Setup Python environment
echo "🐍 Setting up Python environment..."
python3 -m venv venv
source venv/bin/activate

# Create requirements.txt
cat > requirements.txt << EOF
# Core dependencies
anthropic>=0.18.0
neo4j>=5.0.0
milvus>=2.3.0
torch>=2.0.0
transformers>=4.30.0

# OCR dependencies
pytesseract>=0.3.10
paddlepaddle>=2.5.0
paddleocr>=2.6.0
opencv-python>=4.8.0

# Monitoring & debugging
prometheus-client>=0.18.0
opentelemetry-api>=1.20.0
opentelemetry-sdk>=1.20.0
jaeger-client>=4.8.0

# UI & API
gradio>=4.0.0
fastapi>=0.104.0
uvicorn>=0.24.0

# Utilities
tiktoken>=0.5.0
python-dotenv>=1.0.0
redis>=5.0.0
EOF

echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Setup environment variables
echo "🔐 Setting up environment variables..."
cat > .env << EOF
# Claude API Configuration
ANTHROPIC_API_KEY=your_api_key_here

# Database Configuration
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_password

# Redis Configuration
REDIS_HOST=localhost
REDIS_PORT=6379

# GPU Configuration
CUDA_VISIBLE_DEVICES=0
GPU_MEMORY_FRACTION=0.8

# Debugging Configuration
DEBUG_MODE=true
LOG_LEVEL=DEBUG
EOF

echo "⚠️  Please update .env with your actual API keys!"

# Create launcher script
cat > launch.sh << 'EOF'
#!/bin/bash
# Launch Legal Intelligence Platform

echo "🚀 Starting Legal Intelligence Platform..."

# Start Redis for persistent memory
redis-server --daemonize yes

# Start Neo4j
docker run -d \
  --name neo4j-legal \
  -p 7474:7474 -p 7687:7687 \
  -v $PWD/neo4j/data:/data \
  -v $PWD/neo4j/logs:/logs \
  neo4j:5.19.0-community

# Start monitoring stack
docker-compose -f monitoring/docker-compose.yml up -d

# Launch Claude CLI in new terminal
osascript -e 'tell app "Terminal" to do script "cd '$PWD' && source venv/bin/activate && python claude-cli/claude_persistent_cli.py"'

# Launch main application
python src/main.py

EOF

chmod +x launch.sh

echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Update .env with your Anthropic API key"
echo "2. Run ./launch.sh to start the platform"
echo "3. Access Claude CLI in the new terminal window"
