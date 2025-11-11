/**
 * Type definitions for integrations
 */

export interface OrganizationConfig {
  id?: number;
  orgName: string;
  jiraConfig?: JiraConfig;
  githubConfig?: GitHubConfig;
  slackConfig?: SlackConfig;
  createdAt?: Date;
  updatedAt?: Date;
}

export interface JiraConfig {
  baseUrl: string;
  email: string;
  apiToken: string;
  projectKey: string;
}

export interface GitHubConfig {
  token: string;
  owner: string;
  repo: string;
}

export interface SlackConfig {
  webhookUrl: string;
  channel?: string;
}

export interface JiraIssue {
  key?: string;
  summary: string;
  description: string;
  issueType: string;
  priority?: string;
  assignee?: string;
}

export interface GitHubPullRequest {
  title: string;
  body: string;
  head: string;
  base: string;
  draft?: boolean;
}

export interface SlackMessage {
  text: string;
  channel?: string;
  username?: string;
  iconEmoji?: string;
  attachments?: SlackAttachment[];
}

export interface SlackAttachment {
  color?: string;
  title?: string;
  text?: string;
  fields?: Array<{
    title: string;
    value: string;
    short?: boolean;
  }>;
}

export interface IntegrationResponse {
  success: boolean;
  data?: any;
  error?: string;
}
