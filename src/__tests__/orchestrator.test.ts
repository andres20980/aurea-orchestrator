import { Orchestrator } from '../config/orchestrator';
import * as fs from 'fs';

describe('Orchestrator', () => {
  const testDbPath = './test-orchestrator.db';
  let orchestrator: Orchestrator;

  beforeEach(() => {
    if (fs.existsSync(testDbPath)) {
      fs.unlinkSync(testDbPath);
    }
    orchestrator = new Orchestrator(testDbPath);
  });

  afterEach(() => {
    orchestrator.close();
    if (fs.existsSync(testDbPath)) {
      fs.unlinkSync(testDbPath);
    }
  });

  describe('saveConfig', () => {
    it('should save organization configuration', async () => {
      const config = {
        orgName: 'test-org',
        jiraConfig: {
          baseUrl: 'https://test.atlassian.net',
          email: 'test@example.com',
          apiToken: 'token',
          projectKey: 'TEST',
        },
      };

      const id = await orchestrator.saveConfig(config);
      expect(id).toBeGreaterThan(0);
    });
  });

  describe('getConfig', () => {
    it('should retrieve organization configuration', async () => {
      const config = {
        orgName: 'test-org',
        githubConfig: {
          token: 'gh-token',
          owner: 'owner',
          repo: 'repo',
        },
      };

      await orchestrator.saveConfig(config);
      const retrieved = await orchestrator.getConfig('test-org');

      expect(retrieved).toBeDefined();
      expect(retrieved?.orgName).toBe('test-org');
      expect(retrieved?.githubConfig?.token).toBe('gh-token');
    });
  });

  describe('getAllConfigs', () => {
    it('should retrieve all configurations', async () => {
      await orchestrator.saveConfig({
        orgName: 'org1',
        jiraConfig: {
          baseUrl: 'https://org1.atlassian.net',
          email: 'org1@example.com',
          apiToken: 'token1',
          projectKey: 'ORG1',
        },
      });

      await orchestrator.saveConfig({
        orgName: 'org2',
        slackConfig: {
          webhookUrl: 'https://hooks.slack.com/services/TEST',
        },
      });

      const configs = await orchestrator.getAllConfigs();
      expect(configs).toHaveLength(2);
    });
  });

  describe('deleteConfig', () => {
    it('should delete organization configuration', async () => {
      await orchestrator.saveConfig({
        orgName: 'test-org',
        jiraConfig: {
          baseUrl: 'https://test.atlassian.net',
          email: 'test@example.com',
          apiToken: 'token',
          projectKey: 'TEST',
        },
      });

      await orchestrator.deleteConfig('test-org');
      const retrieved = await orchestrator.getConfig('test-org');

      expect(retrieved).toBeNull();
    });
  });

  describe('getJiraAdapter', () => {
    it('should return a JiraToolAdapter', () => {
      const adapter = orchestrator.getJiraAdapter('test-org');
      expect(adapter).toBeDefined();
    });
  });

  describe('getGitHubAdapter', () => {
    it('should return a GitHubToolAdapter', () => {
      const adapter = orchestrator.getGitHubAdapter('test-org');
      expect(adapter).toBeDefined();
    });
  });

  describe('getSlackAdapter', () => {
    it('should return a SlackToolAdapter', () => {
      const adapter = orchestrator.getSlackAdapter('test-org');
      expect(adapter).toBeDefined();
    });
  });
});
