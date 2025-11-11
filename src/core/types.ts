import { OpenAPIV3 } from 'openapi-types';

/**
 * HTTP method types
 */
export type HttpMethod = 'GET' | 'POST' | 'PUT' | 'PATCH' | 'DELETE';

/**
 * Tool definition with OpenAPI/JSON Schema
 */
export interface ToolDefinition {
  /** Unique identifier for the tool */
  id: string;
  /** Human-readable name */
  name: string;
  /** Description of what the tool does */
  description: string;
  /** HTTP endpoint configuration */
  endpoint: {
    /** Base URL for the API */
    baseUrl: string;
    /** Path for the specific operation */
    path: string;
    /** HTTP method */
    method: HttpMethod;
  };
  /** OpenAPI schema for request parameters */
  schema: {
    /** Request parameters schema */
    parameters?: OpenAPIV3.ParameterObject[];
    /** Request body schema */
    requestBody?: OpenAPIV3.RequestBodyObject;
    /** Response schema */
    responses?: OpenAPIV3.ResponsesObject;
  };
  /** Authentication configuration */
  auth?: {
    /** Authentication type */
    type: 'bearer' | 'api-key' | 'basic' | 'oauth2';
    /** Header name for auth (e.g., 'Authorization') */
    headerName?: string;
    /** Environment variable name containing the credential */
    envVar: string;
  };
  /** Additional headers to include in requests */
  headers?: Record<string, string>;
}

/**
 * Request to execute a tool
 */
export interface ToolExecutionRequest {
  /** ID of the tool to execute */
  toolId: string;
  /** Agent making the request */
  agentId: string;
  /** Parameters for the tool execution */
  parameters?: Record<string, unknown>;
  /** Request body data */
  body?: unknown;
}

/**
 * Result of a tool execution
 */
export interface ToolExecutionResult {
  /** Whether the execution was successful */
  success: boolean;
  /** Response data from the tool */
  data?: unknown;
  /** Error message if execution failed */
  error?: string;
  /** HTTP status code */
  statusCode?: number;
  /** Execution timestamp */
  timestamp: Date;
}

/**
 * Audit log entry for tool execution
 */
export interface AuditLogEntry {
  /** Unique identifier for the audit log entry */
  id: string;
  /** Timestamp of the execution */
  timestamp: Date;
  /** ID of the tool that was executed */
  toolId: string;
  /** Agent that executed the tool */
  agentId: string;
  /** Parameters used in the execution */
  parameters?: Record<string, unknown>;
  /** Request body data */
  body?: unknown;
  /** Result of the execution */
  result: ToolExecutionResult;
  /** Duration of the execution in milliseconds */
  durationMs: number;
}

/**
 * Configuration for the allowlist
 */
export interface AllowlistConfig {
  /** Agent ID */
  agentId: string;
  /** List of tool IDs this agent can access */
  allowedTools: string[];
  /** Optional rate limiting */
  rateLimit?: {
    /** Maximum requests per time window */
    maxRequests: number;
    /** Time window in milliseconds */
    windowMs: number;
  };
}
