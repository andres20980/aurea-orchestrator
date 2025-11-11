/**
 * Example: Using integrations directly without the orchestrator
 */

import { JiraIntegration, GitHubIntegration, SlackIntegration } from '../src';

async function main() {
  console.log('=== Direct Integration Usage Examples ===\n');

  // Example 1: Jira Integration
  console.log('--- Jira Integration ---');
  const jira = new JiraIntegration({
    baseUrl: 'https://your-domain.atlassian.net',
    email: 'your-email@example.com',
    apiToken: 'your-api-token',
    projectKey: 'PROJ',
  });

  const jiraIssue = await jira.createIssue({
    summary: 'Sample Bug Report',
    description: 'This is a sample bug report created via API',
    issueType: 'Bug',
    priority: 'High',
  });

  if (jiraIssue.success) {
    console.log('✓ Created Jira issue:', jiraIssue.data?.key);
    
    // Retrieve the issue
    const retrievedIssue = await jira.getIssue(jiraIssue.data?.key);
    if (retrievedIssue.success) {
      console.log('✓ Retrieved issue details');
    }
  } else {
    console.log('✗ Error:', jiraIssue.error);
  }

  // Example 2: GitHub Integration
  console.log('\n--- GitHub Integration ---');
  const github = new GitHubIntegration({
    token: 'ghp_your_github_token',
    owner: 'your-username',
    repo: 'your-repo',
  });

  // Create a GitHub issue
  const githubIssue = await github.createIssue(
    'Sample Issue',
    'This is a sample issue created via GitHub API',
    ['bug', 'documentation']
  );

  if (githubIssue.success) {
    console.log('✓ Created GitHub issue #' + githubIssue.data?.number);
    console.log('  URL:', githubIssue.data?.url);
  } else {
    console.log('✗ Error:', githubIssue.error);
  }

  // Create a pull request
  const pr = await github.createPullRequest({
    title: 'Sample Pull Request',
    body: 'This PR demonstrates the API integration',
    head: 'feature-branch',
    base: 'main',
    draft: true,
  });

  if (pr.success) {
    console.log('✓ Created pull request #' + pr.data?.number);
    console.log('  URL:', pr.data?.url);
  } else {
    console.log('✗ Error:', pr.error);
  }

  // Example 3: Slack Integration
  console.log('\n--- Slack Integration ---');
  const slack = new SlackIntegration({
    webhookUrl: 'https://hooks.slack.com/services/YOUR/WEBHOOK/URL',
    channel: '#general',
  });

  // Send a simple message
  const simpleMsg = await slack.sendSimpleMessage('Hello from Aurea Orchestrator!');
  if (simpleMsg.success) {
    console.log('✓ Sent simple message to Slack');
  } else {
    console.log('✗ Error:', simpleMsg.error);
  }

  // Send a notification
  const notification = await slack.sendNotification(
    'Deployment Status',
    'Application deployed successfully to production',
    'good'
  );
  if (notification.success) {
    console.log('✓ Sent notification to Slack');
  } else {
    console.log('✗ Error:', notification.error);
  }

  // Send a rich message with attachments
  const richMsg = await slack.sendMessage({
    text: 'System Alert',
    username: 'Monitoring Bot',
    iconEmoji: ':warning:',
    attachments: [
      {
        color: 'warning',
        title: 'High Memory Usage Detected',
        text: 'Server XYZ is using 85% of available memory',
        fields: [
          { title: 'Server', value: 'XYZ-001', short: true },
          { title: 'Memory', value: '85%', short: true },
          { title: 'CPU', value: '45%', short: true },
          { title: 'Status', value: 'Warning', short: true },
        ],
      },
    ],
  });

  if (richMsg.success) {
    console.log('✓ Sent rich message to Slack');
  } else {
    console.log('✗ Error:', richMsg.error);
  }

  console.log('\n=== Examples Complete ===');
}

// Run the example
main().catch(console.error);
