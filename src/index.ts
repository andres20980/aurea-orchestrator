// Core exports
export { ToolRegistry } from './core/registry';
export { Allowlist } from './core/allowlist';
export { ToolExecutor } from './core/executor';
export { AuditLogger } from './audit/logger';

// Type exports
export type {
  ToolDefinition,
  ToolExecutionRequest,
  ToolExecutionResult,
  AuditLogEntry,
  AllowlistConfig,
  HttpMethod,
} from './core/types';

// Sample tools
export {
  githubIssuesCreateTool,
  githubIssuesListTool,
} from './tools/github';

export {
  jiraCreateIssueTool,
  jiraSearchIssuesTool,
} from './tools/jira';

export {
  slackPostMessageTool,
  slackListChannelsTool,
} from './tools/slack';
