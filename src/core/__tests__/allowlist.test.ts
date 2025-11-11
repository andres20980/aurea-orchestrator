import { Allowlist } from '../allowlist';
import { AllowlistConfig } from '../types';

describe('Allowlist', () => {
  let allowlist: Allowlist;

  beforeEach(() => {
    allowlist = new Allowlist();
  });

  const mockConfig: AllowlistConfig = {
    agentId: 'agent-1',
    allowedTools: ['tool-1', 'tool-2'],
  };

  describe('configure', () => {
    it('should configure allowlist for an agent', () => {
      allowlist.configure(mockConfig);
      const config = allowlist.getConfig('agent-1');
      expect(config).toEqual(mockConfig);
    });

    it('should update existing configuration', () => {
      allowlist.configure(mockConfig);
      const updatedConfig: AllowlistConfig = {
        agentId: 'agent-1',
        allowedTools: ['tool-1', 'tool-2', 'tool-3'],
      };
      allowlist.configure(updatedConfig);
      
      const config = allowlist.getConfig('agent-1');
      expect(config?.allowedTools).toHaveLength(3);
    });
  });

  describe('isAllowed', () => {
    beforeEach(() => {
      allowlist.configure(mockConfig);
    });

    it('should allow access to tools in allowlist', () => {
      expect(allowlist.isAllowed('agent-1', 'tool-1')).toBe(true);
      expect(allowlist.isAllowed('agent-1', 'tool-2')).toBe(true);
    });

    it('should deny access to tools not in allowlist', () => {
      expect(allowlist.isAllowed('agent-1', 'tool-3')).toBe(false);
    });

    it('should deny access for unconfigured agents', () => {
      expect(allowlist.isAllowed('agent-2', 'tool-1')).toBe(false);
    });
  });

  describe('checkRateLimit', () => {
    it('should allow requests when no rate limit configured', () => {
      allowlist.configure(mockConfig);
      const result = allowlist.checkRateLimit('agent-1');
      expect(result.allowed).toBe(true);
    });

    it('should allow requests within rate limit', () => {
      const configWithRateLimit: AllowlistConfig = {
        ...mockConfig,
        rateLimit: {
          maxRequests: 3,
          windowMs: 60000,
        },
      };
      allowlist.configure(configWithRateLimit);

      expect(allowlist.checkRateLimit('agent-1').allowed).toBe(true);
      expect(allowlist.checkRateLimit('agent-1').allowed).toBe(true);
      expect(allowlist.checkRateLimit('agent-1').allowed).toBe(true);
    });

    it('should deny requests exceeding rate limit', () => {
      const configWithRateLimit: AllowlistConfig = {
        ...mockConfig,
        rateLimit: {
          maxRequests: 2,
          windowMs: 60000,
        },
      };
      allowlist.configure(configWithRateLimit);

      allowlist.checkRateLimit('agent-1');
      allowlist.checkRateLimit('agent-1');
      const result = allowlist.checkRateLimit('agent-1');
      
      expect(result.allowed).toBe(false);
      expect(result.reason).toContain('Rate limit exceeded');
    });

    it('should reset rate limit after window expires', async () => {
      const configWithRateLimit: AllowlistConfig = {
        ...mockConfig,
        rateLimit: {
          maxRequests: 2,
          windowMs: 100, // 100ms window
        },
      };
      allowlist.configure(configWithRateLimit);

      allowlist.checkRateLimit('agent-1');
      allowlist.checkRateLimit('agent-1');

      // Wait for window to expire
      await new Promise(resolve => setTimeout(resolve, 150));

      const result = allowlist.checkRateLimit('agent-1');
      expect(result.allowed).toBe(true);
    });
  });

  describe('remove', () => {
    it('should remove allowlist configuration', () => {
      allowlist.configure(mockConfig);
      const result = allowlist.remove('agent-1');
      
      expect(result).toBe(true);
      expect(allowlist.getConfig('agent-1')).toBeUndefined();
    });

    it('should return false when removing non-existent agent', () => {
      const result = allowlist.remove('non-existent');
      expect(result).toBe(false);
    });
  });

  describe('getAgentIds', () => {
    it('should return all configured agent IDs', () => {
      allowlist.configure(mockConfig);
      allowlist.configure({ agentId: 'agent-2', allowedTools: ['tool-1'] });
      
      const agentIds = allowlist.getAgentIds();
      expect(agentIds).toHaveLength(2);
      expect(agentIds).toContain('agent-1');
      expect(agentIds).toContain('agent-2');
    });
  });
});
