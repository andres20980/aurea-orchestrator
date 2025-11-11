# Aurea Orchestrator - Tooling API

A comprehensive HTTP-based tooling API that allows AI agents to safely call external tools with schema validation, allowlist-based access control, and complete audit logging.

## Features

- 🔧 **HTTP Tools with Schema**: Define tools using OpenAPI 3.0 and JSON Schema
- 🔒 **Safe Allowlist**: Agent-based access control with tool allowlisting
- 📊 **Audit Logging**: Complete tracking of all tool executions
- ⚡ **Rate Limiting**: Configurable rate limits per agent
- ✅ **Schema Validation**: Automatic parameter validation using JSON Schema
- 🎯 **Sample Tools**: Pre-built integrations for GitHub, Jira, and Slack

## Installation

```bash
npm install aurea-orchestrator
```

## Quick Start

```typescript
import {
  ToolRegistry,
  Allowlist,
  AuditLogger,
  ToolExecutor,
  githubIssuesListTool,
} from 'aurea-orchestrator';

// Initialize components
const registry = new ToolRegistry();
const allowlist = new Allowlist();
const auditLogger = new AuditLogger();
const executor = new ToolExecutor(registry, allowlist, auditLogger);

// Register tools
registry.register(githubIssuesListTool);

// Configure agent access
allowlist.configure({
  agentId: 'my-agent',
  allowedTools: ['github-list-issues'],
  rateLimit: {
    maxRequests: 10,
    windowMs: 60000, // 1 minute
  },
});

// Execute a tool
const result = await executor.execute({
  toolId: 'github-list-issues',
  agentId: 'my-agent',
  parameters: {
    owner: 'octocat',
    repo: 'Hello-World',
    state: 'open',
  },
});

console.log(result);
```

## Core Components

### ToolRegistry

Manages tool definitions and schema validation.

```typescript
const registry = new ToolRegistry();

// Register a tool
registry.register(myToolDefinition);

// Get a tool
const tool = registry.get('tool-id');

// Get all tools
const allTools = registry.getAll();

// Validate parameters
const validation = registry.validateParameters('tool-id', { param: 'value' });
```

### Allowlist

Controls which agents can access which tools.

```typescript
const allowlist = new Allowlist();

// Configure agent access
allowlist.configure({
  agentId: 'agent-1',
  allowedTools: ['tool-1', 'tool-2'],
  rateLimit: {
    maxRequests: 10,
    windowMs: 60000,
  },
});

// Check if allowed
const allowed = allowlist.isAllowed('agent-1', 'tool-1');

// Check rate limit
const rateLimit = allowlist.checkRateLimit('agent-1');
```

### AuditLogger

Tracks all tool executions for security and monitoring.

```typescript
const auditLogger = new AuditLogger();

// Logs are automatically created by ToolExecutor
// Query logs
const allLogs = auditLogger.getAllLogs();
const agentLogs = auditLogger.getLogsByAgent('agent-1');
const toolLogs = auditLogger.getLogsByTool('tool-1');
const failedLogs = auditLogger.getFailedExecutions();

// Get statistics
const stats = auditLogger.getStats();
console.log(`Total executions: ${stats.totalExecutions}`);
console.log(`Success rate: ${(stats.successfulExecutions / stats.totalExecutions * 100).toFixed(2)}%`);
```

### ToolExecutor

Executes tools with validation, security checks, and audit logging.

```typescript
const executor = new ToolExecutor(registry, allowlist, auditLogger);

const result = await executor.execute({
  toolId: 'my-tool',
  agentId: 'my-agent',
  parameters: { key: 'value' },
  body: { data: 'payload' },
});

if (result.success) {
  console.log('Data:', result.data);
} else {
  console.error('Error:', result.error);
}
```

## Defining Custom Tools

Tools are defined using OpenAPI 3.0 schema:

```typescript
import { ToolDefinition } from 'aurea-orchestrator';

const myCustomTool: ToolDefinition = {
  id: 'my-custom-tool',
  name: 'My Custom Tool',
  description: 'Does something useful',
  endpoint: {
    baseUrl: 'https://api.example.com',
    path: '/api/v1/resource/{id}',
    method: 'POST',
  },
  schema: {
    parameters: [
      {
        name: 'id',
        in: 'path',
        required: true,
        schema: { type: 'string' },
        description: 'Resource ID',
      },
    ],
    requestBody: {
      required: true,
      content: {
        'application/json': {
          schema: {
            type: 'object',
            required: ['name'],
            properties: {
              name: { type: 'string' },
              value: { type: 'number' },
            },
          },
        },
      },
    },
    responses: {
      '200': { description: 'Success' },
    },
  },
  auth: {
    type: 'bearer',
    envVar: 'MY_API_TOKEN',
  },
  headers: {
    'Content-Type': 'application/json',
  },
};

registry.register(myCustomTool);
```

## Built-in Tools

### GitHub Tools

- **github-create-issue**: Create issues in GitHub repositories
- **github-list-issues**: List issues from GitHub repositories

Set `GITHUB_TOKEN` environment variable.

### Jira Tools

- **jira-create-issue**: Create Jira issues
- **jira-search-issues**: Search Jira using JQL

Set `JIRA_API_TOKEN` environment variable.

### Slack Tools

- **slack-post-message**: Post messages to Slack channels
- **slack-list-channels**: List Slack workspace channels

Set `SLACK_BOT_TOKEN` environment variable.

## Authentication

Tools support multiple authentication methods:

- **bearer**: Bearer token in Authorization header
- **api-key**: API key in custom header
- **basic**: Basic authentication
- **oauth2**: OAuth2 tokens

Credentials are read from environment variables specified in the tool definition:

```typescript
{
  auth: {
    type: 'bearer',
    headerName: 'Authorization', // optional, defaults to 'Authorization'
    envVar: 'MY_API_TOKEN',
  }
}
```

## Security Features

### Allowlist-based Access Control

Only agents explicitly granted access can execute tools:

```typescript
allowlist.configure({
  agentId: 'trusted-agent',
  allowedTools: ['safe-tool-1', 'safe-tool-2'],
});

// This will be denied
executor.execute({
  toolId: 'unsafe-tool',
  agentId: 'trusted-agent',
  // ...
});
```

### Rate Limiting

Prevent abuse with per-agent rate limits:

```typescript
allowlist.configure({
  agentId: 'agent-1',
  allowedTools: ['tool-1'],
  rateLimit: {
    maxRequests: 100,
    windowMs: 3600000, // 1 hour
  },
});
```

### Parameter Validation

All parameters are validated against JSON Schema before execution:

```typescript
// Will fail validation if required parameters are missing
// or if parameter types don't match the schema
const result = await executor.execute({
  toolId: 'my-tool',
  agentId: 'my-agent',
  parameters: { invalid: 'params' },
});
```

### Complete Audit Trail

Every tool execution is logged with:
- Timestamp
- Tool ID and Agent ID
- Parameters and request body
- Execution result (success/failure)
- Duration in milliseconds

## Example Usage

See `src/example.ts` for a complete working example:

```bash
npm run build
node dist/example.js
```

## Development

```bash
# Install dependencies
npm install

# Build
npm run build

# Run tests
npm test

# Run tests with coverage
npm run test:coverage

# Lint
npm run lint

# Format code
npm run format
```

## Testing

The project includes comprehensive test coverage:

```bash
npm test
```

Tests cover:
- Tool registration and validation
- Allowlist management and rate limiting
- Audit logging and statistics
- Parameter validation

## API Reference

### Types

```typescript
interface ToolDefinition {
  id: string;
  name: string;
  description: string;
  endpoint: {
    baseUrl: string;
    path: string;
    method: HttpMethod;
  };
  schema: {
    parameters?: OpenAPIV3.ParameterObject[];
    requestBody?: OpenAPIV3.RequestBodyObject;
    responses?: OpenAPIV3.ResponsesObject;
  };
  auth?: {
    type: 'bearer' | 'api-key' | 'basic' | 'oauth2';
    headerName?: string;
    envVar: string;
  };
  headers?: Record<string, string>;
}

interface ToolExecutionRequest {
  toolId: string;
  agentId: string;
  parameters?: Record<string, unknown>;
  body?: unknown;
}

interface ToolExecutionResult {
  success: boolean;
  data?: unknown;
  error?: string;
  statusCode?: number;
  timestamp: Date;
}

interface AllowlistConfig {
  agentId: string;
  allowedTools: string[];
  rateLimit?: {
    maxRequests: number;
    windowMs: number;
  };
}

interface AuditLogEntry {
  id: string;
  timestamp: Date;
  toolId: string;
  agentId: string;
  parameters?: Record<string, unknown>;
  body?: unknown;
  result: ToolExecutionResult;
  durationMs: number;
}
```

## License

ISC

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
