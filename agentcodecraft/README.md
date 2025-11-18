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

