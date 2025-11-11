import { Database } from '../database';
import { JiraToolAdapter, GitHubToolAdapter, SlackToolAdapter } from '../adapters';
import { OrganizationConfig } from '../types';
import * as fs from 'fs';

// Mock integrations
jest.mock('../integrations/jira');
jest.mock('../integrations/github');
jest.mock('../integrations/slack');

import { JiraIntegration } from '../integrations/jira';
import { GitHubIntegration } from '../integrations/github';
import { SlackIntegration } from '../integrations/slack';

const MockedJiraIntegration = JiraIntegration as jest.MockedClass<typeof JiraIntegration>;
const MockedGitHubIntegration = GitHubIntegration as jest.MockedClass<typeof GitHubIntegration>;
const MockedSlackIntegration = SlackIntegration as jest.MockedClass<typeof SlackIntegration>;

describe('Tool Adapters', () => {
  const testDbPath = './test-adapters.db';
  let db: Database;

  beforeEach(() => {
    if (fs.existsSync(testDbPath)) {
      fs.unlinkSync(testDbPath);
    }
    db = new Database(testDbPath);
    jest.clearAllMocks();
  });

  afterEach(() => {
    db.close();
    if (fs.existsSync(testDbPath)) {
      fs.unlinkSync(testDbPath);
    }
  });

  describe('JiraToolAdapter', () => {
    it('should execute createIssue action', async () => {
      const config: OrganizationConfig = {
        orgName: 'test-org',
        jiraConfig: {
          baseUrl: 'https://test.atlassian.net',
          email: 'test@example.com',
          apiToken: 'token',
          projectKey: 'TEST',
        },
      };

      await db.saveOrganizationConfig(config);

      const mockCreateIssue = jest.fn().mockResolvedValue({
        success: true,
        data: { key: 'TEST-123' },
      });

      MockedJiraIntegration.mockImplementation(() => ({
        createIssue: mockCreateIssue,
        getIssue: jest.fn(),
      } as any));

      const adapter = new JiraToolAdapter(db, 'test-org');
      const result = await adapter.execute('createIssue', {
        summary: 'Test Issue',
        description: 'Test Description',
        issueType: 'Task',
      });

      expect(result.success).toBe(true);
      expect(result.data?.key).toBe('TEST-123');
      expect(mockCreateIssue).toHaveBeenCalled();
    });

    it('should return error when config not found', async () => {
      const adapter = new JiraToolAdapter(db, 'non-existent');
      const result = await adapter.execute('createIssue', {});

      expect(result.success).toBe(false);
      expect(result.error).toContain('Jira configuration not found');
    });

    it('should return error for unknown action', async () => {
      const config: OrganizationConfig = {
        orgName: 'test-org',
        jiraConfig: {
          baseUrl: 'https://test.atlassian.net',
          email: 'test@example.com',
          apiToken: 'token',
          projectKey: 'TEST',
        },
      };

      await db.saveOrganizationConfig(config);

      const adapter = new JiraToolAdapter(db, 'test-org');
      const result = await adapter.execute('unknownAction', {});

      expect(result.success).toBe(false);
      expect(result.error).toContain('Unknown action');
    });
  });

  describe('GitHubToolAdapter', () => {
    it('should execute createPullRequest action', async () => {
      const config: OrganizationConfig = {
        orgName: 'test-org',
        githubConfig: {
          token: 'gh-token',
          owner: 'test-owner',
          repo: 'test-repo',
        },
      };

      await db.saveOrganizationConfig(config);

      const mockCreatePR = jest.fn().mockResolvedValue({
        success: true,
        data: { number: 123, url: 'https://github.com/test/repo/pull/123' },
      });

      MockedGitHubIntegration.mockImplementation(() => ({
        createPullRequest: mockCreatePR,
        createIssue: jest.fn(),
        getPullRequest: jest.fn(),
      } as any));

      const adapter = new GitHubToolAdapter(db, 'test-org');
      const result = await adapter.execute('createPullRequest', {
        title: 'Test PR',
        body: 'Test Body',
        head: 'feature',
        base: 'main',
      });

      expect(result.success).toBe(true);
      expect(result.data?.number).toBe(123);
      expect(mockCreatePR).toHaveBeenCalled();
    });

    it('should execute createIssue action', async () => {
      const config: OrganizationConfig = {
        orgName: 'test-org',
        githubConfig: {
          token: 'gh-token',
          owner: 'test-owner',
          repo: 'test-repo',
        },
      };

      await db.saveOrganizationConfig(config);

      const mockCreateIssue = jest.fn().mockResolvedValue({
        success: true,
        data: { number: 456 },
      });

      MockedGitHubIntegration.mockImplementation(() => ({
        createPullRequest: jest.fn(),
        createIssue: mockCreateIssue,
        getPullRequest: jest.fn(),
      } as any));

      const adapter = new GitHubToolAdapter(db, 'test-org');
      const result = await adapter.execute('createIssue', {
        title: 'Bug',
        body: 'Found a bug',
        labels: ['bug'],
      });

      expect(result.success).toBe(true);
      expect(mockCreateIssue).toHaveBeenCalledWith('Bug', 'Found a bug', ['bug']);
    });

    it('should return error when config not found', async () => {
      const adapter = new GitHubToolAdapter(db, 'non-existent');
      const result = await adapter.execute('createPullRequest', {});

      expect(result.success).toBe(false);
      expect(result.error).toContain('GitHub configuration not found');
    });
  });

  describe('SlackToolAdapter', () => {
    it('should execute sendMessage action', async () => {
      const config: OrganizationConfig = {
        orgName: 'test-org',
        slackConfig: {
          webhookUrl: 'https://hooks.slack.com/services/TEST',
          channel: '#general',
        },
      };

      await db.saveOrganizationConfig(config);

      const mockSendMessage = jest.fn().mockResolvedValue({
        success: true,
        data: { message: 'Sent' },
      });

      MockedSlackIntegration.mockImplementation(() => ({
        sendMessage: mockSendMessage,
        sendSimpleMessage: jest.fn(),
        sendNotification: jest.fn(),
      } as any));

      const adapter = new SlackToolAdapter(db, 'test-org');
      const result = await adapter.execute('sendMessage', {
        text: 'Hello!',
      });

      expect(result.success).toBe(true);
      expect(mockSendMessage).toHaveBeenCalled();
    });

    it('should execute sendSimpleMessage action', async () => {
      const config: OrganizationConfig = {
        orgName: 'test-org',
        slackConfig: {
          webhookUrl: 'https://hooks.slack.com/services/TEST',
        },
      };

      await db.saveOrganizationConfig(config);

      const mockSendSimple = jest.fn().mockResolvedValue({
        success: true,
        data: { message: 'Sent' },
      });

      MockedSlackIntegration.mockImplementation(() => ({
        sendMessage: jest.fn(),
        sendSimpleMessage: mockSendSimple,
        sendNotification: jest.fn(),
      } as any));

      const adapter = new SlackToolAdapter(db, 'test-org');
      const result = await adapter.execute('sendSimpleMessage', {
        text: 'Quick message',
        channel: '#alerts',
      });

      expect(result.success).toBe(true);
      expect(mockSendSimple).toHaveBeenCalledWith('Quick message', '#alerts');
    });

    it('should return error when config not found', async () => {
      const adapter = new SlackToolAdapter(db, 'non-existent');
      const result = await adapter.execute('sendMessage', {});

      expect(result.success).toBe(false);
      expect(result.error).toContain('Slack configuration not found');
    });
  });
});
