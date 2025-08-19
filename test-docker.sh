#!/bin/bash
# test-docker.sh - Test Docker deployment setup

echo "🚀 Testing FonDeDeNaJa Docker deployment setup..."

# Check if all required files exist
echo "Checking required files..."

if [ -f "Dockerfile.rust" ]; then
    echo "✅ Dockerfile.rust found"
else
    echo "❌ Dockerfile.rust missing"
    exit 1
fi

if [ -f "docker-compose.rust.yml" ]; then
    echo "✅ docker-compose.rust.yml found"
else
    echo "❌ docker-compose.rust.yml missing"
    exit 1
fi

if [ -f ".dockerignore" ]; then
    echo "✅ .dockerignore found"
else
    echo "❌ .dockerignore missing"
    exit 1
fi

if [ -f "deploy.sh" ]; then
    echo "✅ deploy.sh found"
    if [ -x "deploy.sh" ]; then
        echo "✅ deploy.sh is executable"
    else
        echo "❌ deploy.sh is not executable"
        chmod +x deploy.sh
        echo "✅ Made deploy.sh executable"
    fi
else
    echo "❌ deploy.sh missing"
    exit 1
fi

# Test Rust build
echo "Testing Rust build..."
if cargo check; then
    echo "✅ Rust code compiles successfully"
else
    echo "❌ Rust compilation failed"
    exit 1
fi

# Test deploy script help
echo "Testing deploy script..."
if ./deploy.sh help > /dev/null; then
    echo "✅ Deploy script works"
else
    echo "❌ Deploy script failed"
    exit 1
fi

# Check Docker and Docker Compose availability
echo "Checking Docker environment..."
if command -v docker > /dev/null; then
    echo "✅ Docker is available"
    if docker info > /dev/null 2>&1; then
        echo "✅ Docker daemon is running"
    else
        echo "⚠️  Docker daemon is not running"
    fi
else
    echo "⚠️  Docker is not installed"
fi

if command -v docker-compose > /dev/null; then
    echo "✅ Docker Compose is available"
else
    echo "⚠️  Docker Compose is not installed"
fi

echo ""
echo "🚀 Docker deployment setup test completed!"
echo ""
echo "To deploy:"
echo "  ./deploy.sh setup    # Complete setup and start"
echo "  ./deploy.sh start    # Start services"
echo "  ./deploy.sh status   # Check status"
echo ""
echo "Manual Docker commands:"
echo "  docker build -f Dockerfile.rust -t fondedenaja-rust ."
echo "  docker-compose -f docker-compose.rust.yml up -d"
echo ""