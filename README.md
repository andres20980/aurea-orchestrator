# Aurea Orchestrator

Automated Unified Reasoning & Execution Agents

## Overview

Aurea Orchestrator is a flexible integration framework that allows AI agents to interact with popular services like Jira, GitHub, and Slack. It provides a unified interface for creating issues, pull requests, and sending notifications, with per-organization configuration stored in a local database.

## Features

- **Jira Integration**: Create and manage Jira issues
- **GitHub Integration**: Create pull requests and issues
- **Slack Integration**: Send messages and notifications via webhooks
- **Organization-based Configuration**: Store different credentials per organization
- **Tool Adapters**: Easy-to-use adapters for agent integration
- **Type-safe**: Built with TypeScript for better developer experience

## Installation

```bash
npm install
```

## Usage

### Basic Setup

```typescript
import { Orchestrator } from 'aurea-orchestrator';

// Create an orchestrator instance
const orchestrator = new Orchestrator('./aurea.db');

// Save organization configuration
await orchestrator.saveConfig({
  orgName: 'my-company',
  jiraConfig: {
    baseUrl: 'https://mycompany.atlassian.net',
    email: 'admin@mycompany.com',
    apiToken: 'your-jira-api-token',
    projectKey: 'PROJ',
  },
  githubConfig: {
    token: 'ghp_your_github_token',
    owner: 'mycompany',
    repo: 'my-repo',
  },
  slackConfig: {
    webhookUrl: 'https://hooks.slack.com/services/YOUR/WEBHOOK/URL',
    channel: '#general',
  },
});
```

### Using Jira Integration

```typescript
// Get Jira adapter
const jiraAdapter = orchestrator.getJiraAdapter('my-company');

// Create an issue
const result = await jiraAdapter.execute('createIssue', {
  summary: 'Bug in login flow',
  description: 'Users cannot log in with SSO',
  issueType: 'Bug',
  priority: 'High',
});

console.log(result); // { success: true, data: { key: 'PROJ-123', ... } }

// Get issue details
const issueResult = await jiraAdapter.execute('getIssue', {
  issueKey: 'PROJ-123',
});
```

### Using GitHub Integration

```typescript
// Get GitHub adapter
const githubAdapter = orchestrator.getGitHubAdapter('my-company');

// Create a pull request
const prResult = await githubAdapter.execute('createPullRequest', {
  title: 'Add new feature',
  body: 'This PR adds a new feature',
  head: 'feature-branch',
  base: 'main',
  draft: false,
});

console.log(prResult); // { success: true, data: { number: 123, url: '...' } }

// Create an issue
const issueResult = await githubAdapter.execute('createIssue', {
  title: 'Bug report',
  body: 'Found a bug in the application',
  labels: ['bug', 'high-priority'],
});
```

### Using Slack Integration

```typescript
// Get Slack adapter
const slackAdapter = orchestrator.getSlackAdapter('my-company');

// Send a simple message
await slackAdapter.execute('sendSimpleMessage', {
  text: 'Deployment completed successfully!',
  channel: '#deployments',
});

// Send a formatted notification
await slackAdapter.execute('sendNotification', {
  title: 'Build Status',
  message: 'The build has completed successfully',
  color: 'good',
});

// Send a rich message with attachments
await slackAdapter.execute('sendMessage', {
  text: 'Alert: System Issue Detected',
  attachments: [
    {
      color: 'danger',
      title: 'Error Details',
      text: 'Database connection timeout',
      fields: [
        { title: 'Severity', value: 'Critical', short: true },
        { title: 'Component', value: 'Database', short: true },
      ],
    },
  ],
});
```

### Direct Integration Usage

You can also use the integrations directly without adapters:

```typescript
import { JiraIntegration, GitHubIntegration, SlackIntegration } from 'aurea-orchestrator';

// Jira
const jira = new JiraIntegration({
  baseUrl: 'https://mycompany.atlassian.net',
  email: 'admin@mycompany.com',
  apiToken: 'token',
  projectKey: 'PROJ',
});

await jira.createIssue({
  summary: 'Issue title',
  description: 'Issue description',
  issueType: 'Task',
});

// GitHub
const github = new GitHubIntegration({
  token: 'ghp_token',
  owner: 'owner',
  repo: 'repo',
});

await github.createPullRequest({
  title: 'PR title',
  body: 'PR body',
  head: 'feature',
  base: 'main',
});

// Slack
const slack = new SlackIntegration({
  webhookUrl: 'https://hooks.slack.com/services/YOUR/WEBHOOK',
  channel: '#general',
});

await slack.sendMessage({ text: 'Hello!' });
```

## Configuration Management

```typescript
// Get configuration for an organization
const config = await orchestrator.getConfig('my-company');

// Get all configurations
const allConfigs = await orchestrator.getAllConfigs();

// Delete configuration
await orchestrator.deleteConfig('my-company');

// Close database connection
orchestrator.close();
```

## Testing

```bash
# Run all tests
npm test

# Run tests with coverage
npm test -- --coverage

# Run specific test file
npm test -- database.test.ts
```

## Development

```bash
# Build the project
npm run build

# Lint code
npm run lint

# Format code
npm run format
```

## API Reference

### OrganizationConfig

```typescript
interface OrganizationConfig {
  id?: number;
  orgName: string;
  jiraConfig?: JiraConfig;
  githubConfig?: GitHubConfig;
  slackConfig?: SlackConfig;
  createdAt?: Date;
  updatedAt?: Date;
}
```

### JiraConfig

```typescript
interface JiraConfig {
  baseUrl: string;      // e.g., 'https://mycompany.atlassian.net'
  email: string;        // Jira account email
  apiToken: string;     // Jira API token
  projectKey: string;   // Project key (e.g., 'PROJ')
}
```

### GitHubConfig

```typescript
interface GitHubConfig {
  token: string;   // GitHub personal access token
  owner: string;   // Repository owner
  repo: string;    // Repository name
}
```

### SlackConfig

```typescript
interface SlackConfig {
  webhookUrl: string;  // Incoming webhook URL
  channel?: string;    // Default channel (optional)
}
```

## License

MIT
