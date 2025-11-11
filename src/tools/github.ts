import { ToolDefinition } from '../core/types';

/**
 * GitHub Issues Tool
 * Allows creating and listing issues in a GitHub repository
 */
export const githubIssuesCreateTool: ToolDefinition = {
  id: 'github-create-issue',
  name: 'GitHub Create Issue',
  description: 'Create a new issue in a GitHub repository',
  endpoint: {
    baseUrl: 'https://api.github.com',
    path: '/repos/{owner}/{repo}/issues',
    method: 'POST',
  },
  schema: {
    parameters: [
      {
        name: 'owner',
        in: 'path',
        required: true,
        schema: {
          type: 'string',
          description: 'Repository owner (username or organization)',
        },
        description: 'Repository owner',
      },
      {
        name: 'repo',
        in: 'path',
        required: true,
        schema: {
          type: 'string',
          description: 'Repository name',
        },
        description: 'Repository name',
      },
    ],
    requestBody: {
      required: true,
      content: {
        'application/json': {
          schema: {
            type: 'object',
            required: ['title'],
            properties: {
              title: {
                type: 'string',
                description: 'The title of the issue',
              },
              body: {
                type: 'string',
                description: 'The contents of the issue',
              },
              labels: {
                type: 'array',
                items: { type: 'string' },
                description: 'Labels to associate with this issue',
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
    type: 'bearer',
    envVar: 'GITHUB_TOKEN',
  },
  headers: {
    'Accept': 'application/vnd.github.v3+json',
  },
};

export const githubIssuesListTool: ToolDefinition = {
  id: 'github-list-issues',
  name: 'GitHub List Issues',
  description: 'List issues in a GitHub repository',
  endpoint: {
    baseUrl: 'https://api.github.com',
    path: '/repos/{owner}/{repo}/issues',
    method: 'GET',
  },
  schema: {
    parameters: [
      {
        name: 'owner',
        in: 'path',
        required: true,
        schema: {
          type: 'string',
          description: 'Repository owner',
        },
        description: 'Repository owner',
      },
      {
        name: 'repo',
        in: 'path',
        required: true,
        schema: {
          type: 'string',
          description: 'Repository name',
        },
        description: 'Repository name',
      },
      {
        name: 'state',
        in: 'query',
        required: false,
        schema: {
          type: 'string',
          enum: ['open', 'closed', 'all'],
          description: 'State of issues to return',
        },
        description: 'Filter by state',
      },
    ],
    responses: {
      '200': {
        description: 'List of issues',
      },
    },
  },
  auth: {
    type: 'bearer',
    envVar: 'GITHUB_TOKEN',
  },
  headers: {
    'Accept': 'application/vnd.github.v3+json',
  },
};
