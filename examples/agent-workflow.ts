/**
 * Example: Agent workflow that uses multiple integrations
 */

import { Orchestrator } from '../src';

async function agentWorkflow() {
  const orchestrator = new Orchestrator('./agent-workflow.db');

  try {
    // Setup: Configure organization
    await orchestrator.saveConfig({
      orgName: 'dev-team',
      jiraConfig: {
        baseUrl: 'https://devteam.atlassian.net',
        email: 'bot@devteam.com',
        apiToken: process.env.JIRA_API_TOKEN || 'token',
        projectKey: 'DEV',
      },
      githubConfig: {
        token: process.env.GITHUB_TOKEN || 'token',
        owner: 'dev-team',
        repo: 'backend',
      },
      slackConfig: {
        webhookUrl: process.env.SLACK_WEBHOOK || 'https://hooks.slack.com/services/TEST',
        channel: '#dev-updates',
      },
    });

    console.log('🤖 Agent Workflow Started\n');

    // Step 1: Agent detects a bug and creates a Jira issue
    console.log('Step 1: Creating Jira issue for detected bug...');
    const jiraAdapter = orchestrator.getJiraAdapter('dev-team');
    const issueResult = await jiraAdapter.execute('createIssue', {
      summary: 'Critical: Database connection timeout in production',
      description: `The production database is experiencing connection timeouts.
      
Details:
- First detected: ${new Date().toISOString()}
- Affected service: User Authentication
- Error rate: 15%
- Impact: Users cannot log in`,
      issueType: 'Bug',
      priority: 'Highest',
    });

    if (!issueResult.success) {
      console.error('✗ Failed to create Jira issue:', issueResult.error);
      return;
    }

    const issueKey = issueResult.data?.key;
    console.log(`✓ Created Jira issue: ${issueKey}\n`);

    // Step 2: Agent creates a hotfix PR
    console.log('Step 2: Creating GitHub PR with hotfix...');
    const githubAdapter = orchestrator.getGitHubAdapter('dev-team');
    const prResult = await githubAdapter.execute('createPullRequest', {
      title: `Hotfix: Increase database connection pool size [${issueKey}]`,
      body: `## Description
This PR fixes the database timeout issue by increasing the connection pool size.

## Related Issue
- Jira: ${issueKey}

## Changes
- Increased max connections from 10 to 50
- Added connection retry logic
- Improved error handling

## Testing
- [x] Tested in staging environment
- [x] Connection timeout resolved
- [x] No performance degradation`,
      head: 'hotfix/db-connection-timeout',
      base: 'main',
      draft: false,
    });

    if (!prResult.success) {
      console.error('✗ Failed to create PR:', prResult.error);
      return;
    }

    const prUrl = prResult.data?.url;
    console.log(`✓ Created pull request: ${prUrl}\n`);

    // Step 3: Agent notifies team via Slack
    console.log('Step 3: Notifying team on Slack...');
    const slackAdapter = orchestrator.getSlackAdapter('dev-team');
    const slackResult = await slackAdapter.execute('sendMessage', {
      text: '🚨 Critical Bug Detected and Hotfix Created',
      attachments: [
        {
          color: 'danger',
          title: 'Database Connection Timeout',
          text: 'A critical bug has been detected in production',
          fields: [
            {
              title: 'Jira Issue',
              value: `<https://devteam.atlassian.net/browse/${issueKey}|${issueKey}>`,
              short: true,
            },
            {
              title: 'Pull Request',
              value: `<${prUrl}|View PR>`,
              short: true,
            },
            {
              title: 'Priority',
              value: 'Highest',
              short: true,
            },
            {
              title: 'Status',
              value: 'Hotfix Ready for Review',
              short: true,
            },
          ],
        },
        {
          color: 'good',
          title: '✓ Automated Actions Completed',
          text: '• Jira issue created\n• Hotfix PR opened\n• Team notified',
        },
      ],
    });

    if (!slackResult.success) {
      console.error('✗ Failed to send Slack notification:', slackResult.error);
      return;
    }

    console.log('✓ Team notified on Slack\n');

    // Step 4: Summary
    console.log('=== Workflow Complete ===');
    console.log(`Jira Issue: ${issueKey}`);
    console.log(`GitHub PR: ${prUrl}`);
    console.log('Slack notification sent');
    console.log('\n🎉 Agent successfully handled the incident!');
  } catch (error) {
    console.error('Error in workflow:', error);
  } finally {
    orchestrator.close();
  }
}

// Run the workflow
agentWorkflow();
