#!/bin/bash

# Legal Intelligence Platform - Deployment Script
# For RTX 4090 with 16GB RAM

set -e

echo "🚀 Legal Intelligence Platform Deployment"
echo "========================================"

# Check prerequisites
check_prerequisites() {
    echo "📋 Checking prerequisites..."
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        echo "❌ Docker not found. Please install Docker first."
        exit 1
    fi
    
    # Check Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        echo "❌ Docker Compose not found. Please install Docker Compose first."
        exit 1
    fi
    
    # Check NVIDIA Docker runtime
    if ! docker info | grep -q nvidia; then
        echo "⚠️  NVIDIA Docker runtime not found. GPU acceleration will not be available."
        echo "   Install nvidia-docker2 for GPU support."
    fi
    
    echo "✅ Prerequisites satisfied"
}

# Create directories
create_directories() {
    echo "📁 Creating directories..."
    
    mkdir -p /data/ocr/{input,output,processed}
    mkdir -p /data/graph
    mkdir -p ./postgres/init-scripts
    mkdir -p ./monitoring/prometheus
    mkdir -p ./monitoring/grafana/{dashboards,datasources}
    mkdir -p ./nginx/ssl
    
    # Set permissions
    chmod -R 755 /data/ocr
    
    echo "✅ Directories created"
}