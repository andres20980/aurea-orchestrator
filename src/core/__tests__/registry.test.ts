import { ToolRegistry } from '../registry';
import { ToolDefinition } from '../types';

describe('ToolRegistry', () => {
  let registry: ToolRegistry;

  beforeEach(() => {
    registry = new ToolRegistry();
  });

  const mockTool: ToolDefinition = {
    id: 'test-tool',
    name: 'Test Tool',
    description: 'A test tool',
    endpoint: {
      baseUrl: 'https://api.example.com',
      path: '/test',
      method: 'GET',
    },
    schema: {
      parameters: [
        {
          name: 'param1',
          in: 'query',
          required: true,
          schema: { type: 'string' },
          description: 'Test parameter',
        },
      ],
    },
  };

  describe('register', () => {
    it('should register a valid tool', () => {
      expect(() => registry.register(mockTool)).not.toThrow();
      expect(registry.has('test-tool')).toBe(true);
    });

    it('should throw error when registering duplicate tool', () => {
      registry.register(mockTool);
      expect(() => registry.register(mockTool)).toThrow(
        "Tool with id 'test-tool' is already registered"
      );
    });

    it('should throw error for tool without id', () => {
      const invalidTool = { ...mockTool, id: '' };
      expect(() => registry.register(invalidTool as ToolDefinition)).toThrow(
        'Tool must have id, name, and description'
      );
    });

    it('should throw error for tool with invalid HTTP method', () => {
      const invalidTool = {
        ...mockTool,
        endpoint: { ...mockTool.endpoint, method: 'INVALID' as unknown as 'GET' },
      };
      expect(() => registry.register(invalidTool)).toThrow('Invalid HTTP method');
    });
  });

  describe('get', () => {
    it('should return registered tool', () => {
      registry.register(mockTool);
      const tool = registry.get('test-tool');
      expect(tool).toEqual(mockTool);
    });

    it('should return undefined for non-existent tool', () => {
      const tool = registry.get('non-existent');
      expect(tool).toBeUndefined();
    });
  });

  describe('getAll', () => {
    it('should return all registered tools', () => {
      const tool2: ToolDefinition = { ...mockTool, id: 'test-tool-2', name: 'Test Tool 2' };
      registry.register(mockTool);
      registry.register(tool2);
      
      const tools = registry.getAll();
      expect(tools).toHaveLength(2);
      expect(tools).toContainEqual(mockTool);
      expect(tools).toContainEqual(tool2);
    });

    it('should return empty array when no tools registered', () => {
      expect(registry.getAll()).toEqual([]);
    });
  });

  describe('unregister', () => {
    it('should unregister a tool', () => {
      registry.register(mockTool);
      const result = registry.unregister('test-tool');
      
      expect(result).toBe(true);
      expect(registry.has('test-tool')).toBe(false);
    });

    it('should return false when unregistering non-existent tool', () => {
      const result = registry.unregister('non-existent');
      expect(result).toBe(false);
    });
  });

  describe('validateParameters', () => {
    it('should validate correct parameters', () => {
      registry.register(mockTool);
      const result = registry.validateParameters('test-tool', { param1: 'value' });
      
      expect(result.valid).toBe(true);
      expect(result.errors).toBeUndefined();
    });

    it('should reject missing required parameters', () => {
      registry.register(mockTool);
      const result = registry.validateParameters('test-tool', {});
      
      expect(result.valid).toBe(false);
      expect(result.errors).toBeDefined();
    });

    it('should return valid for tool without validation', () => {
      const toolNoValidation: ToolDefinition = {
        ...mockTool,
        id: 'no-validation',
        schema: {},
      };
      registry.register(toolNoValidation);
      const result = registry.validateParameters('no-validation', {});
      
      expect(result.valid).toBe(true);
    });
  });
});
