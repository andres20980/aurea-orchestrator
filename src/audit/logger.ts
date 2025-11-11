import { AuditLogEntry } from '../core/types';
import { randomUUID } from 'crypto';

/**
 * Manages audit logging for tool executions
 */
export class AuditLogger {
  private logs: AuditLogEntry[] = [];
  private maxLogs: number;

  constructor(maxLogs: number = 10000) {
    this.maxLogs = maxLogs;
  }

  /**
   * Log a tool execution
   */
  log(entry: Omit<AuditLogEntry, 'id'>): void {
    const logEntry: AuditLogEntry = {
      ...entry,
      id: randomUUID(),
    };

    this.logs.push(logEntry);

    // Keep only the most recent logs
    if (this.logs.length > this.maxLogs) {
      this.logs = this.logs.slice(-this.maxLogs);
    }
  }

  /**
   * Get all logs
   */
  getAllLogs(): AuditLogEntry[] {
    return [...this.logs];
  }

  /**
   * Get logs for a specific agent
   */
  getLogsByAgent(agentId: string): AuditLogEntry[] {
    return this.logs.filter((log) => log.agentId === agentId);
  }

  /**
   * Get logs for a specific tool
   */
  getLogsByTool(toolId: string): AuditLogEntry[] {
    return this.logs.filter((log) => log.toolId === toolId);
  }

  /**
   * Get logs within a time range
   */
  getLogsByTimeRange(startTime: Date, endTime: Date): AuditLogEntry[] {
    return this.logs.filter(
      (log) => log.timestamp >= startTime && log.timestamp <= endTime
    );
  }

  /**
   * Get failed executions
   */
  getFailedExecutions(): AuditLogEntry[] {
    return this.logs.filter((log) => !log.result.success);
  }

  /**
   * Clear all logs
   */
  clear(): void {
    this.logs = [];
  }

  /**
   * Get statistics about tool usage
   */
  getStats(): {
    totalExecutions: number;
    successfulExecutions: number;
    failedExecutions: number;
    averageDuration: number;
    toolUsage: Record<string, number>;
    agentUsage: Record<string, number>;
  } {
    const totalExecutions = this.logs.length;
    const successfulExecutions = this.logs.filter((log) => log.result.success).length;
    const failedExecutions = totalExecutions - successfulExecutions;

    const totalDuration = this.logs.reduce((sum, log) => sum + log.durationMs, 0);
    const averageDuration = totalExecutions > 0 ? totalDuration / totalExecutions : 0;

    const toolUsage: Record<string, number> = {};
    const agentUsage: Record<string, number> = {};

    for (const log of this.logs) {
      toolUsage[log.toolId] = (toolUsage[log.toolId] || 0) + 1;
      agentUsage[log.agentId] = (agentUsage[log.agentId] || 0) + 1;
    }

    return {
      totalExecutions,
      successfulExecutions,
      failedExecutions,
      averageDuration,
      toolUsage,
      agentUsage,
    };
  }
}
