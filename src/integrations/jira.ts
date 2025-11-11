import axios from 'axios';
import { JiraConfig, JiraIssue, IntegrationResponse } from '../types';

export class JiraIntegration {
  private config: JiraConfig;

  constructor(config: JiraConfig) {
    this.config = config;
  }

  /**
   * Create a new Jira issue
   */
  async createIssue(issue: JiraIssue): Promise<IntegrationResponse> {
    try {
      const auth = Buffer.from(`${this.config.email}:${this.config.apiToken}`).toString('base64');
      
      const response = await axios.post(
        `${this.config.baseUrl}/rest/api/3/issue`,
        {
          fields: {
            project: {
              key: this.config.projectKey,
            },
            summary: issue.summary,
            description: {
              type: 'doc',
              version: 1,
              content: [
                {
                  type: 'paragraph',
                  content: [
                    {
                      type: 'text',
                      text: issue.description,
                    },
                  ],
                },
              ],
            },
            issuetype: {
              name: issue.issueType,
            },
            ...(issue.priority && {
              priority: {
                name: issue.priority,
              },
            }),
            ...(issue.assignee && {
              assignee: {
                accountId: issue.assignee,
              },
            }),
          },
        },
        {
          headers: {
            Authorization: `Basic ${auth}`,
            'Content-Type': 'application/json',
          },
        }
      );

      return {
        success: true,
        data: {
          key: response.data.key,
          id: response.data.id,
          self: response.data.self,
        },
      };
    } catch (error: any) {
      return {
        success: false,
        error: error.response?.data?.errorMessages?.join(', ') || error.message,
      };
    }
  }

  /**
   * Get issue details
   */
  async getIssue(issueKey: string): Promise<IntegrationResponse> {
    try {
      const auth = Buffer.from(`${this.config.email}:${this.config.apiToken}`).toString('base64');
      
      const response = await axios.get(
        `${this.config.baseUrl}/rest/api/3/issue/${issueKey}`,
        {
          headers: {
            Authorization: `Basic ${auth}`,
            'Content-Type': 'application/json',
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
        error: error.response?.data?.errorMessages?.join(', ') || error.message,
      };
    }
  }
}
