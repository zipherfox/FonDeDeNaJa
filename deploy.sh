#!/bin/bash
# deploy.sh - 🚀 Blazingly Fast Deployment Script for FonDeDeNaJa Rust OMR 🚀

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}🚀 $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check if Docker is installed
check_docker() {
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    
    print_success "Docker and Docker Compose are available"
}

# Build the Rust application
build_rust() {
    print_status "Building Rust OMR application..."
    if cargo build --release; then
        print_success "Rust build completed successfully"
    else
        print_error "Rust build failed"
        exit 1
    fi
}

# Build Docker image
build_docker() {
    print_status "Building Docker image..."
    if docker build -f Dockerfile.rust -t fondedenaja-rust .; then
        print_success "Docker image built successfully"
    else
        print_error "Docker build failed"
        exit 1
    fi
}

# Create necessary directories
setup_directories() {
    print_status "Setting up directories..."
    
    # Create directories with proper permissions
    mkdir -p uploads outputs templates
    
    # Set ownership to the container user (1000:1000)
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        sudo chown -R 1000:1000 uploads outputs 2>/dev/null || true
    fi
    
    print_success "Directories created and configured"
}

# Start services
start_services() {
    print_status "Starting FonDeDeNaJa Rust OMR services..."
    
    case $1 in
        "rust-only")
            docker-compose -f docker-compose.rust.yml up -d
            print_success "Rust OMR service started on http://localhost:3000"
            ;;
        "both")
            docker-compose up -d
            print_success "Both services started:"
            print_success "  - Rust OMR: http://localhost:3000"
            print_success "  - Streamlit: http://localhost:8501"
            ;;
        *)
            docker-compose -f docker-compose.rust.yml up -d
            print_success "Rust OMR service started on http://localhost:3000"
            ;;
    esac
}

# Stop services
stop_services() {
    print_status "Stopping services..."
    
    docker-compose -f docker-compose.rust.yml down 2>/dev/null || true
    docker-compose down 2>/dev/null || true
    
    print_success "Services stopped"
}

# Show status
show_status() {
    print_status "Service Status:"
    docker-compose -f docker-compose.rust.yml ps
    
    print_status "Checking health..."
    if curl -f http://localhost:3000/api/health &>/dev/null; then
        print_success "Rust OMR service is healthy"
    else
        print_warning "Rust OMR service is not responding"
    fi
}

# Show logs
show_logs() {
    print_status "Showing recent logs..."
    docker-compose -f docker-compose.rust.yml logs --tail=50 -f
}

# Clean up
cleanup() {
    print_status "Cleaning up Docker resources..."
    
    # Stop containers
    stop_services
    
    # Remove images (optional)
    if [[ "$1" == "--images" ]]; then
        docker rmi fondedenaja-rust 2>/dev/null || true
        print_success "Docker images removed"
    fi
    
    # Clean up build artifacts
    if [[ "$1" == "--all" ]] || [[ "$2" == "--all" ]]; then
        cargo clean
        docker system prune -f
        print_success "Build artifacts and Docker cache cleaned"
    fi
    
    print_success "Cleanup completed"
}

# Update deployment
update() {
    print_status "Updating FonDeDeNaJa Rust OMR..."
    
    # Stop services
    stop_services
    
    # Pull latest changes (if in git repo)
    if [ -d .git ]; then
        print_status "Pulling latest changes..."
        git pull
    fi
    
    # Rebuild
    build_rust
    build_docker
    
    # Restart services
    start_services
    
    print_success "Update completed successfully"
}

# Show help
show_help() {
    echo -e "${BLUE}🚀 FonDeDeNaJa Rust OMR Deployment Script 🚀${NC}"
    echo
    echo "Usage: $0 [COMMAND] [OPTIONS]"
    echo
    echo "Commands:"
    echo "  setup              - Complete setup: build + directories + start"
    echo "  build              - Build Rust application and Docker image"
    echo "  start [rust-only|both] - Start services (default: rust-only)"
    echo "  stop               - Stop all services"
    echo "  restart            - Stop and start services"
    echo "  status             - Show service status and health"
    echo "  logs               - Show and follow logs"
    echo "  update             - Update and restart services"
    echo "  cleanup [--images] [--all] - Clean up containers, images, and cache"
    echo "  help               - Show this help message"
    echo
    echo "Examples:"
    echo "  $0 setup                    # Complete setup"
    echo "  $0 start rust-only          # Start only Rust service"
    echo "  $0 start both               # Start both Rust and Python services"
    echo "  $0 cleanup --all            # Clean up everything"
    echo
}

# Main script logic
main() {
    case $1 in
        "setup")
            check_docker
            build_rust
            build_docker
            setup_directories
            start_services
            show_status
            ;;
        "build")
            check_docker
            build_rust
            build_docker
            ;;
        "start")
            check_docker
            setup_directories
            start_services $2
            ;;
        "stop")
            stop_services
            ;;
        "restart")
            stop_services
            start_services $2
            ;;
        "status")
            show_status
            ;;
        "logs")
            show_logs
            ;;
        "update")
            check_docker
            update
            ;;
        "cleanup")
            cleanup $2 $3
            ;;
        "help"|"--help"|"-h")
            show_help
            ;;
        "")
            print_warning "No command specified. Use 'help' to see available commands."
            show_help
            ;;
        *)
            print_error "Unknown command: $1"
            show_help
            exit 1
            ;;
    esac
}

# Run main function with all arguments
main "$@"