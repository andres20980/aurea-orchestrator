import axios from 'axios';
import { GitHubConfig, GitHubPullRequest, IntegrationResponse } from '../types';

export class GitHubIntegration {
  private config: GitHubConfig;

  constructor(config: GitHubConfig) {
    this.config = config;
  }

  /**
   * Create a new pull request
   */
  async createPullRequest(pr: GitHubPullRequest): Promise<IntegrationResponse> {
    try {
      const response = await axios.post(
        `https://api.github.com/repos/${this.config.owner}/${this.config.repo}/pulls`,
        {
          title: pr.title,
          body: pr.body,
          head: pr.head,
          base: pr.base,
          draft: pr.draft || false,
        },
        {
          headers: {
            Authorization: `Bearer ${this.config.token}`,
            'Content-Type': 'application/json',
            Accept: 'application/vnd.github.v3+json',
          },
        }
      );

      return {
        success: true,
        data: {
          number: response.data.number,
          url: response.data.html_url,
          state: response.data.state,
        },
      };
    } catch (error: any) {
      return {
        success: false,
        error: error.response?.data?.message || error.message,
      };
    }
  }

  /**
   * Create an issue
   */
  async createIssue(title: string, body: string, labels?: string[]): Promise<IntegrationResponse> {
    try {
      const response = await axios.post(
        `https://api.github.com/repos/${this.config.owner}/${this.config.repo}/issues`,
        {
          title,
          body,
          labels: labels || [],
        },
        {
          headers: {
            Authorization: `Bearer ${this.config.token}`,
            'Content-Type': 'application/json',
            Accept: 'application/vnd.github.v3+json',
          },
        }
      );

      return {
        success: true,
        data: {
          number: response.data.number,
          url: response.data.html_url,
          state: response.data.state,
        },
      };
    } catch (error: any) {
      return {
        success: false,
        error: error.response?.data?.message || error.message,
      };
    }
  }

  /**
   * Get pull request details
   */
  async getPullRequest(prNumber: number): Promise<IntegrationResponse> {
    try {
      const response = await axios.get(
        `https://api.github.com/repos/${this.config.owner}/${this.config.repo}/pulls/${prNumber}`,
        {
          headers: {
            Authorization: `Bearer ${this.config.token}`,
            Accept: 'application/vnd.github.v3+json',
          },
        }
      );

      return {
        success: true,
        data: response.data,
      };
    } catch (error: any) {
      return {
        success: false,
        error: error.response?.data?.message || error.message,
      };
    }
  }
}
