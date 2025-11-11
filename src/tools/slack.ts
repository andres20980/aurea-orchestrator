import { ToolDefinition } from '../core/types';

/**
 * Slack Tool
 * Allows posting messages to Slack channels
 */
export const slackPostMessageTool: ToolDefinition = {
  id: 'slack-post-message',
  name: 'Slack Post Message',
  description: 'Post a message to a Slack channel',
  endpoint: {
    baseUrl: 'https://slack.com',
    path: '/api/chat.postMessage',
    method: 'POST',
  },
  schema: {
    requestBody: {
      required: true,
      content: {
        'application/json': {
          schema: {
            type: 'object',
            required: ['channel', 'text'],
            properties: {
              channel: {
                type: 'string',
                description: 'Channel ID or name (e.g., #general)',
              },
              text: {
                type: 'string',
                description: 'Message text',
              },
              blocks: {
                type: 'array',
                description: 'Structured message blocks',
                items: {
                  type: 'object',
                },
              },
              thread_ts: {
                type: 'string',
                description: 'Thread timestamp to reply to',
              },
            },
          },
        },
      },
    },
    responses: {
      '200': {
        description: 'Message posted successfully',
      },
    },
  },
  auth: {
    type: 'bearer',
    envVar: 'SLACK_BOT_TOKEN',
  },
  headers: {
    'Content-Type': 'application/json',
  },
};

export const slackListChannelsTool: ToolDefinition = {
  id: 'slack-list-channels',
  name: 'Slack List Channels',
  description: 'List all channels in a Slack workspace',
  endpoint: {
    baseUrl: 'https://slack.com',
    path: '/api/conversations.list',
    method: 'GET',
  },
  schema: {
    parameters: [
      {
        name: 'types',
        in: 'query',
        required: false,
        schema: {
          type: 'string',
          description: 'Channel types to include (public_channel, private_channel)',
          default: 'public_channel',
        },
        description: 'Types of channels to list',
      },
      {
        name: 'limit',
        in: 'query',
        required: false,
        schema: {
          type: 'integer',
          description: 'Maximum number of channels to return',
          default: 100,
        },
        description: 'Limit results',
      },
    ],
    responses: {
      '200': {
        description: 'List of channels',
      },
    },
  },
  auth: {
    type: 'bearer',
    envVar: 'SLACK_BOT_TOKEN',
  },
  headers: {
    'Content-Type': 'application/json',
  },
};
