import axios, { AxiosRequestConfig } from 'axios';
import { ToolRegistry } from './registry';
import { Allowlist } from './allowlist';
import { AuditLogger } from '../audit/logger';
import { ToolDefinition, ToolExecutionRequest, ToolExecutionResult } from './types';

/**
 * Executes tool calls with security and audit logging
 */
export class ToolExecutor {
  constructor(
    private registry: ToolRegistry,
    private allowlist: Allowlist,
    private auditLogger: AuditLogger
  ) {}

  /**
   * Execute a tool with validation and audit logging
   */
  async execute(request: ToolExecutionRequest): Promise<ToolExecutionResult> {
    const startTime = Date.now();

    try {
      // Check if agent is allowed to use this tool
      if (!this.allowlist.isAllowed(request.agentId, request.toolId)) {
        const result: ToolExecutionResult = {
          success: false,
          error: `Agent '${request.agentId}' is not allowed to use tool '${request.toolId}'`,
          timestamp: new Date(),
        };
        this.logExecution(request, result, Date.now() - startTime);
        return result;
      }

      // Check rate limit
      const rateLimitCheck = this.allowlist.checkRateLimit(request.agentId);
      if (!rateLimitCheck.allowed) {
        const result: ToolExecutionResult = {
          success: false,
          error: rateLimitCheck.reason,
          timestamp: new Date(),
        };
        this.logExecution(request, result, Date.now() - startTime);
        return result;
      }

      // Get tool definition
      const tool = this.registry.get(request.toolId);
      if (!tool) {
        const result: ToolExecutionResult = {
          success: false,
          error: `Tool '${request.toolId}' not found`,
          timestamp: new Date(),
        };
        this.logExecution(request, result, Date.now() - startTime);
        return result;
      }

      // Validate parameters
      const validation = this.registry.validateParameters(request.toolId, request.parameters);
      if (!validation.valid) {
        const result: ToolExecutionResult = {
          success: false,
          error: `Parameter validation failed: ${validation.errors?.join(', ')}`,
          timestamp: new Date(),
        };
        this.logExecution(request, result, Date.now() - startTime);
        return result;
      }

      // Execute the HTTP request
      const result = await this.executeHttpRequest(tool, request);
      this.logExecution(request, result, Date.now() - startTime);
      return result;
    } catch (error) {
      const result: ToolExecutionResult = {
        success: false,
        error: error instanceof Error ? error.message : 'Unknown error',
        timestamp: new Date(),
      };
      this.logExecution(request, result, Date.now() - startTime);
      return result;
    }
  }

  private async executeHttpRequest(
    tool: ToolDefinition,
    request: ToolExecutionRequest
  ): Promise<ToolExecutionResult> {
    try {
      // Build URL with path parameters
      let url = tool.endpoint.baseUrl + tool.endpoint.path;

      // Replace path parameters
      if (request.parameters) {
        for (const [key, value] of Object.entries(request.parameters)) {
          url = url.replace(`{${key}}`, String(value));
        }
      }

      // Build request configuration
      const config: AxiosRequestConfig = {
        method: tool.endpoint.method,
        url,
        headers: { ...tool.headers },
      };

      // Add authentication
      if (tool.auth) {
        const authValue = process.env[tool.auth.envVar];
        if (!authValue) {
          throw new Error(`Authentication credential not found in env var: ${tool.auth.envVar}`);
        }

        const headerName = tool.auth.headerName || 'Authorization';
        if (tool.auth.type === 'bearer') {
          config.headers![headerName] = `Bearer ${authValue}`;
        } else if (tool.auth.type === 'api-key') {
          config.headers![headerName] = authValue;
        }
      }

      // Add query parameters for GET requests
      if (tool.endpoint.method === 'GET' && request.parameters) {
        config.params = request.parameters;
      }

      // Add body for POST/PUT/PATCH requests
      if (['POST', 'PUT', 'PATCH'].includes(tool.endpoint.method)) {
        config.data = request.body;
      }

      const response = await axios(config);

      return {
        success: true,
        data: response.data,
        statusCode: response.status,
        timestamp: new Date(),
      };
    } catch (error) {
      if (axios.isAxiosError(error)) {
        return {
          success: false,
          error: error.response?.data?.message || error.message,
          statusCode: error.response?.status,
          timestamp: new Date(),
        };
      }

      return {
        success: false,
        error: error instanceof Error ? error.message : 'Unknown error',
        timestamp: new Date(),
      };
    }
  }

  private logExecution(
    request: ToolExecutionRequest,
    result: ToolExecutionResult,
    durationMs: number
  ): void {
    this.auditLogger.log({
      timestamp: new Date(),
      toolId: request.toolId,
      agentId: request.agentId,
      parameters: request.parameters,
      body: request.body,
      result,
      durationMs,
    });
  }
}
