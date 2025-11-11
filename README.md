# aurea-orchestrator
Automated Unified Reasoning & Execution Agents

A secure, isolated Docker-based sandbox orchestrator for executing untrusted code with resource limits, timeouts, and comprehensive logging.

## Features

- **Isolated Execution**: Code runs in isolated Docker containers with no network access
- **Resource Limits**: Configurable CPU and memory limits per execution
- **Timeouts**: Execution time limits to prevent runaway processes
- **Read-Only Filesystem**: Optional read-only workspace for enhanced security
- **Log Capture**: Automatic capture of stdout, stderr, and execution metadata
- **Artifact Management**: Support for capturing output files and artifacts
- **REST API**: Simple HTTP API for submitting and managing code executions
- **Multi-Language Support**: Python, JavaScript/Node.js, Bash (extensible)

## Quick Start

### Prerequisites

- Docker installed and running
- Python 3.11+
- pip for package management

### Installation

1. Clone the repository:
```bash
git clone https://github.com/andres20980/aurea-orchestrator.git
cd aurea-orchestrator
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Build the sandbox Docker image:
```bash
docker build -t aurea-sandbox:latest .
```

### Running the Server

Start the API server:
```bash
python src/main.py
```

Or with custom configuration:
```bash
SANDBOX_CPU_LIMIT=2.0 SANDBOX_MEMORY_LIMIT=1g PORT=8080 python src/main.py
```

The server will be available at `http://localhost:8000`

### API Documentation

Interactive API documentation is available at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Usage Examples

### Submit a Python code execution:

```bash
curl -X POST "http://localhost:8000/run" \
  -H "Content-Type: application/json" \
  -d '{
    "code": "print(\"Hello from sandbox!\")",
    "language": "python",
    "timeout": 30,
    "readonly": true
  }'
```

### Submit JavaScript code:

```bash
curl -X POST "http://localhost:8000/run" \
  -H "Content-Type: application/json" \
  -d '{
    "code": "console.log(\"Hello from Node.js!\")",
    "language": "javascript",
    "timeout": 30
  }'
```

### Example Response:

```json
{
  "run_id": "550e8400-e29b-41d4-a716-446655440000",
  "success": true,
  "exit_code": 0,
  "stdout": "Hello from sandbox!\n",
  "stderr": "",
  "execution_time": 0.234,
  "timed_out": false,
  "timeout": 30,
  "artifacts": {}
}
```

## Configuration

Environment variables for customization:

| Variable | Default | Description |
|----------|---------|-------------|
| `SANDBOX_IMAGE` | `aurea-sandbox:latest` | Docker image for sandbox |
| `SANDBOX_CPU_LIMIT` | `1.0` | CPU cores limit (e.g., 1.0 = 1 core) |
| `SANDBOX_MEMORY_LIMIT` | `512m` | Memory limit (e.g., 512m, 1g) |
| `SANDBOX_DEFAULT_TIMEOUT` | `30` | Default timeout in seconds |
| `HOST` | `0.0.0.0` | Server host |
| `PORT` | `8000` | Server port |

## API Endpoints

### `POST /run`
Submit code for execution in the sandbox.

**Request Body:**
```json
{
  "code": "string",
  "language": "python|javascript|bash",
  "timeout": 30,
  "files": {"filename": "content"},
  "readonly": true,
  "capture_artifacts": true
}
```

**Response:**
```json
{
  "run_id": "uuid",
  "success": boolean,
  "exit_code": int,
  "stdout": "string",
  "stderr": "string",
  "execution_time": float,
  "timed_out": boolean,
  "timeout": int,
  "artifacts": {}
}
```

### `GET /health`
Check service health and Docker availability.

### `POST /build-image`
Build/rebuild the sandbox Docker image.

## Security Considerations

### 🔒 Security Features

1. **Container Isolation**
   - Each execution runs in a separate, ephemeral Docker container
   - Containers are removed after execution
   - No data persists between executions

2. **Network Isolation**
   - Network access is disabled by default (`network_disabled: true`)
   - Prevents outbound connections and data exfiltration
   - Cannot communicate with other containers or external services

3. **Resource Limits**
   - CPU limits prevent CPU exhaustion attacks
   - Memory limits prevent memory bombs
   - Timeouts prevent infinite loops and long-running processes

4. **Filesystem Security**
   - Optional read-only filesystem prevents file modifications
   - Temporary workspace is isolated and cleaned up after execution
   - Non-root user (`sandbox`) runs code inside containers

5. **Process Isolation**
   - Docker's process isolation prevents container escape
   - Limited syscalls available to sandboxed processes
   - No privileged operations allowed

### ⚠️ Security Warnings

1. **Docker Daemon Access**
   - The service requires access to the Docker daemon
   - Run the service with minimal privileges
   - Consider using Docker socket proxy for additional security

2. **Resource Exhaustion**
   - Configure appropriate rate limiting at the API gateway level
   - Monitor resource usage to prevent DoS attacks
   - Set reasonable timeout and resource limit defaults

3. **Code Injection**
   - Always validate and sanitize input code
   - Never execute code with elevated privileges
   - Review code execution patterns for suspicious activity

4. **Container Escape**
   - Keep Docker updated to latest stable version
   - Use AppArmor/SELinux profiles for additional security
   - Consider using gVisor or Kata Containers for enhanced isolation

5. **Secrets Management**
   - Never pass secrets or credentials in code
   - Use environment variables or secret management systems
   - Audit logs for sensitive data exposure

### 🛡️ Best Practices

1. **Deployment**
   - Run behind a reverse proxy with rate limiting
   - Use HTTPS in production
   - Implement authentication and authorization
   - Deploy in a restricted network segment

2. **Monitoring**
   - Log all code executions with timestamps and user IDs
   - Monitor resource usage patterns
   - Set up alerts for suspicious activity
   - Regularly audit execution logs

3. **Maintenance**
   - Keep all dependencies updated
   - Regularly rebuild Docker images with security patches
   - Review and update resource limits based on usage
   - Perform security audits periodically

4. **Additional Hardening**
   - Use read-only root filesystem in production
   - Enable seccomp profiles
   - Drop unnecessary Linux capabilities
   - Use user namespaces for additional isolation

## Testing

Run the test suite:

```bash
pytest tests/ -v
```

Run tests with coverage:

```bash
pytest tests/ -v --cov=src --cov-report=html
```

## Development

### Project Structure

```
aurea-orchestrator/
├── src/
│   ├── sandbox/
│   │   ├── __init__.py
│   │   ├── runner.py      # Core sandbox runner
│   │   ├── schemas.py     # Pydantic models
│   │   └── api.py         # FastAPI application
│   └── main.py            # Entry point
├── tests/
│   ├── test_runner.py     # Runner tests
│   └── test_api.py        # API tests
├── Dockerfile             # Sandbox container image
├── requirements.txt       # Python dependencies
└── README.md
```

### Adding New Languages

To add support for a new programming language:

1. Update `_get_code_filename()` in `runner.py`:
```python
"ruby": "main.rb",
```

2. Update `_get_execution_command()` in `runner.py`:
```python
"ruby": ["ruby", code_file],
```

3. Ensure the language runtime is available in the Docker image (update `Dockerfile`)

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## License

MIT License - see LICENSE file for details

## Support

For issues, questions, or contributions, please visit:
https://github.com/andres20980/aurea-orchestrator/issues
