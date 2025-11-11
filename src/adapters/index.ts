import { Database } from '../database';
import { JiraIntegration } from '../integrations/jira';
import { GitHubIntegration } from '../integrations/github';
import { SlackIntegration } from '../integrations/slack';
import { JiraIssue, GitHubPullRequest, SlackMessage, IntegrationResponse } from '../types';

/**
 * Base adapter interface for all tool integrations
 */
export interface ToolAdapter {
  execute(action: string, params: any): Promise<IntegrationResponse>;
}

/**
 * Jira Tool Adapter
 * Allows agents to interact with Jira
 */
export class JiraToolAdapter implements ToolAdapter {
  private db: Database;
  private orgName: string;

  constructor(db: Database, orgName: string) {
    this.db = db;
    this.orgName = orgName;
  }

  async execute(action: string, params: any): Promise<IntegrationResponse> {
    const config = await this.db.getOrganizationConfig(this.orgName);
    
    if (!config?.jiraConfig) {
      return {
        success: false,
        error: `Jira configuration not found for organization: ${this.orgName}`,
      };
    }

    const jira = new JiraIntegration(config.jiraConfig);

    switch (action) {
      case 'createIssue':
        return await jira.createIssue(params as JiraIssue);
      case 'getIssue':
        return await jira.getIssue(params.issueKey);
      default:
        return {
          success: false,
          error: `Unknown action: ${action}`,
        };
    }
  }
}

/**
 * GitHub Tool Adapter
 * Allows agents to interact with GitHub
 */
export class GitHubToolAdapter implements ToolAdapter {
  private db: Database;
  private orgName: string;

  constructor(db: Database, orgName: string) {
    this.db = db;
    this.orgName = orgName;
  }

  async execute(action: string, params: any): Promise<IntegrationResponse> {
    const config = await this.db.getOrganizationConfig(this.orgName);
    
    if (!config?.githubConfig) {
      return {
        success: false,
        error: `GitHub configuration not found for organization: ${this.orgName}`,
      };
    }

    const github = new GitHubIntegration(config.githubConfig);

    switch (action) {
      case 'createPullRequest':
        return await github.createPullRequest(params as GitHubPullRequest);
      case 'createIssue':
        return await github.createIssue(params.title, params.body, params.labels);
      case 'getPullRequest':
        return await github.getPullRequest(params.prNumber);
      default:
        return {
          success: false,
          error: `Unknown action: ${action}`,
        };
    }
  }
}

/**
 * Slack Tool Adapter
 * Allows agents to send messages to Slack
 */
export class SlackToolAdapter implements ToolAdapter {
  private db: Database;
  private orgName: string;

  constructor(db: Database, orgName: string) {
    this.db = db;
    this.orgName = orgName;
  }

  async execute(action: string, params: any): Promise<IntegrationResponse> {
    const config = await this.db.getOrganizationConfig(this.orgName);
    
    if (!config?.slackConfig) {
      return {
        success: false,
        error: `Slack configuration not found for organization: ${this.orgName}`,
      };
    }

    const slack = new SlackIntegration(config.slackConfig);

    switch (action) {
      case 'sendMessage':
        return await slack.sendMessage(params as SlackMessage);
      case 'sendSimpleMessage':
        return await slack.sendSimpleMessage(params.text, params.channel);
      case 'sendNotification':
        return await slack.sendNotification(params.title, params.message, params.color);
      default:
        return {
          success: false,
          error: `Unknown action: ${action}`,
        };
    }
  }
}
