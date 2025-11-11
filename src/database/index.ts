import sqlite3 from 'sqlite3';
import { promisify } from 'util';
import { OrganizationConfig } from '../types';

export class Database {
  private db: sqlite3.Database;

  constructor(dbPath: string = './aurea.db') {
    this.db = new sqlite3.Database(dbPath);
    this.initializeDatabase();
  }

  private async initializeDatabase(): Promise<void> {
    const run = promisify(this.db.run.bind(this.db));
    
    await run(`
      CREATE TABLE IF NOT EXISTS organization_configs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        org_name TEXT UNIQUE NOT NULL,
        jira_config TEXT,
        github_config TEXT,
        slack_config TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
      )
    `);
  }

  async saveOrganizationConfig(config: OrganizationConfig): Promise<number> {
    const run = promisify(this.db.run.bind(this.db));
    
    const jiraConfig = config.jiraConfig ? JSON.stringify(config.jiraConfig) : null;
    const githubConfig = config.githubConfig ? JSON.stringify(config.githubConfig) : null;
    const slackConfig = config.slackConfig ? JSON.stringify(config.slackConfig) : null;

    const result = await run(
      `INSERT OR REPLACE INTO organization_configs 
       (org_name, jira_config, github_config, slack_config, updated_at)
       VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)`,
      [config.orgName, jiraConfig, githubConfig, slackConfig]
    );

    return (result as any).lastID;
  }

  async getOrganizationConfig(orgName: string): Promise<OrganizationConfig | null> {
    const get = promisify(this.db.get.bind(this.db));
    
    const row: any = await get(
      'SELECT * FROM organization_configs WHERE org_name = ?',
      [orgName]
    );

    if (!row) {
      return null;
    }

    return {
      id: row.id,
      orgName: row.org_name,
      jiraConfig: row.jira_config ? JSON.parse(row.jira_config) : undefined,
      githubConfig: row.github_config ? JSON.parse(row.github_config) : undefined,
      slackConfig: row.slack_config ? JSON.parse(row.slack_config) : undefined,
      createdAt: new Date(row.created_at),
      updatedAt: new Date(row.updated_at),
    };
  }

  async getAllOrganizationConfigs(): Promise<OrganizationConfig[]> {
    const all = promisify(this.db.all.bind(this.db));
    
    const rows: any[] = await all('SELECT * FROM organization_configs');

    return rows.map(row => ({
      id: row.id,
      orgName: row.org_name,
      jiraConfig: row.jira_config ? JSON.parse(row.jira_config) : undefined,
      githubConfig: row.github_config ? JSON.parse(row.github_config) : undefined,
      slackConfig: row.slack_config ? JSON.parse(row.slack_config) : undefined,
      createdAt: new Date(row.created_at),
      updatedAt: new Date(row.updated_at),
    }));
  }

  async deleteOrganizationConfig(orgName: string): Promise<void> {
    const run = promisify(this.db.run.bind(this.db));
    await run('DELETE FROM organization_configs WHERE org_name = ?', [orgName]);
  }

  close(): void {
    this.db.close();
  }
}
