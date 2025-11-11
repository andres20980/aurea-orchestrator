import {
  ToolRegistry,
  Allowlist,
  AuditLogger,
  ToolExecutor,
  githubIssuesCreateTool,
  githubIssuesListTool,
  jiraCreateIssueTool,
  slackPostMessageTool,
} from './index';

/**
 * Example usage of the Aurea Orchestrator Tooling API
 */
async function main() {
  console.log('🚀 Aurea Orchestrator - Tooling API Example\n');

  // Initialize components
  const registry = new ToolRegistry();
  const allowlist = new Allowlist();
  const auditLogger = new AuditLogger();
  const executor = new ToolExecutor(registry, allowlist, auditLogger);

  // Register sample tools
  console.log('📝 Registering tools...');
  registry.register(githubIssuesCreateTool);
  registry.register(githubIssuesListTool);
  registry.register(jiraCreateIssueTool);
  registry.register(slackPostMessageTool);
  console.log(`✅ Registered ${registry.getAll().length} tools\n`);

  // Configure allowlist for agents
  console.log('🔒 Configuring agent allowlists...');
  allowlist.configure({
    agentId: 'agent-1',
    allowedTools: ['github-list-issues', 'slack-post-message'],
    rateLimit: {
      maxRequests: 10,
      windowMs: 60000, // 1 minute
    },
  });

  allowlist.configure({
    agentId: 'agent-2',
    allowedTools: ['github-create-issue', 'jira-create-issue'],
    rateLimit: {
      maxRequests: 5,
      windowMs: 60000,
    },
  });
  console.log('✅ Configured allowlists for 2 agents\n');

  // Example 1: Allowed execution
  console.log('📋 Example 1: Listing GitHub issues (allowed)');
  const result1 = await executor.execute({
    toolId: 'github-list-issues',
    agentId: 'agent-1',
    parameters: {
      owner: 'octocat',
      repo: 'Hello-World',
      state: 'open',
    },
  });
  console.log('Result:', result1.success ? '✅ Success' : '❌ Failed');
  if (!result1.success) {
    console.log('Error:', result1.error);
  }
  console.log();

  // Example 2: Denied execution (not in allowlist)
  console.log('📋 Example 2: Creating GitHub issue (denied - not in allowlist)');
  const result2 = await executor.execute({
    toolId: 'github-create-issue',
    agentId: 'agent-1',
    parameters: {
      owner: 'octocat',
      repo: 'Hello-World',
    },
    body: {
      title: 'Test Issue',
      body: 'This is a test issue',
    },
  });
  console.log('Result:', result2.success ? '✅ Success' : '❌ Failed');
  if (!result2.success) {
    console.log('Error:', result2.error);
  }
  console.log();

  // Example 3: Parameter validation
  console.log('📋 Example 3: Invalid parameters');
  const result3 = await executor.execute({
    toolId: 'github-list-issues',
    agentId: 'agent-1',
    parameters: {
      // Missing required 'owner' and 'repo' parameters
      state: 'open',
    },
  });
  console.log('Result:', result3.success ? '✅ Success' : '❌ Failed');
  if (!result3.success) {
    console.log('Error:', result3.error);
  }
  console.log();

  // Display audit logs
  console.log('📊 Audit Log Summary:');
  const stats = auditLogger.getStats();
  console.log(`  Total executions: ${stats.totalExecutions}`);
  console.log(`  Successful: ${stats.successfulExecutions}`);
  console.log(`  Failed: ${stats.failedExecutions}`);
  console.log(`  Average duration: ${stats.averageDuration.toFixed(2)}ms`);
  console.log('\n  Tool usage:');
  for (const [toolId, count] of Object.entries(stats.toolUsage)) {
    console.log(`    - ${toolId}: ${count}`);
  }
  console.log('\n  Agent usage:');
  for (const [agentId, count] of Object.entries(stats.agentUsage)) {
    console.log(`    - ${agentId}: ${count}`);
  }
  console.log();

  // Display recent logs
  console.log('📜 Recent Audit Logs:');
  const recentLogs = auditLogger.getAllLogs().slice(-3);
  for (const log of recentLogs) {
    console.log(`  [${log.timestamp.toISOString()}] ${log.agentId} → ${log.toolId}`);
    console.log(`    Status: ${log.result.success ? 'SUCCESS' : 'FAILED'}`);
    if (!log.result.success) {
      console.log(`    Error: ${log.result.error}`);
    }
    console.log(`    Duration: ${log.durationMs}ms`);
  }
}

// Run the example
if (require.main === module) {
  main().catch(console.error);
}

export { main };
