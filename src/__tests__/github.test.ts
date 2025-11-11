import { GitHubIntegration } from '../integrations/github';
import { GitHubConfig, GitHubPullRequest } from '../types';

// Mock axios
jest.mock('axios');
import axios from 'axios';
const mockedAxios = axios as jest.Mocked<typeof axios>;

describe('GitHubIntegration', () => {
  const config: GitHubConfig = {
    token: 'gh-test-token',
    owner: 'test-owner',
    repo: 'test-repo',
  };

  let github: GitHubIntegration;

  beforeEach(() => {
    github = new GitHubIntegration(config);
    jest.clearAllMocks();
  });

  describe('createPullRequest', () => {
    it('should create a pull request successfully', async () => {
      const pr: GitHubPullRequest = {
        title: 'Test PR',
        body: 'This is a test pull request',
        head: 'feature-branch',
        base: 'main',
      };

      const mockResponse = {
        data: {
          number: 123,
          html_url: 'https://github.com/test-owner/test-repo/pull/123',
          state: 'open',
        },
      };

      mockedAxios.post.mockResolvedValue(mockResponse);

      const result = await github.createPullRequest(pr);

      expect(result.success).toBe(true);
      expect(result.data?.number).toBe(123);
      expect(result.data?.url).toBe('https://github.com/test-owner/test-repo/pull/123');
      expect(mockedAxios.post).toHaveBeenCalledWith(
        'https://api.github.com/repos/test-owner/test-repo/pulls',
        expect.objectContaining({
          title: 'Test PR',
          head: 'feature-branch',
          base: 'main',
        }),
        expect.objectContaining({
          headers: expect.objectContaining({
            Authorization: 'Bearer gh-test-token',
          }),
        })
      );
    });

    it('should create a draft pull request', async () => {
      const pr: GitHubPullRequest = {
        title: 'Draft PR',
        body: 'This is a draft',
        head: 'feature',
        base: 'main',
        draft: true,
      };

      const mockResponse = {
        data: {
          number: 124,
          html_url: 'https://github.com/test-owner/test-repo/pull/124',
          state: 'open',
        },
      };

      mockedAxios.post.mockResolvedValue(mockResponse);

      await github.createPullRequest(pr);

      expect(mockedAxios.post).toHaveBeenCalledWith(
        expect.any(String),
        expect.objectContaining({
          draft: true,
        }),
        expect.any(Object)
      );
    });

    it('should handle errors when creating PR', async () => {
      const pr: GitHubPullRequest = {
        title: 'Test PR',
        body: 'Test',
        head: 'feature',
        base: 'main',
      };

      mockedAxios.post.mockRejectedValue({
        response: {
          data: {
            message: 'Validation Failed',
          },
        },
      });

      const result = await github.createPullRequest(pr);

      expect(result.success).toBe(false);
      expect(result.error).toContain('Validation Failed');
    });
  });

  describe('createIssue', () => {
    it('should create an issue successfully', async () => {
      const mockResponse = {
        data: {
          number: 456,
          html_url: 'https://github.com/test-owner/test-repo/issues/456',
          state: 'open',
        },
      };

      mockedAxios.post.mockResolvedValue(mockResponse);

      const result = await github.createIssue('Bug Report', 'Found a bug', ['bug', 'priority']);

      expect(result.success).toBe(true);
      expect(result.data?.number).toBe(456);
      expect(mockedAxios.post).toHaveBeenCalledWith(
        'https://api.github.com/repos/test-owner/test-repo/issues',
        expect.objectContaining({
          title: 'Bug Report',
          body: 'Found a bug',
          labels: ['bug', 'priority'],
        }),
        expect.any(Object)
      );
    });

    it('should create issue without labels', async () => {
      const mockResponse = {
        data: {
          number: 457,
          html_url: 'https://github.com/test-owner/test-repo/issues/457',
          state: 'open',
        },
      };

      mockedAxios.post.mockResolvedValue(mockResponse);

      await github.createIssue('Feature Request', 'Add new feature');

      expect(mockedAxios.post).toHaveBeenCalledWith(
        expect.any(String),
        expect.objectContaining({
          labels: [],
        }),
        expect.any(Object)
      );
    });
  });

  describe('getPullRequest', () => {
    it('should retrieve pull request details successfully', async () => {
      const mockResponse = {
        data: {
          number: 123,
          title: 'Test PR',
          state: 'open',
          html_url: 'https://github.com/test-owner/test-repo/pull/123',
        },
      };

      mockedAxios.get.mockResolvedValue(mockResponse);

      const result = await github.getPullRequest(123);

      expect(result.success).toBe(true);
      expect(result.data?.number).toBe(123);
      expect(mockedAxios.get).toHaveBeenCalledWith(
        'https://api.github.com/repos/test-owner/test-repo/pulls/123',
        expect.any(Object)
      );
    });

    it('should handle errors when retrieving PR', async () => {
      mockedAxios.get.mockRejectedValue({
        response: {
          data: {
            message: 'Not Found',
          },
        },
      });

      const result = await github.getPullRequest(999);

      expect(result.success).toBe(false);
      expect(result.error).toContain('Not Found');
    });
  });
});
