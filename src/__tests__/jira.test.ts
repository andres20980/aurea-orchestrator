import { JiraIntegration } from '../integrations/jira';
import { JiraConfig, JiraIssue } from '../types';

// Mock axios
jest.mock('axios');
import axios from 'axios';
const mockedAxios = axios as jest.Mocked<typeof axios>;

describe('JiraIntegration', () => {
  const config: JiraConfig = {
    baseUrl: 'https://test.atlassian.net',
    email: 'test@example.com',
    apiToken: 'test-token',
    projectKey: 'TEST',
  };

  let jira: JiraIntegration;

  beforeEach(() => {
    jira = new JiraIntegration(config);
    jest.clearAllMocks();
  });

  describe('createIssue', () => {
    it('should create a Jira issue successfully', async () => {
      const issue: JiraIssue = {
        summary: 'Test Issue',
        description: 'This is a test issue',
        issueType: 'Task',
      };

      const mockResponse = {
        data: {
          key: 'TEST-123',
          id: '10001',
          self: 'https://test.atlassian.net/rest/api/3/issue/10001',
        },
      };

      mockedAxios.post.mockResolvedValue(mockResponse);

      const result = await jira.createIssue(issue);

      expect(result.success).toBe(true);
      expect(result.data?.key).toBe('TEST-123');
      expect(mockedAxios.post).toHaveBeenCalledWith(
        'https://test.atlassian.net/rest/api/3/issue',
        expect.objectContaining({
          fields: expect.objectContaining({
            summary: 'Test Issue',
            project: { key: 'TEST' },
          }),
        }),
        expect.objectContaining({
          headers: expect.objectContaining({
            'Content-Type': 'application/json',
          }),
        })
      );
    });

    it('should handle errors when creating issue', async () => {
      const issue: JiraIssue = {
        summary: 'Test Issue',
        description: 'This is a test issue',
        issueType: 'Task',
      };

      mockedAxios.post.mockRejectedValue({
        response: {
          data: {
            errorMessages: ['Project does not exist'],
          },
        },
      });

      const result = await jira.createIssue(issue);

      expect(result.success).toBe(false);
      expect(result.error).toContain('Project does not exist');
    });

    it('should include optional fields when provided', async () => {
      const issue: JiraIssue = {
        summary: 'Test Issue',
        description: 'This is a test issue',
        issueType: 'Bug',
        priority: 'High',
        assignee: 'user123',
      };

      const mockResponse = {
        data: {
          key: 'TEST-124',
          id: '10002',
          self: 'https://test.atlassian.net/rest/api/3/issue/10002',
        },
      };

      mockedAxios.post.mockResolvedValue(mockResponse);

      await jira.createIssue(issue);

      expect(mockedAxios.post).toHaveBeenCalledWith(
        expect.any(String),
        expect.objectContaining({
          fields: expect.objectContaining({
            priority: { name: 'High' },
            assignee: { accountId: 'user123' },
          }),
        }),
        expect.any(Object)
      );
    });
  });

  describe('getIssue', () => {
    it('should retrieve issue details successfully', async () => {
      const mockResponse = {
        data: {
          key: 'TEST-123',
          fields: {
            summary: 'Test Issue',
            status: { name: 'Open' },
          },
        },
      };

      mockedAxios.get.mockResolvedValue(mockResponse);

      const result = await jira.getIssue('TEST-123');

      expect(result.success).toBe(true);
      expect(result.data?.key).toBe('TEST-123');
      expect(mockedAxios.get).toHaveBeenCalledWith(
        'https://test.atlassian.net/rest/api/3/issue/TEST-123',
        expect.any(Object)
      );
    });

    it('should handle errors when retrieving issue', async () => {
      mockedAxios.get.mockRejectedValue({
        response: {
          data: {
            errorMessages: ['Issue does not exist'],
          },
        },
      });

      const result = await jira.getIssue('TEST-999');

      expect(result.success).toBe(false);
      expect(result.error).toContain('Issue does not exist');
    });
  });
});
