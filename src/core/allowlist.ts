import { AllowlistConfig } from './types';

/**
 * Manages agent access control via allowlists
 */
export class Allowlist {
  private allowlists: Map<string, AllowlistConfig> = new Map();
  private rateLimitTracking: Map<string, { count: number; resetAt: number }> = new Map();

  /**
   * Add or update allowlist configuration for an agent
   */
  configure(config: AllowlistConfig): void {
    this.allowlists.set(config.agentId, config);
  }

  /**
   * Check if an agent is allowed to use a specific tool
   */
  isAllowed(agentId: string, toolId: string): boolean {
    const config = this.allowlists.get(agentId);
    if (!config) {
      return false; // No allowlist means no access
    }

    return config.allowedTools.includes(toolId);
  }

  /**
   * Check rate limit for an agent
   */
  checkRateLimit(agentId: string): { allowed: boolean; reason?: string } {
    const config = this.allowlists.get(agentId);
    if (!config || !config.rateLimit) {
      return { allowed: true }; // No rate limit configured
    }

    const key = `${agentId}`;
    const now = Date.now();
    const tracking = this.rateLimitTracking.get(key);

    // Initialize or reset if window expired
    if (!tracking || now > tracking.resetAt) {
      this.rateLimitTracking.set(key, {
        count: 1,
        resetAt: now + config.rateLimit.windowMs,
      });
      return { allowed: true };
    }

    // Check if limit exceeded
    if (tracking.count >= config.rateLimit.maxRequests) {
      const resetIn = Math.ceil((tracking.resetAt - now) / 1000);
      return {
        allowed: false,
        reason: `Rate limit exceeded. Resets in ${resetIn} seconds`,
      };
    }

    // Increment count
    tracking.count++;
    return { allowed: true };
  }

  /**
   * Get allowlist configuration for an agent
   */
  getConfig(agentId: string): AllowlistConfig | undefined {
    return this.allowlists.get(agentId);
  }

  /**
   * Remove allowlist for an agent
   */
  remove(agentId: string): boolean {
    this.rateLimitTracking.delete(agentId);
    return this.allowlists.delete(agentId);
  }

  /**
   * Get all agent IDs with allowlists
   */
  getAgentIds(): string[] {
    return Array.from(this.allowlists.keys());
  }
}
