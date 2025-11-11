import { Database } from '../database';
import { JiraToolAdapter, GitHubToolAdapter, SlackToolAdapter } from '../adapters';
import { OrganizationConfig } from '../types';

/**
 * Main orchestrator class that manages integrations and tool adapters
 */
export class Orchestrator {
  private db: Database;

  constructor(dbPath?: string) {
    this.db = new Database(dbPath);
  }

  /**
   * Get a Jira adapter for the specified organization
   */
  getJiraAdapter(orgName: string): JiraToolAdapter {
    return new JiraToolAdapter(this.db, orgName);
  }

  /**
   * Get a GitHub adapter for the specified organization
   */
  getGitHubAdapter(orgName: string): GitHubToolAdapter {
    return new GitHubToolAdapter(this.db, orgName);
  }

  /**
   * Get a Slack adapter for the specified organization
   */
  getSlackAdapter(orgName: string): SlackToolAdapter {
    return new SlackToolAdapter(this.db, orgName);
  }

  /**
   * Save organization configuration
   */
  async saveConfig(config: OrganizationConfig): Promise<number> {
    return await this.db.saveOrganizationConfig(config);
  }

  /**
   * Get organization configuration
   */
  async getConfig(orgName: string): Promise<OrganizationConfig | null> {
    return await this.db.getOrganizationConfig(orgName);
  }

  /**
   * Get all organization configurations
   */
  async getAllConfigs(): Promise<OrganizationConfig[]> {
    return await this.db.getAllOrganizationConfigs();
  }

  /**
   * Delete organization configuration
   */
  async deleteConfig(orgName: string): Promise<void> {
    await this.db.deleteOrganizationConfig(orgName);
  }

  /**
   * Close database connection
   */
  close(): void {
    this.db.close();
  }
}
