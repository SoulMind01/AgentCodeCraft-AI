# AgentCodeCraft AI

A policy-driven AI assistant for automated code refactoring and review. This system analyzes code, applies organizational policies, and provides refactoring suggestions to improve code quality, security, and maintainability.

## Features

- **Policy-Aware Refactoring**: Automatically refactor code according to configurable security, governance, and style policies
- **Multi-Language Support**: Currently supports Python and Terraform (extensible to other languages)
- **Compliance Evaluation**: Real-time policy violation detection and compliance scoring
- **Code Quality Metrics**: Complexity analysis, test pass rates, and maintainability scores
- **Web Interface**: Streamlit-based UI for easy interaction
- **RESTful API**: FastAPI backend for programmatic access

## Prerequisites

- Python 3.10 or higher
- pip (Python package manager)
- Git (optional, for cloning the repository)

## Installation

1. **Clone or navigate to the project directory:**
   ```bash
   cd agentcodecraft
   ```

2. **Create a virtual environment (recommended):**
   ```bash
   python -m venv venv
   
   # On Windows:
   venv\Scripts\activate
   
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables (optional):**
   Create a `.env` file in the `agentcodecraft` directory:
   ```env
   DATABASE_URL=sqlite:///./agentcodecraft.db
   GEMINI_API_KEY=your_gemini_api_key_here
   ```
   Note: The Gemini API key is optional for now as the adapter uses a stub implementation.

## Running the Project

### Start the Backend API

In one terminal window:

```bash
cd agentcodecraft
uvicorn app.main:app --reload
```

The API will be available at `http://127.0.0.1:8000`

- API Documentation: `http://127.0.0.1:8000/docs`
- Root endpoint: `http://127.0.0.1:8000/`
- Health check: `http://127.0.0.1:8000/health`

### Start the Streamlit Frontend

In another terminal window:

```bash
cd agentcodecraft
streamlit run frontend/streamlit_app.py
```

The UI will open automatically in your browser at `http://localhost:8501`

## Deployment

### Production Environment Setup

For production deployment, you'll need to configure:

1. **Production Database**: Use PostgreSQL instead of SQLite
2. **Environment Variables**: Set secure configuration
3. **Process Management**: Use systemd, supervisor, or Docker
4. **Reverse Proxy**: Nginx or similar for SSL termination
5. **Monitoring**: Logging and health checks

### Option 1: Docker Deployment (Recommended)

#### Create Dockerfile

Create `Dockerfile` in the `agentcodecraft` directory:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose ports
EXPOSE 8000 8501

# Default command (can be overridden)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### Create docker-compose.yml

Create `docker-compose.yml` in the `agentcodecraft` directory:

```yaml
version: '3.8'

services:
  backend:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://agentcodecraft:password@db:5432/agentcodecraft
      - GEMINI_API_KEY=${GEMINI_API_KEY}
      - ENVIRONMENT=production
      - LOG_LEVEL=INFO
    depends_on:
      - db
    volumes:
      - ./policies:/app/policies
      - ./examples:/app/examples
    restart: unless-stopped
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4

  frontend:
    build: .
    ports:
      - "8501:8501"
    environment:
      - AGENTCODECRAFT_API=http://backend:8000
    depends_on:
      - backend
    restart: unless-stopped
    command: streamlit run frontend/streamlit_app.py --server.port 8501 --server.address 0.0.0.0

  db:
    image: postgres:15-alpine
    environment:
      - POSTGRES_USER=agentcodecraft
      - POSTGRES_PASSWORD=password
      - POSTGRES_DB=agentcodecraft
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped

volumes:
  postgres_data:
```

#### Deploy with Docker Compose

```bash
cd agentcodecraft

# Build and start services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Option 2: Google Cloud Run Deployment

#### Create Dockerfile (same as above)

#### Build and Push Container

```bash
# Set your GCP project
export PROJECT_ID=your-gcp-project-id
export SERVICE_NAME=agentcodecraft-ai

# Build container
gcloud builds submit --tag gcr.io/$PROJECT_ID/$SERVICE_NAME

# Deploy to Cloud Run
gcloud run deploy $SERVICE_NAME \
  --image gcr.io/$PROJECT_ID/$SERVICE_NAME \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars DATABASE_URL=postgresql://... \
  --set-env-vars GEMINI_API_KEY=... \
  --set-env-vars ENVIRONMENT=production \
  --memory 2Gi \
  --cpu 2 \
  --timeout 300 \
  --max-instances 10
```

#### Deploy Frontend Separately

```bash
# Build frontend container
docker build -t gcr.io/$PROJECT_ID/$SERVICE_NAME-frontend -f Dockerfile.frontend .

# Deploy frontend
gcloud run deploy $SERVICE_NAME-frontend \
  --image gcr.io/$PROJECT_ID/$SERVICE_NAME-frontend \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars AGENTCODECRAFT_API=https://$SERVICE_NAME-xxxxx.run.app \
  --memory 1Gi
```

### Option 3: Traditional Server Deployment (systemd)

#### 1. Install Dependencies on Server

```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install -y python3.11 python3.11-venv postgresql nginx

# Create application user
sudo useradd -m -s /bin/bash agentcodecraft
sudo su - agentcodecraft
```

#### 2. Deploy Application Code

```bash
# Clone or copy code to server
cd /home/agentcodecraft
git clone <your-repo> agentcodecraft
cd agentcodecraft

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

#### 3. Configure PostgreSQL Database

```bash
# As postgres user
sudo -u postgres psql

CREATE DATABASE agentcodecraft;
CREATE USER agentcodecraft WITH PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE agentcodecraft TO agentcodecraft;
\q
```

#### 4. Create Environment File

Create `/home/agentcodecraft/agentcodecraft/.env`:

```env
ENVIRONMENT=production
DATABASE_URL=postgresql://agentcodecraft:secure_password@localhost:5432/agentcodecraft
GEMINI_API_KEY=your_actual_api_key
LOG_LEVEL=INFO
```

#### 5. Create systemd Service for Backend

Create `/etc/systemd/system/agentcodecraft-backend.service`:

```ini
[Unit]
Description=AgentCodeCraft AI Backend
After=network.target postgresql.service

[Service]
Type=simple
User=agentcodecraft
WorkingDirectory=/home/agentcodecraft/agentcodecraft
Environment="PATH=/home/agentcodecraft/agentcodecraft/venv/bin"
ExecStart=/home/agentcodecraft/agentcodecraft/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

#### 6. Create systemd Service for Frontend

Create `/etc/systemd/system/agentcodecraft-frontend.service`:

```ini
[Unit]
Description=AgentCodeCraft AI Frontend
After=network.target agentcodecraft-backend.service

[Service]
Type=simple
User=agentcodecraft
WorkingDirectory=/home/agentcodecraft/agentcodecraft
Environment="PATH=/home/agentcodecraft/agentcodecraft/venv/bin"
Environment="AGENTCODECRAFT_API=http://localhost:8000"
ExecStart=/home/agentcodecraft/agentcodecraft/venv/bin/streamlit run frontend/streamlit_app.py --server.port 8501 --server.address 0.0.0.0
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

#### 7. Start Services

```bash
sudo systemctl daemon-reload
sudo systemctl enable agentcodecraft-backend
sudo systemctl enable agentcodecraft-frontend
sudo systemctl start agentcodecraft-backend
sudo systemctl start agentcodecraft-frontend

# Check status
sudo systemctl status agentcodecraft-backend
sudo systemctl status agentcodecraft-frontend
```

#### 8. Configure Nginx Reverse Proxy

Create `/etc/nginx/sites-available/agentcodecraft`:

```nginx
# Backend API
server {
    listen 80;
    server_name api.yourdomain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

# Frontend UI
server {
    listen 80;
    server_name yourdomain.com;

    location / {
        proxy_pass http://127.0.0.1:8501;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

Enable and restart Nginx:

```bash
sudo ln -s /etc/nginx/sites-available/agentcodecraft /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

#### 9. Set Up SSL with Let's Encrypt

```bash
sudo apt-get install certbot python3-certbot-nginx
sudo certbot --nginx -d yourdomain.com -d api.yourdomain.com
```

### Production Environment Variables

Create a `.env` file or set environment variables:

```env
# Environment
ENVIRONMENT=production

# Database (use PostgreSQL in production)
DATABASE_URL=postgresql://user:password@localhost:5432/agentcodecraft

# API Keys
GEMINI_API_KEY=your_actual_gemini_api_key

# Logging
LOG_LEVEL=INFO

# Security (if implementing auth)
SECRET_KEY=generate_a_secure_random_key_here
ALLOWED_ORIGINS=https://yourdomain.com,https://api.yourdomain.com
```

### Database Migration for Production

Update `app/db.py` to use PostgreSQL connection pooling:

```python
# In production, use connection pooling
from sqlalchemy.pool import QueuePool

engine = create_engine(
    settings.database_url,
    poolclass=QueuePool,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True
)
```

### Monitoring and Logging

#### View Logs

```bash
# systemd logs
sudo journalctl -u agentcodecraft-backend -f
sudo journalctl -u agentcodecraft-frontend -f

# Docker logs
docker-compose logs -f backend
docker-compose logs -f frontend
```

#### Health Checks

Set up monitoring to check:
- `http://your-api-domain/health` - Should return `{"status": "ok"}`
- Database connectivity
- API response times

### Security Considerations

1. **Never commit `.env` files** - Add to `.gitignore`
2. **Use strong database passwords** - Generate random passwords
3. **Enable HTTPS** - Use Let's Encrypt or similar
4. **Restrict database access** - Use firewall rules
5. **Rotate API keys regularly** - Especially Gemini API keys
6. **Implement rate limiting** - Consider using FastAPI middleware
7. **Sanitize user inputs** - Code uploads should be validated
8. **Regular updates** - Keep dependencies updated

### Scaling Considerations

- **Horizontal Scaling**: Run multiple backend instances behind a load balancer
- **Database**: Use connection pooling and read replicas for high traffic
- **Caching**: Consider Redis for session storage and policy caching
- **CDN**: Serve static assets through a CDN
- **Queue System**: For long-running refactoring tasks, use Celery with Redis/RabbitMQ

## Sample Test Workflow

### Option 1: Using the Streamlit UI (Recommended for First-Time Users)

1. **Start both services** (backend and frontend) as described above.

2. **Import a Policy Profile:**
   - In the Streamlit sidebar, select **"Policy Studio"**
   - Open the example policy file: `policies/example_python_policy.yaml`
   - Copy its contents and paste into the "Policy Document" text area
   - Click **"Import Policy Profile"**
   - Wait for the success message and verify the profile appears in the "Available Profiles" list

3. **Run a Refactoring Session:**
   - Switch to **"Refactor Workspace"** in the sidebar
   - Select the policy profile you just imported from the dropdown
   - Open the example code file: `examples/demo_input.py`
   - Copy its contents and paste into the "Code Snippet" text area
   - Optionally fill in metadata (repo name, branch, file path, user info)
   - Click **"Run Policy-Aware Refactor"**

4. **Review Results:**
   - **Compliance Summary**: Policy score, complexity delta, test pass rate
   - **Code Comparison**: Side-by-side view of original vs. refactored code
   - **Refactoring Suggestions**: Detailed list with rationale and confidence scores
   - **Policy Violations**: Remaining violations detected after refactoring

### Option 2: Using cURL (Command Line)

1. **Import a Policy Profile:**
   ```bash
   curl -X POST http://127.0.0.1:8000/policies/import \
     -H "Content-Type: application/json" \
     -d @- <<'JSON'
   {
     "document": "profile:\n  name: basic_python_security\n  domain: python\n  version: \"1.0\"\nrules:\n  - key: no_eval\n    description: \"Do not use eval()\"\n    category: security\n    expression: \"eval\\(\"\n    severity: high\n    auto_fixable: false\n  - key: no_hardcoded_password\n    description: \"Avoid hardcoded passwords\"\n    category: security\n    expression: \"password\\s*=\\s*[\\\"'].*[\\\"']\"\n    severity: medium\n    auto_fixable: false"
   }
   JSON
   ```
   
   Save the `policy_profile_id` from the response.

2. **Run a Refactoring Session:**
   ```bash
   curl -X POST http://127.0.0.1:8000/refactor \
     -H "Content-Type: application/json" \
     -d @- <<'JSON'
   {
     "user_id": "test-user-001",
     "user_name": "Test User",
     "role": "developer",
     "code": "password = \"123456\"\nprint(\"hello\")\neval(\"print(123)\")",
     "language": "python",
     "policy_profile_id": "PASTE_POLICY_PROFILE_ID_HERE",
     "file_path": "demo_input.py",
     "repo": "test-repo"
   }
   JSON
   ```

3. **View Session Details:**
   ```bash
   curl http://127.0.0.1:8000/sessions/PASTE_SESSION_ID_HERE
   ```

### Option 3: Using Python Script

Create a test script `test_refactor.py`:

```python
import requests
import json

BASE_URL = "http://127.0.0.1:8000"

# Step 1: Import policy
with open("policies/example_python_policy.yaml", "r") as f:
    policy_doc = f.read()

policy_response = requests.post(
    f"{BASE_URL}/policies/import",
    json={"document": policy_doc}
)
policy_data = policy_response.json()
policy_profile_id = policy_data["policy_profile_id"]
print(f"Imported policy: {policy_profile_id}")

# Step 2: Run refactor
with open("examples/demo_input.py", "r") as f:
    code = f.read()

refactor_response = requests.post(
    f"{BASE_URL}/refactor",
    json={
        "user_id": "test-user-001",
        "user_name": "Test User",
        "code": code,
        "language": "python",
        "policy_profile_id": policy_profile_id,
        "file_path": "demo_input.py"
    }
)
result = refactor_response.json()
print(f"\nSession ID: {result['session']['session_id']}")
print(f"Policy Score: {result['compliance']['policy_score']}%")
print(f"Suggestions: {len(result['suggestions'])}")
print(f"Violations: {len(result['violations'])}")
```

Run it:
```bash
python test_refactor.py
```

## Running Tests

Execute the test suite:

```bash
cd agentcodecraft
python -m pytest
```

Run with verbose output:
```bash
python -m pytest -v
```

Run specific test file:
```bash
python -m pytest tests/test_policy_engine.py
```

## Project Structure

```
agentcodecraft/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application entry point
│   ├── config.py               # Configuration and settings
│   ├── db.py                   # Database initialization
│   ├── models/
│   │   ├── domain.py           # Pydantic models for API
│   │   └── orm.py              # SQLAlchemy ORM models
│   ├── services/
│   │   ├── gemini_adapter.py   # LLM adapter (stub implementation)
│   │   ├── policy_engine.py    # Policy loading and evaluation
│   │   ├── static_analysis.py  # Code complexity and quality metrics
│   │   └── orchestrator.py     # Main refactoring orchestration
│   └── api/
│       ├── deps.py             # Dependency injection
│       ├── routes_refactor.py  # Refactor endpoints
│       ├── routes_policies.py  # Policy management endpoints
│       └── routes_sessions.py  # Session query endpoints
├── frontend/
│   └── streamlit_app.py        # Streamlit web interface
├── tests/
│   ├── test_api.py             # API endpoint tests
│   ├── test_policy_engine.py   # Policy engine tests
│   └── test_static_analysis.py # Static analysis tests
├── policies/
│   └── example_python_policy.yaml  # Example policy file
├── examples/
│   └── demo_input.py           # Example code to refactor
├── requirements.txt            # Python dependencies
└── README.md                   # This file
```

## API Endpoints

### Core Endpoints

- `GET /` - Root endpoint (health check message)
- `GET /health` - Health check
- `POST /refactor` - Trigger a refactoring session
- `GET /sessions/{session_id}` - Get session details
- `GET /policies` - List all policy profiles
- `POST /policies/import` - Import a new policy profile

### Example API Response

```json
{
  "session": {
    "session_id": "...",
    "status": "completed",
    "language": "python",
    "policy_profile_id": "..."
  },
  "suggestions": [
    {
      "suggestion_id": "...",
      "file_path": "demo_input.py",
      "start_line": 1,
      "end_line": 3,
      "original_code": "...",
      "proposed_code": "...",
      "rationale": "Normalized trailing whitespace",
      "confidence_score": 0.85
    }
  ],
  "compliance": {
    "policy_score": 0.0,
    "complexity_delta": -0.1,
    "test_pass_rate": 1.0,
    "latency_ms": 45,
    "token_usage": 150
  },
  "original_code": "password = \"123456\"\n...",
  "refactored_code": "password = \"123456\"\n...",
  "violations": [
    {
      "rule_key": "no_eval",
      "message": "Do not use eval()",
      "severity": "high"
    }
  ]
}
```

## Policy File Format

Policy files are YAML or JSON documents with the following structure:

```yaml
profile:
  name: policy_name
  domain: python  # or terraform, etc.
  version: "1.0"

rules:
  - key: rule_identifier
    description: "Human-readable description"
    category: security  # security, privacy, style, etc.
    expression: "regex_pattern"  # Pattern to detect violations
    severity: high  # high, medium, low
    auto_fixable: true  # or false
```

## Current Limitations

- **Gemini Adapter**: Currently uses a stub implementation that performs basic whitespace normalization. Real Gemini Pro 2.5 integration is planned.
- **Auto-fixing**: Policy violations are detected but not automatically fixed yet (even if `auto_fixable: true`).
- **Test Execution**: Test pass rate is currently stubbed. Real test execution requires integration with testing frameworks.

## Next Steps

1. Integrate real Gemini Pro 2.5 API for intelligent refactoring
2. Implement auto-fix capabilities for `auto_fixable` rules
3. Add support for more languages (Java, C#, etc.)
4. Integrate real test runners (pytest, unittest, etc.)
5. Add authentication and user management
6. Deploy to Google Cloud Run

## Troubleshooting

**Backend won't start:**
- Ensure port 8000 is not in use
- Check that all dependencies are installed: `pip install -r requirements.txt`

**Frontend can't connect to backend:**
- Verify the backend is running on `http://127.0.0.1:8000`
- Check the `AGENTCODECRAFT_API` environment variable in Streamlit (defaults to `http://127.0.0.1:8000`)

**Database errors:**
- Delete `agentcodecraft.db` and restart the backend (it will recreate the database)

**Policy import fails:**
- Verify YAML syntax is correct
- Check that `key` or `rule_key` is present in each rule
- Ensure expression patterns are properly escaped

## Contributing

This is a research project for CMPE 295A. For questions or issues, contact the project team.

## License

This project is part of academic research at San Jose State University.

