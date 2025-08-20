#!/bin/bash

# ==========================================
# KOREI ASSISTANT - DEPLOYMENT SCRIPT
# ==========================================

set -e  # Exit on any error

echo "🚀 Starting Korei Assistant Deployment..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if .env file exists
if [ ! -f .env ]; then
    print_error ".env file not found!"
    print_warning "Create .env file with your environment variables"
    exit 1
fi

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    print_error "Docker is not running! Please start Docker first."
    exit 1
fi

print_success "Docker is running ✓"

# Stop existing containers
print_status "Stopping existing containers..."
docker-compose down --remove-orphans || true

# Build the application
print_status "Building Docker image..."
docker-compose build --no-cache

# Start the services
print_status "Starting services..."
docker-compose up -d

# Wait for health check
print_status "Waiting for application to be healthy..."
sleep 10

# Check if application is healthy
if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    print_success "🎉 Application is healthy and running!"
    print_success "📍 API available at: http://localhost:8000"
    print_success "🔍 Health check: http://localhost:8000/health"
else
    print_error "❌ Application failed to start properly"
    print_warning "Checking logs..."
    docker-compose logs korei-api
    exit 1
fi

# Show running containers
print_status "Running containers:"
docker-compose ps

print_success "🚀 Deployment completed successfully!"
print_status "Use 'docker-compose logs -f' to view logs"
print_status "Use 'docker-compose down' to stop the application"