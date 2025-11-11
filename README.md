# aurea-orchestrator
Automated Unified Reasoning & Execution Agents

A REST API service with JWT authentication, role-based access control (RBAC), and multi-tenant organization support.

## Features

- **JWT Authentication**: Secure token-based authentication
- **Role-Based Access Control (RBAC)**: Three user roles with different permissions:
  - `admin`: Full access to all endpoints including approval
  - `reviewer`: Can create and update reviews
  - `dev`: Read-only access
- **Multi-Tenancy**: Organization-scoped data isolation
- **Protected Endpoints**: Write operations require authentication and appropriate roles

## Environment Variables

The following environment variables are required to run the service:

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `JWT_SECRET` | Yes | - | Secret key used to sign JWT tokens. Should be a strong random string. |
| `TOKEN_TTL` | No | `24h` | Token time-to-live duration. Format: Go duration string (e.g., `1h`, `30m`, `24h`). |
| `PORT` | No | `8080` | Port on which the server will listen. |

## Quick Start

1. Set required environment variables:
```bash
export JWT_SECRET="your-secret-key-here"
export TOKEN_TTL="24h"
```

2. Build and run the server:
```bash
go build -o aurea-orchestrator ./cmd/server
./aurea-orchestrator
```

## API Endpoints

### Public Endpoints

- `POST /login` - Authenticate and receive JWT token

### Protected Endpoints (require JWT token)

All protected endpoints require an `Authorization` header with format: `Bearer <token>`

#### User Endpoints
- `GET /api/me` - Get current authenticated user information

#### Organization Endpoints
- `GET /api/orgs/{id}/members` - List organization members (org-scoped)
- `POST /api/orgs/{id}/members` - Add member to organization (admin only)
- `DELETE /api/orgs/{id}/members/{userId}` - Remove member from organization (admin only)

#### Review Endpoints
- `GET /api/reviews` - List reviews (org-scoped)
- `POST /api/reviews` - Create a new review (reviewer/admin only)
- `GET /api/reviews/{id}` - Get review details (org-scoped)
- `PUT /api/reviews/{id}` - Update review (reviewer/admin only)
- `POST /api/reviews/{id}/approve` - Approve review (admin only)

## Authentication

### Login

Request:
```bash
curl -X POST http://localhost:8080/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "password"}'
```

Response:
```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": "1",
    "username": "admin",
    "email": "admin@example.com",
    "role": "admin",
    "org_id": "org1"
  }
}
```

### Using the Token

Include the token in the `Authorization` header for protected endpoints:

```bash
curl -X GET http://localhost:8080/api/me \
  -H "Authorization: Bearer <your-token>"
```

## Demo Users

The service includes three demo users for testing:

| Username | Password | Role | Organization |
|----------|----------|------|--------------|
| admin | password | admin | org1 |
| reviewer | password | reviewer | org1 |
| dev | password | dev | org2 |

## Security Features

- JWT tokens include user ID, role, and organization ID
- All write operations are protected by authentication
- RBAC checks prevent unauthorized actions
- Organization-scoped data isolation prevents cross-tenant access
- Token expiration enforced via TTL configuration

## Development

### Building
```bash
go build -o aurea-orchestrator ./cmd/server
```

### Running Tests
```bash
go test ./...
```

### Project Structure
```
.
├── cmd/
│   └── server/          # Application entry point
│       └── main.go
├── internal/
│   ├── auth/            # Authentication service
│   ├── handlers/        # HTTP request handlers
│   ├── middleware/      # JWT and RBAC middleware
│   └── models/          # Data models
├── go.mod
└── README.md
```