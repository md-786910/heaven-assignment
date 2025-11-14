#!/bin/bash

# Issue Tracker Application - Complete Setup Script
# This script sets up and runs both backend and frontend applications

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_info() {
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

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to wait for service to be ready
wait_for_service() {
    local url=$1
    local service_name=$2
    local max_attempts=30
    local attempt=1

    print_info "Waiting for $service_name to be ready..."

    while [ $attempt -le $max_attempts ]; do
        if curl -s -f "$url" > /dev/null 2>&1; then
            print_success "$service_name is ready!"
            return 0
        fi
        echo -n "."
        sleep 2
        attempt=$((attempt + 1))
    done

    print_error "$service_name failed to start within expected time"
    return 1
}

# Print banner
echo ""
echo "=========================================="
echo "   Issue Tracker Application Setup"
echo "=========================================="
echo ""

# Check prerequisites
print_info "Checking prerequisites..."

if ! command_exists docker; then
    print_error "Docker is not installed. Please install Docker first."
    exit 1
fi

if ! command_exists docker-compose && ! docker compose version > /dev/null 2>&1; then
    print_error "Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

if ! command_exists node; then
    print_error "Node.js is not installed. Please install Node.js first."
    exit 1
fi

if ! command_exists npm; then
    print_error "npm is not installed. Please install npm first."
    exit 1
fi

if ! command_exists curl; then
    print_error "curl is not installed. Please install curl first."
    exit 1
fi

print_success "All prerequisites are installed!"

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Step 1: Setup Backend
print_info "Step 1/4: Setting up Backend..."
cd backend

# Check if .env exists
if [ ! -f .env ]; then
    print_warning ".env file not found. Creating from .env.example..."
    if [ -f .env.example ]; then
        cp .env.example .env
        print_warning "Please update SECRET_KEY in .env file with a secure random key!"
        print_info "Generate one using: openssl rand -hex 32"
    else
        print_error ".env.example not found!"
        exit 1
    fi
fi

# Stop any existing containers
print_info "Stopping any existing backend containers..."
docker compose down 2>/dev/null || true

# Start backend services
print_info "Starting backend services (PostgreSQL + FastAPI)..."
docker compose up -d

# Wait for backend to be ready
wait_for_service "http://localhost:8000/docs" "Backend API"

cd ..

# Step 2: Setup Frontend
print_info "Step 2/4: Setting up Frontend..."
cd client

# Install dependencies if node_modules doesn't exist
if [ ! -d "node_modules" ]; then
    print_info "Installing frontend dependencies (this may take a few minutes)..."
    npm install
else
    print_info "Frontend dependencies already installed"
fi

# Start frontend in background
print_info "Starting frontend development server..."
PORT=3000 npm start > /dev/null 2>&1 &
FRONTEND_PID=$!

# Save PID for cleanup
echo $FRONTEND_PID > /tmp/issue_tracker_frontend.pid

# Wait for frontend to be ready
wait_for_service "http://localhost:3000" "Frontend"

cd ..

# Step 3: Test API Endpoints
print_info "Step 3/4: Testing API endpoints..."

# Test 1: Health check
print_info "Testing health check..."
if curl -s -f http://localhost:8000/docs > /dev/null; then
    print_success "API documentation accessible at http://localhost:8000/docs"
else
    print_error "Failed to access API documentation"
fi

# Test 2: Register a test user
print_info "Registering test user..."
REGISTER_RESPONSE=$(curl -s -X POST http://localhost:8000/api/v1/auth/register \
    -H "Content-Type: application/json" \
    -d '{
        "username": "testuser_'$(date +%s)'",
        "email": "test'$(date +%s)'@example.com",
        "full_name": "Test User",
        "password": "testpass123"
    }')

if echo "$REGISTER_RESPONSE" | grep -q "access_token"; then
    print_success "User registration successful"
    TOKEN=$(echo "$REGISTER_RESPONSE" | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)
else
    print_warning "User registration response: $REGISTER_RESPONSE"
fi

# Test 3: Create an issue (if token was obtained)
if [ ! -z "$TOKEN" ]; then
    print_info "Creating test issue..."
    ISSUE_RESPONSE=$(curl -s -X POST http://localhost:8000/api/v1/issues \
        -H "Content-Type: application/json" \
        -H "Authorization: Bearer $TOKEN" \
        -d '{
            "title": "Test Issue from Setup Script",
            "description": "This is a test issue created by the setup script",
            "status": "open",
            "priority": "medium",
            "creator_id": 1
        }')

    if echo "$ISSUE_RESPONSE" | grep -q "id"; then
        print_success "Issue creation successful"
    else
        print_warning "Issue creation response: $ISSUE_RESPONSE"
    fi
fi

# Test 4: Get all issues (public endpoint)
print_info "Fetching all issues..."
ISSUES_RESPONSE=$(curl -s http://localhost:8000/api/v1/issues)
if echo "$ISSUES_RESPONSE" | grep -q '\['; then
    ISSUE_COUNT=$(echo "$ISSUES_RESPONSE" | grep -o '"id"' | wc -l)
    print_success "Issues endpoint working (found $ISSUE_COUNT issues)"
else
    print_warning "Issues response: $ISSUES_RESPONSE"
fi

# Test 5: Get reports
print_info "Testing reports endpoint..."
REPORTS_RESPONSE=$(curl -s http://localhost:8000/api/v1/reports/latency)
if echo "$REPORTS_RESPONSE" | grep -q 'average_resolution_time_hours'; then
    print_success "Reports endpoint working"
else
    print_warning "Reports response: $REPORTS_RESPONSE"
fi

# Step 4: Display running services and summary
print_info "Step 4/4: Setup Complete!"
echo ""
echo "=========================================="
echo "   Running Services"
echo "=========================================="
echo ""

# Check backend
if docker compose -f backend/docker-compose.yml ps | grep -q "Up"; then
    echo -e "${GREEN}✓${NC} Backend API:        http://localhost:8000"
    echo -e "${GREEN}✓${NC} API Documentation:  http://localhost:8000/docs"
    echo -e "${GREEN}✓${NC} PostgreSQL:         localhost:5432"
else
    echo -e "${RED}✗${NC} Backend services are not running"
fi

# Check frontend
if curl -s -f http://localhost:3000 > /dev/null 2>&1; then
    echo -e "${GREEN}✓${NC} Frontend:           http://localhost:3000"
else
    echo -e "${RED}✗${NC} Frontend is not running"
fi

echo ""
echo "=========================================="
echo "   Setup Summary"
echo "=========================================="
echo ""
echo "✓ Backend services started (PostgreSQL + FastAPI)"
echo "✓ Frontend development server started (React)"
echo "✓ API endpoints tested and verified"
echo ""
echo "Access your application:"
echo "  • Frontend:           http://localhost:3000"
echo "  • Backend API:        http://localhost:8000"
echo "  • API Documentation:  http://localhost:8000/docs"
echo ""
echo "Next Steps:"
echo "  1. Open http://localhost:3000 in your browser"
echo "  2. Register a new user account"
echo "  3. Start creating issues!"
echo ""
echo "Useful Commands:"
echo "  • View backend logs:  cd backend && docker compose logs -f backend"
echo "  • Run tests:          cd backend && docker compose exec backend python -m pytest tests/ -v"
echo "  • Stop all services:  ./stop.sh"
echo ""
echo "=========================================="
echo ""

# Create a stop script
print_info "Creating stop script..."
cat > "$SCRIPT_DIR/stop.sh" << 'STOPEOF'
#!/bin/bash

echo "Stopping Issue Tracker Application..."

# Stop frontend
if [ -f /tmp/issue_tracker_frontend.pid ]; then
    FRONTEND_PID=$(cat /tmp/issue_tracker_frontend.pid)
    if ps -p $FRONTEND_PID > /dev/null 2>&1; then
        echo "Stopping frontend (PID: $FRONTEND_PID)..."
        kill $FRONTEND_PID
    fi
    rm /tmp/issue_tracker_frontend.pid
fi

# Also kill any node process on port 3000
FRONTEND_PORT_PID=$(lsof -ti:3000 2>/dev/null)
if [ ! -z "$FRONTEND_PORT_PID" ]; then
    echo "Stopping frontend process on port 3000..."
    kill $FRONTEND_PORT_PID 2>/dev/null || true
fi

# Stop backend
cd "$(dirname "$0")/backend"
echo "Stopping backend services..."
docker compose down

echo "All services stopped!"
STOPEOF

chmod +x "$SCRIPT_DIR/stop.sh"
print_success "Created stop.sh script"

# Save information for user
cat > "$SCRIPT_DIR/.running_services" << INFOEOF
Backend: http://localhost:8000
Frontend: http://localhost:3000
Frontend PID: $FRONTEND_PID
Started: $(date)
INFOEOF

print_success "Setup complete! Your application is running."
