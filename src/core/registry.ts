import { ToolDefinition } from './types';
import Ajv, { ValidateFunction } from 'ajv';

/**
 * Registry for managing tool definitions
 */
export class ToolRegistry {
  private tools: Map<string, ToolDefinition> = new Map();
  private validators: Map<string, ValidateFunction> = new Map();
  private ajv: Ajv;

  constructor() {
    this.ajv = new Ajv({ allErrors: true, strict: false });
  }

  /**
   * Register a new tool
   */
  register(tool: ToolDefinition): void {
    if (this.tools.has(tool.id)) {
      throw new Error(`Tool with id '${tool.id}' is already registered`);
    }

    // Validate the tool definition
    this.validateToolDefinition(tool);

    // Store the tool
    this.tools.set(tool.id, tool);

    // Create validator for parameters if schema exists
    if (tool.schema.parameters || tool.schema.requestBody) {
      this.createValidator(tool);
    }
  }

  /**
   * Get a tool by ID
   */
  get(toolId: string): ToolDefinition | undefined {
    return this.tools.get(toolId);
  }

  /**
   * Get all registered tools
   */
  getAll(): ToolDefinition[] {
    return Array.from(this.tools.values());
  }

  /**
   * Check if a tool is registered
   */
  has(toolId: string): boolean {
    return this.tools.has(toolId);
  }

  /**
   * Unregister a tool
   */
  unregister(toolId: string): boolean {
    this.validators.delete(toolId);
    return this.tools.delete(toolId);
  }

  /**
   * Validate tool execution parameters
   */
  validateParameters(toolId: string, parameters?: Record<string, unknown>): {
    valid: boolean;
    errors?: string[];
  } {
    const validator = this.validators.get(toolId);
    if (!validator) {
      return { valid: true }; // No validation configured
    }

    const valid = validator(parameters || {});
    if (valid) {
      return { valid: true };
    }

    const errors = validator.errors?.map((err) => `${err.instancePath} ${err.message}`) || [];
    return { valid: false, errors };
  }

  private validateToolDefinition(tool: ToolDefinition): void {
    if (!tool.id || !tool.name || !tool.description) {
      throw new Error('Tool must have id, name, and description');
    }

    if (!tool.endpoint || !tool.endpoint.baseUrl || !tool.endpoint.path) {
      throw new Error('Tool must have valid endpoint configuration');
    }

    const validMethods = ['GET', 'POST', 'PUT', 'PATCH', 'DELETE'];
    if (!validMethods.includes(tool.endpoint.method)) {
      throw new Error(`Invalid HTTP method: ${tool.endpoint.method}`);
    }
  }

  private createValidator(tool: ToolDefinition): void {
    // Build JSON Schema from OpenAPI parameters
    const schema: Record<string, unknown> = {
      type: 'object',
      properties: {},
      required: [],
    };

    if (tool.schema.parameters) {
      for (const param of tool.schema.parameters) {
        if ('name' in param && 'schema' in param) {
          (schema.properties as Record<string, unknown>)[param.name] = param.schema;
          if (param.required) {
            (schema.required as string[]).push(param.name);
          }
        }
      }
    }

    const validator = this.ajv.compile(schema);
    this.validators.set(tool.id, validator);
  }
}
