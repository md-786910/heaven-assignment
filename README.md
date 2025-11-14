# Issue Tracker Application

A full-stack Issue Tracker application with **authentication and authorization** built with FastAPI (Python) and React (JavaScript) with Tailwind CSS.

## Features

### Backend (FastAPI)
- **Authentication & Authorization**: JWT-based authentication with role-based access control
  - User registration and login
  - Password reset with code display (no email required)
  - Protected endpoints for write operations
  - Ownership validation (only creators can delete their issues)
- **Issue Management**: Full CRUD operations with optimistic concurrency control (versioning)
- **Comments**: Add comments to issues with validation (authentication required)
- **Labels**: Create and assign unique labels to issues
- **Bulk Updates**: Transactional bulk status updates with automatic rollback (authentication required)
- **CSV Import**: Upload CSV files to create multiple issues with validation and summary report (authentication required)
- **Reports**:
  - Top assignees by issue count
  - Average resolution time for resolved issues
- **Timeline**: Bonus feature showing complete issue history
- **Database**: PostgreSQL with proper indexes, constraints, and relationships

### Frontend (React + Tailwind CSS)
- **Authentication UI**:
  - Login page with redirect to intended destination
  - Registration page with auto-login
  - Password reset with code display UI
  - Conditional navigation (shows user info when logged in)
  - Logout functionality
- Clean and modern UI with Tailwind CSS
- Issue list with filtering and pagination (public access)
- Issue detail view with comments and timeline (public access for viewing)
- Create and edit issues with form validation (requires authentication)
- CSV import interface with result summary (requires authentication)
- Reports dashboard (public access)
- Protected routes with automatic redirect to login
- Responsive design

## Access Control

### Public Access (No Login Required)
- ✅ View all issues
- ✅ View issue details
- ✅ View reports
- ✅ View timeline

### Protected Operations (Authentication Required)
- 🔒 Create issues
- 🔒 Update issues
- 🔒 Delete issues (only by creator)
- 🔒 Add comments
- 🔒 Import CSV
- 🔒 Bulk status updates

**Note**: When users try to perform protected operations without logging in, they are automatically redirected to the login page and returned to their intended destination after successful authentication.

## Project Structure

```
heaven_venture_project/
├── backend/
│   ├── app/
│   │   ├── core/          # Configuration, database, and auth utilities
│   │   ├── models/        # SQLAlchemy models (data layer)
│   │   ├── schemas/       # Pydantic schemas (validation)
│   │   ├── controllers/   # Business logic layer ⭐
│   │   ├── routes/        # API endpoints (HTTP layer)
│   │   ├── init_db.py     # Database initialization
│   │   └── main.py        # FastAPI application
│   ├── requirements.txt
│   ├── .env
│   ├── docker compose.yml
│   ├── run.py
│   └── migrate_user_auth.py  # Database migration for auth fields
└── client/
    ├── src/
    │   ├── components/    # React components (ProtectedRoute)
    │   ├── pages/         # Page components (Login, Register, etc.)
    │   ├── services/      # API service with auth interceptors
    │   ├── App.jsx        # Main app with routing
    │   └── index.js       # Entry point
    ├── package.json
    └── index.html
```

## Architecture

The backend follows a **clean, layered architecture** with the **Controller Pattern**:

```
Routes (HTTP) → Controllers (Business Logic) → Models (Data) → Database
                      ↓
            Auth Middleware (JWT validation)
```

- **Routes**: Thin handlers for HTTP requests/responses
- **Controllers**: Core business logic and validation
- **Models**: Database ORM and schema
- **Schemas**: Request/response validation
- **Auth Middleware**: JWT token validation and user extraction

## Setup Instructions

### Prerequisites
- **Docker & Docker compose** (recommended - no Python installation needed)
- OR manually: Python 3.10+, PostgreSQL 15+
- **Node.js 18+** (for frontend)

---
## Quick Start with Automated Setup Script ⚡

The easiest way to get started is using the automated setup script that handles everything for you:

```bash
# Run the setup script (sets up backend, frontend, and tests API endpoints)
./startApp.sh
```

The setup script will:
1. ✅ Check all prerequisites (Docker, Node.js, npm, curl)
2. ✅ Set up backend services (PostgreSQL + FastAPI)
3. ✅ Set up and start the frontend development server
4. ✅ Test API endpoints to verify everything works
5. ✅ Display a summary with access URLs

After setup completes, access your application at:
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

To stop all services:
```bash
./stop.sh
```

---



## Quick Start with Docker (Recommended)

### Backend Setup with Docker

**No Python installation required!** The entire backend runs in Docker containers.

1. Navigate to the backend directory:
```bash
cd backend
```

2. Start both PostgreSQL and FastAPI backend with Docker compose:
```bash
docker compose up -d
```

This will:
- Start PostgreSQL database on port 5432
- Build and start FastAPI backend on port 8000
- Create a network for service communication
- Set up health checks and auto-restart

3. Check if services are running:
```bash
docker compose ps
```

4. View backend logs:
```bash
docker compose logs -f backend
```

The API will be available at `http://localhost:8000`
API documentation: `http://localhost:8000/docs`

### Stopping the Backend
```bash
docker compose down
```

To remove volumes (database data) as well:
```bash
docker compose down -v
```

---

## Manual Setup (Without Docker)

### Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Start PostgreSQL (using Docker):
```bash
docker compose up -d postgres
```

Or use your local PostgreSQL and update the `.env` file:
```
DATABASE_URL=postgresql://postgres:password@localhost:5432/issue_tracker
SECRET_KEY=your-secret-key-change-in-production
```

5. Run database migration (if needed for existing database):
```bash
python migrate_user_auth.py
```

6. Run the application:
```bash
python run.py
```

The API will be available at `http://localhost:8000`
API documentation: `http://localhost:8000/docs`

---

### Frontend Setup

**Important:** The frontend uses **Create React App (CRA)** for reliable Tailwind CSS support.

1. Navigate to the client directory:
```bash
cd client
```

2. Install dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm start
```

The frontend will be available at `http://localhost:3000`

## API Endpoints

### Authentication
- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/login` - Login and get JWT token
- `POST /api/v1/auth/forgot-password` - Request password reset code
- `POST /api/v1/auth/reset-password` - Reset password with code
- `GET /api/v1/auth/me` - Get current user (protected)
- `POST /api/v1/auth/logout` - Logout

### Issues
- `POST /api/v1/issues` - Create new issue (protected)
- `GET /api/v1/issues` - List issues (with filtering and pagination)
- `GET /api/v1/issues/{id}` - Get issue with comments & labels
- `PATCH /api/v1/issues/{id}` - Update issue (protected)
- `DELETE /api/v1/issues/{id}` - Delete issue (protected, creator only)
- `POST /api/v1/issues/bulk-status` - Bulk status update (protected)
- `POST /api/v1/issues/import` - CSV upload for issue import (protected)
- `GET /api/v1/issues/{id}/timeline` - Get issue history (Bonus)

### Comments
- `POST /api/v1/issues/{id}/comments` - Add comment to issue (protected)

### Labels
- `POST /api/v1/labels` - Create new label
- `GET /api/v1/labels` - List all labels
- `PUT /api/v1/labels/issues/{id}/labels` - Replace issue labels atomically

### Reports
- `GET /api/v1/reports/top-assignees` - Top assignees by issue count
- `GET /api/v1/reports/latency` - Average resolution time

### Users
- `POST /api/v1/users` - Create new user
- `GET /api/v1/users` - List all users
- `GET /api/v1/users/{id}` - Get specific user

## Database Schema

### Tables
- **users**: User information with authentication fields (hashed_password, reset_code, etc.)
- **issues**: Issues with versioning for concurrency control
- **comments**: Comments on issues
- **labels**: Unique labels
- **issue_labels**: Many-to-many relationship between issues and labels
- **issue_history**: Timeline of changes (Bonus feature)

### Key Features
- Foreign key constraints
- Unique constraints (username, email, label names)
- Indexes on frequently queried fields (status, assignee_id, created_at)
- Optimistic concurrency control using version field
- Automatic timestamp tracking
- Password hashing with bcrypt

## Testing the Application

### 1. Register a User
```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_doe",
    "email": "john@example.com",
    "full_name": "John Doe",
    "password": "password123"
  }'
```

Response includes a JWT token:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": { ... }
}
```

### 2. Create an Issue (with authentication)
```bash
TOKEN="your_jwt_token_here"

curl -X POST http://localhost:8000/api/v1/issues \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "title": "Test Issue",
    "description": "This is a test",
    "status": "open",
    "priority": "medium",
    "creator_id": 1
  }'
```

### 3. Update Issue (with version check and authentication)
```bash
curl -X PATCH http://localhost:8000/api/v1/issues/1 \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "status": "in_progress",
    "version": 1
  }'
```

### 4. Delete Issue (creator only)
```bash
curl -X DELETE http://localhost:8000/api/v1/issues/1 \
  -H "Authorization: Bearer $TOKEN"
```

### Using the Frontend
1. Go to http://localhost:3000
2. Click "Register" to create an account
3. You'll be auto-logged in
4. Click "New Issue" to create an issue
5. View public issues without logging out
6. Click "Logout" to sign out

## Key Implementation Details

### Authentication & Authorization
- **JWT Tokens**: 30-day expiration, HS256 algorithm
- **Password Hashing**: Bcrypt with automatic salt generation
- **Token Storage**: LocalStorage in frontend
- **Auto-Redirect**: Unauthorized access redirects to login with return URL
- **Axios Interceptors**: Automatic token injection and 401 handling
- **Ownership Validation**: Only issue creators can delete their issues

### Optimistic Concurrency Control
- Each issue has a `version` field that increments on every update
- Update requests must include the current version
- Returns 409 Conflict if version mismatch detected
- Prevents lost updates in concurrent scenarios

### Transactional Bulk Updates
- Uses database transactions for bulk operations
- Automatic rollback if any issue fails validation
- All-or-nothing guarantee for consistency

### CSV Import Validation
- Validates each row independently
- Returns detailed summary with success/failure status
- Continues processing even if some rows fail
- Creates issues in a single transaction

### Error Handling
- Comprehensive validation using Pydantic
- Proper HTTP status codes (401, 403, 404, 409, etc.)
- Detailed error messages
- Foreign key validation
- Automatic redirect on authentication errors

### Database Performance
- Indexes on frequently queried columns
- Efficient join queries for reports
- Connection pooling with SQLAlchemy
- Optimized queries with proper filtering

## Technologies Used

### Backend
- **FastAPI**: Modern Python web framework
- **SQLAlchemy**: ORM for database operations
- **Pydantic**: Data validation
- **PostgreSQL**: Relational database
- **Uvicorn**: ASGI server
- **python-jose**: JWT token handling
- **passlib**: Password hashing with bcrypt

### Frontend
- **React 19**: UI library
- **React Router DOM**: Client-side routing
- **Axios**: HTTP client with interceptors
- **Tailwind CSS**: Utility-first CSS framework
- **Create React App**: Build tool and dev server

## Security Configuration

### Environment Variables

All sensitive configuration data is stored in environment variables and loaded from a `.env` file in the `backend/` directory. **Never commit the `.env` file to version control.**

#### Required Environment Variables

Copy `backend/.env.example` to `backend/.env` and configure the following variables:

**Database Configuration:**
- `DATABASE_URL`: PostgreSQL connection string
- `POSTGRES_USER`: PostgreSQL username
- `POSTGRES_PASSWORD`: PostgreSQL password
- `POSTGRES_DB`: PostgreSQL database name

**JWT/Security Configuration:**
- `SECRET_KEY`: **CRITICAL** - Secret key for JWT token signing
  - Must be a strong, random string
  - Generate using: `openssl rand -hex 32`
  - **Never use the default value in production!**
- `ALGORITHM`: JWT algorithm (default: HS256)
- `ACCESS_TOKEN_EXPIRE_MINUTES`: Token expiration time in minutes (default: 43200 = 30 days)

#### Generate a Strong Secret Key

For production, generate a strong random secret key:

```bash
# Generate a secure random key
openssl rand -hex 32
```

Copy the output and set it as your `SECRET_KEY` in the `.env` file.

#### Protect Your .env File

- ✅ The `.env` file is listed in `.gitignore`
- ✅ Never commit `.env` to version control
- ✅ Use `.env.example` as a template (with dummy values)
- ✅ Keep `.env` file permissions restricted (e.g., `chmod 600 .env`)

### Production Security Checklist

Before deploying to production:

- [ ] Generate and set a strong `SECRET_KEY` using `openssl rand -hex 32`
- [ ] Change all default passwords (database, etc.)
- [ ] Use strong database passwords
- [ ] Enable HTTPS/TLS for API access
- [ ] Restrict database access to application server only
- [ ] Enable database connection encryption
- [ ] Set appropriate token expiration times
- [ ] Configure proper CORS settings (restrict allowed origins)
- [ ] Enable rate limiting on authentication endpoints
- [ ] Set up monitoring and logging
- [ ] Regular security updates
- [ ] Enforce strong password policies
- [ ] Review and restrict API endpoint access

### Security Features Implemented

- ✅ **No hardcoded secrets** - All sensitive data in environment variables
- ✅ **JWT Authentication** - Secure token-based auth with 30-day expiration
- ✅ **Password Hashing** - Bcrypt with automatic salt generation
- ✅ **Protected Routes** - Authentication required for write operations
- ✅ **Ownership Validation** - Only creators can delete their issues
- ✅ **Input Validation** - Pydantic schemas validate all inputs
- ✅ **SQL Injection Prevention** - SQLAlchemy ORM protects against SQL injection
- ✅ **Password Reset** - Time-limited reset codes (1 hour expiration)
- ✅ **Environment-based Config** - Easy to change per environment (dev/staging/prod)
- ✅ **.env excluded from git** - Prevents accidental commits of secrets

### Configuration Files

**Backend Configuration:**
- `/backend/.env` - Environment variables (excluded from git)
- `/backend/.env.example` - Template with dummy values (safe to commit)
- `/backend/.gitignore` - Excludes `.env` and other sensitive files
- `/backend/app/core/config.py` - Loads and validates environment variables
- `/backend/app/core/auth.py` - Uses config settings (not hardcoded values)

### Troubleshooting Security Issues

**"Could not validate credentials" Error:**
- If you change the `SECRET_KEY`, all existing JWT tokens become invalid
- Solution: Clear browser localStorage/cookies and log in again

**Environment Variables Not Loading:**
1. Ensure `.env` file exists in the `backend/` directory
2. Check file permissions
3. Verify the file format (no spaces around `=`)
4. Restart the application after changes

**Token Expired:**
- Tokens expire after `ACCESS_TOKEN_EXPIRE_MINUTES` (default: 30 days)
- Solution: Log in again to get a new token

## Development

### Backend Development with Docker (Recommended)
```bash
cd backend
docker compose up
# Code changes in app/ folder will auto-reload
```

### Backend Development (Manual)
```bash
cd backend
source venv/bin/activate
python run.py
```

### Frontend Development
```bash
cd client
npm start
```

### Unit Testing

The backend includes comprehensive unit tests with 88% code coverage covering all major API endpoints.

#### Running Tests

**With Docker (Recommended):**
```bash
cd backend
docker compose exec backend python -m pytest tests/ -v
```

**With Coverage Report:**
```bash
docker compose exec backend python -m pytest tests/ -v --cov=app --cov-report=term-missing --cov-report=html
# View HTML report at backend/htmlcov/index.html
```

**Run Specific Test Categories:**
```bash
# Authentication tests only
docker compose exec backend python -m pytest tests/ -v -m auth

# Issue management tests only
docker compose exec backend python -m pytest tests/ -v -m issues

# Comments tests only
docker compose exec backend python -m pytest tests/ -v -m comments

# Labels tests only
docker compose exec backend python -m pytest tests/ -v -m labels

# Reports tests only
docker compose exec backend python -m pytest tests/ -v -m reports

# User tests only
docker compose exec backend python -m pytest tests/ -v -m users
```

**Without Docker:**
```bash
cd backend
source venv/bin/activate
pip install -r requirements.txt
python -m pytest tests/ -v
```

#### Test Coverage

The test suite includes **46 tests** covering:

- **Authentication (13 tests)**
  - User registration (success, duplicate username, duplicate email)
  - Login (success, wrong password, non-existent user)
  - Get current user (authenticated, unauthenticated)
  - Password reset flow (forgot password, reset with code, invalid code)
  - Logout

- **Issue Management (14 tests)**
  - Create issues (with/without auth)
  - Get all issues
  - Get issue by ID
  - Update issues (with version control, with/without auth)
  - Delete issues (with/without auth)
  - Filter issues by status
  - Bulk status updates (with/without auth)
  - Issue timeline

- **Comments (5 tests)**
  - Add comments (with/without auth)
  - Comment validation (empty body)
  - Comments on non-existent issues
  - Comments in issue details

- **Labels (6 tests)**
  - Create labels
  - Duplicate label validation
  - Get all labels
  - Assign labels to issues
  - Replace labels (atomic operation)
  - Non-existent label handling

- **Reports (3 tests)**
  - Top assignees report
  - Latency/resolution time report
  - Empty reports handling

- **Users (5 tests)**
  - Create user (via registration)
  - Duplicate username validation
  - Get all users
  - Get user by ID
  - Non-existent user handling

#### Test Infrastructure

- **Framework**: pytest with async support
- **Test Database**: In-memory SQLite (for speed and isolation)
- **Test Client**: FastAPI TestClient
- **Fixtures**: Reusable fixtures for database, authentication, and test data
- **Coverage**: pytest-cov for code coverage reporting

## Production Build

### Backend
```bash
cd backend
pip install -r requirements.txt
python run.py
```

### Frontend
```bash
cd client
npm run build
# Deploy the build/ folder to your hosting service
```

## Troubleshooting

### Docker Issues

#### Backend container won't start
```bash
# Check if containers are running
docker compose ps

# View backend logs
docker compose logs backend

# Rebuild containers (after code changes)
docker compose up -d --build

# Check if PostgreSQL is healthy
docker compose logs postgres
```

#### Port already in use
```bash
# Find process using port 8000 or 5432
sudo lsof -i :8000
sudo lsof -i :5432

# Stop containers and restart
docker compose down
docker compose up -d
```

#### Database connection issues
```bash
# Check if PostgreSQL is ready
docker compose exec postgres pg_isready -U postgres

# Check network connectivity
docker compose exec backend ping postgres

# Restart with fresh database
docker compose down -v
docker compose up -d
```

#### View all container logs
```bash
docker compose logs -f
```

### Manual Setup Issues

#### Backend won't start
- Check PostgreSQL is running: `docker ps`
- Verify database credentials in `.env`
- Ensure Python 3.10+ is installed
- Activate virtual environment: `source venv/bin/activate`

### Frontend Tailwind CSS not working
- Clear cache: `rm -rf node_modules/.cache && npm start`
- Verify `postcss.config.js` and `tailwind.config.js` exist

### 401 Unauthorized errors
- Check if token is expired
- Verify token is being sent in Authorization header
- Check SECRET_KEY matches between requests

## License

MIT License
