#!/bin/bash

# Exit on error
set -e

echo "🤖 Skylos AI - Demo de Agentes IA"
echo "=================================="

# Check if .env exists
if [ ! -f .env ]; then
    echo "❌ Error: Archivo .env no encontrado"
    echo "   Copia .env.example a .env y configura tu GEMINI_API_KEY"
    exit 1
fi

# Check if GEMINI_API_KEY is set
if ! grep -q "GEMINI_API_KEY=" .env || grep -q "GEMINI_API_KEY=$" .env; then
    echo "❌ Error: GEMINI_API_KEY no configurada en .env"
    echo "   Edita el archivo .env y agrega tu API key de Gemini"
    exit 1
fi

echo "✅ Configuración verificada"

# Build frontend
echo "📦 Construyendo frontend..."
(cd frontend && npm install && npm run build)

# Check if Docker is available and user wants to use it
if command -v docker &> /dev/null && [ "${USE_DOCKER:-}" = "true" ]; then
    echo "🐳 Usando Docker..."
    
    # Build backend image
    echo "🔨 Construyendo imagen Docker..."
    docker build --no-cache -t skylos-ai-demo .
    
    # Run backend container
    echo "🚀 Iniciando demo con Docker..."
    echo "Demo will be available at: http://localhost:8001"
    docker run --rm -p 8001:8000 --env-file .env skylos-ai-demo
else
    echo "🐍 Usando Python local..."
    
    # Check if uv is available
    if command -v uv &> /dev/null; then
        echo "📋 Instalando dependencias con uv..."
        uv install
        
        echo "🚀 Iniciando demo..."
        uv run python api/main.py
    else
        echo "❌ Error: uv no está instalado"
        echo "   Instala uv desde: https://docs.astral.sh/uv/getting-started/installation/"
        echo "   O usa Docker con: USE_DOCKER=true ./run.sh"
        exit 1
    fi
fi
