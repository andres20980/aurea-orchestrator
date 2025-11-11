import { Database } from '../database';
import { OrganizationConfig } from '../types';
import * as fs from 'fs';

describe('Database', () => {
  const testDbPath = './test-aurea.db';
  let db: Database;

  beforeEach(() => {
    // Clean up test database if it exists
    if (fs.existsSync(testDbPath)) {
      fs.unlinkSync(testDbPath);
    }
    db = new Database(testDbPath);
  });

  afterEach(() => {
    db.close();
    if (fs.existsSync(testDbPath)) {
      fs.unlinkSync(testDbPath);
    }
  });

  describe('saveOrganizationConfig', () => {
    it('should save a new organization configuration', async () => {
      const config: OrganizationConfig = {
        orgName: 'test-org',
        jiraConfig: {
          baseUrl: 'https://test.atlassian.net',
          email: 'test@example.com',
          apiToken: 'test-token',
          projectKey: 'TEST',
        },
      };

      const id = await db.saveOrganizationConfig(config);
      expect(id).toBeGreaterThan(0);
    });

    it('should update existing organization configuration', async () => {
      const config: OrganizationConfig = {
        orgName: 'test-org',
        jiraConfig: {
          baseUrl: 'https://test.atlassian.net',
          email: 'test@example.com',
          apiToken: 'test-token',
          projectKey: 'TEST',
        },
      };

      await db.saveOrganizationConfig(config);
      
      const updatedConfig: OrganizationConfig = {
        orgName: 'test-org',
        githubConfig: {
          token: 'gh-token',
          owner: 'test-owner',
          repo: 'test-repo',
        },
      };

      await db.saveOrganizationConfig(updatedConfig);
      const retrieved = await db.getOrganizationConfig('test-org');

      expect(retrieved?.githubConfig).toBeDefined();
      expect(retrieved?.githubConfig?.token).toBe('gh-token');
    });
  });

  describe('getOrganizationConfig', () => {
    it('should retrieve organization configuration', async () => {
      const config: OrganizationConfig = {
        orgName: 'test-org',
        slackConfig: {
          webhookUrl: 'https://hooks.slack.com/services/TEST',
          channel: '#general',
        },
      };

      await db.saveOrganizationConfig(config);
      const retrieved = await db.getOrganizationConfig('test-org');

      expect(retrieved).toBeDefined();
      expect(retrieved?.orgName).toBe('test-org');
      expect(retrieved?.slackConfig?.webhookUrl).toBe('https://hooks.slack.com/services/TEST');
      expect(retrieved?.slackConfig?.channel).toBe('#general');
    });

    it('should return null for non-existent organization', async () => {
      const retrieved = await db.getOrganizationConfig('non-existent');
      expect(retrieved).toBeNull();
    });
  });

  describe('getAllOrganizationConfigs', () => {
    it('should retrieve all organization configurations', async () => {
      const config1: OrganizationConfig = {
        orgName: 'org1',
        jiraConfig: {
          baseUrl: 'https://org1.atlassian.net',
          email: 'org1@example.com',
          apiToken: 'token1',
          projectKey: 'ORG1',
        },
      };

      const config2: OrganizationConfig = {
        orgName: 'org2',
        githubConfig: {
          token: 'gh-token2',
          owner: 'org2',
          repo: 'repo2',
        },
      };

      await db.saveOrganizationConfig(config1);
      await db.saveOrganizationConfig(config2);

      const allConfigs = await db.getAllOrganizationConfigs();
      expect(allConfigs).toHaveLength(2);
      expect(allConfigs.map(c => c.orgName)).toContain('org1');
      expect(allConfigs.map(c => c.orgName)).toContain('org2');
    });

    it('should return empty array when no configurations exist', async () => {
      const allConfigs = await db.getAllOrganizationConfigs();
      expect(allConfigs).toEqual([]);
    });
  });

  describe('deleteOrganizationConfig', () => {
    it('should delete organization configuration', async () => {
      const config: OrganizationConfig = {
        orgName: 'test-org',
        jiraConfig: {
          baseUrl: 'https://test.atlassian.net',
          email: 'test@example.com',
          apiToken: 'test-token',
          projectKey: 'TEST',
        },
      };

      await db.saveOrganizationConfig(config);
      await db.deleteOrganizationConfig('test-org');
      
      const retrieved = await db.getOrganizationConfig('test-org');
      expect(retrieved).toBeNull();
    });
  });
});
