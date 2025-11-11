import { ToolDefinition } from '../core/types';

/**
 * Jira Tool
 * Allows creating and searching issues in Jira
 */
export const jiraCreateIssueTool: ToolDefinition = {
  id: 'jira-create-issue',
  name: 'Jira Create Issue',
  description: 'Create a new issue in Jira',
  endpoint: {
    baseUrl: 'https://your-domain.atlassian.net',
    path: '/rest/api/3/issue',
    method: 'POST',
  },
  schema: {
    requestBody: {
      required: true,
      content: {
        'application/json': {
          schema: {
            type: 'object',
            required: ['fields'],
            properties: {
              fields: {
                type: 'object',
                required: ['project', 'summary', 'issuetype'],
                properties: {
                  project: {
                    type: 'object',
                    properties: {
                      key: {
                        type: 'string',
                        description: 'Project key',
                      },
                    },
                  },
                  summary: {
                    type: 'string',
                    description: 'Issue summary',
                  },
                  description: {
                    type: 'object',
                    description: 'Issue description in Atlassian Document Format',
                  },
                  issuetype: {
                    type: 'object',
                    properties: {
                      name: {
                        type: 'string',
                        description: 'Issue type (e.g., Bug, Task, Story)',
                      },
                    },
                  },
                },
              },
            },
          },
        },
      },
    },
    responses: {
      '201': {
        description: 'Issue created successfully',
      },
    },
  },
  auth: {
    type: 'basic',
    envVar: 'JIRA_API_TOKEN',
  },
  headers: {
    'Content-Type': 'application/json',
  },
};

export const jiraSearchIssuesTool: ToolDefinition = {
  id: 'jira-search-issues',
  name: 'Jira Search Issues',
  description: 'Search for issues in Jira using JQL',
  endpoint: {
    baseUrl: 'https://your-domain.atlassian.net',
    path: '/rest/api/3/search',
    method: 'GET',
  },
  schema: {
    parameters: [
      {
        name: 'jql',
        in: 'query',
        required: true,
        schema: {
          type: 'string',
          description: 'JQL query string',
        },
        description: 'JQL query to search issues',
      },
      {
        name: 'maxResults',
        in: 'query',
        required: false,
        schema: {
          type: 'integer',
          description: 'Maximum number of results to return',
          default: 50,
        },
        description: 'Maximum results',
      },
    ],
    responses: {
      '200': {
        description: 'Search results',
      },
    },
  },
  auth: {
    type: 'basic',
    envVar: 'JIRA_API_TOKEN',
  },
  headers: {
    'Content-Type': 'application/json',
  },
};
