import { AuditLogger } from '../logger';
import { AuditLogEntry } from '../../core/types';

describe('AuditLogger', () => {
  let logger: AuditLogger;

  beforeEach(() => {
    logger = new AuditLogger();
  });

  const createMockLogEntry = (
    toolId: string,
    agentId: string,
    success: boolean = true
  ): Omit<AuditLogEntry, 'id'> => ({
    timestamp: new Date(),
    toolId,
    agentId,
    parameters: { test: 'value' },
    result: {
      success,
      data: success ? { message: 'ok' } : undefined,
      error: success ? undefined : 'Test error',
      timestamp: new Date(),
    },
    durationMs: 100,
  });

  describe('log', () => {
    it('should log an entry', () => {
      const entry = createMockLogEntry('tool-1', 'agent-1');
      logger.log(entry);
      
      const logs = logger.getAllLogs();
      expect(logs).toHaveLength(1);
      expect(logs[0]).toMatchObject(entry);
      expect(logs[0].id).toBeDefined();
    });

    it('should enforce max logs limit', () => {
      const smallLogger = new AuditLogger(3);
      
      smallLogger.log(createMockLogEntry('tool-1', 'agent-1'));
      smallLogger.log(createMockLogEntry('tool-2', 'agent-1'));
      smallLogger.log(createMockLogEntry('tool-3', 'agent-1'));
      smallLogger.log(createMockLogEntry('tool-4', 'agent-1'));
      
      const logs = smallLogger.getAllLogs();
      expect(logs).toHaveLength(3);
      expect(logs[0].toolId).toBe('tool-2');
      expect(logs[2].toolId).toBe('tool-4');
    });
  });

  describe('getLogsByAgent', () => {
    beforeEach(() => {
      logger.log(createMockLogEntry('tool-1', 'agent-1'));
      logger.log(createMockLogEntry('tool-2', 'agent-2'));
      logger.log(createMockLogEntry('tool-3', 'agent-1'));
    });

    it('should filter logs by agent', () => {
      const logs = logger.getLogsByAgent('agent-1');
      expect(logs).toHaveLength(2);
      expect(logs.every(log => log.agentId === 'agent-1')).toBe(true);
    });

    it('should return empty array for non-existent agent', () => {
      const logs = logger.getLogsByAgent('non-existent');
      expect(logs).toHaveLength(0);
    });
  });

  describe('getLogsByTool', () => {
    beforeEach(() => {
      logger.log(createMockLogEntry('tool-1', 'agent-1'));
      logger.log(createMockLogEntry('tool-1', 'agent-2'));
      logger.log(createMockLogEntry('tool-2', 'agent-1'));
    });

    it('should filter logs by tool', () => {
      const logs = logger.getLogsByTool('tool-1');
      expect(logs).toHaveLength(2);
      expect(logs.every(log => log.toolId === 'tool-1')).toBe(true);
    });
  });

  describe('getLogsByTimeRange', () => {
    it('should filter logs by time range', () => {
      const now = new Date();
      const past = new Date(now.getTime() - 60000);
      const future = new Date(now.getTime() + 60000);

      const oldEntry = { ...createMockLogEntry('tool-1', 'agent-1'), timestamp: past };
      const currentEntry = createMockLogEntry('tool-2', 'agent-1');

      logger.log(oldEntry);
      logger.log(currentEntry);

      const logs = logger.getLogsByTimeRange(
        new Date(now.getTime() - 1000),
        future
      );
      
      expect(logs).toHaveLength(1);
      expect(logs[0].toolId).toBe('tool-2');
    });
  });

  describe('getFailedExecutions', () => {
    beforeEach(() => {
      logger.log(createMockLogEntry('tool-1', 'agent-1', true));
      logger.log(createMockLogEntry('tool-2', 'agent-1', false));
      logger.log(createMockLogEntry('tool-3', 'agent-1', false));
    });

    it('should return only failed executions', () => {
      const logs = logger.getFailedExecutions();
      expect(logs).toHaveLength(2);
      expect(logs.every(log => !log.result.success)).toBe(true);
    });
  });

  describe('getStats', () => {
    beforeEach(() => {
      logger.log(createMockLogEntry('tool-1', 'agent-1', true));
      logger.log(createMockLogEntry('tool-1', 'agent-2', false));
      logger.log(createMockLogEntry('tool-2', 'agent-1', true));
    });

    it('should return correct statistics', () => {
      const stats = logger.getStats();
      
      expect(stats.totalExecutions).toBe(3);
      expect(stats.successfulExecutions).toBe(2);
      expect(stats.failedExecutions).toBe(1);
      expect(stats.averageDuration).toBe(100);
      expect(stats.toolUsage['tool-1']).toBe(2);
      expect(stats.toolUsage['tool-2']).toBe(1);
      expect(stats.agentUsage['agent-1']).toBe(2);
      expect(stats.agentUsage['agent-2']).toBe(1);
    });
  });

  describe('clear', () => {
    it('should clear all logs', () => {
      logger.log(createMockLogEntry('tool-1', 'agent-1'));
      logger.log(createMockLogEntry('tool-2', 'agent-1'));
      
      logger.clear();
      
      expect(logger.getAllLogs()).toHaveLength(0);
    });
  });
});
