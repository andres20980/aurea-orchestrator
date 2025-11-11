/**
 * Example: Using the Orchestrator to manage integrations
 */

import { Orchestrator } from '../src';

async function main() {
  // Create orchestrator instance
  const orchestrator = new Orchestrator('./example.db');

  try {
    // Save configuration for an organization
    console.log('Saving organization configuration...');
    await orchestrator.saveConfig({
      orgName: 'acme-corp',
      jiraConfig: {
        baseUrl: 'https://acme.atlassian.net',
        email: 'admin@acme.com',
        apiToken: 'your-jira-api-token',
        projectKey: 'ACME',
      },
      githubConfig: {
        token: 'ghp_your_github_token',
        owner: 'acme-corp',
        repo: 'main-repo',
      },
      slackConfig: {
        webhookUrl: 'https://hooks.slack.com/services/YOUR/WEBHOOK/URL',
        channel: '#engineering',
      },
    });
    console.log('Configuration saved successfully!');

    // Retrieve configuration
    console.log('\nRetrieving configuration...');
    const config = await orchestrator.getConfig('acme-corp');
    console.log('Organization:', config?.orgName);
    console.log('Has Jira config:', !!config?.jiraConfig);
    console.log('Has GitHub config:', !!config?.githubConfig);
    console.log('Has Slack config:', !!config?.slackConfig);

    // Example: Create a Jira issue
    console.log('\n=== Creating Jira Issue ===');
    const jiraAdapter = orchestrator.getJiraAdapter('acme-corp');
    const jiraResult = await jiraAdapter.execute('createIssue', {
      summary: 'Implement new feature',
      description: 'We need to implement the user authentication feature',
      issueType: 'Story',
      priority: 'Medium',
    });

    if (jiraResult.success) {
      console.log('✓ Jira issue created:', jiraResult.data?.key);
    } else {
      console.log('✗ Failed to create Jira issue:', jiraResult.error);
    }

    // Example: Create a GitHub PR
    console.log('\n=== Creating GitHub Pull Request ===');
    const githubAdapter = orchestrator.getGitHubAdapter('acme-corp');
    const prResult = await githubAdapter.execute('createPullRequest', {
      title: 'Add authentication feature',
      body: 'This PR implements the authentication feature discussed in ACME-123',
      head: 'feature/authentication',
      base: 'main',
      draft: false,
    });

    if (prResult.success) {
      console.log('✓ Pull request created:', prResult.data?.url);
    } else {
      console.log('✗ Failed to create PR:', prResult.error);
    }

    // Example: Send Slack notification
    console.log('\n=== Sending Slack Notification ===');
    const slackAdapter = orchestrator.getSlackAdapter('acme-corp');
    const slackResult = await slackAdapter.execute('sendNotification', {
      title: 'Deployment Successful',
      message: 'Version 2.0.0 has been deployed to production',
      color: 'good',
    });

    if (slackResult.success) {
      console.log('✓ Slack notification sent');
    } else {
      console.log('✗ Failed to send Slack notification:', slackResult.error);
    }

    // List all configurations
    console.log('\n=== All Organizations ===');
    const allConfigs = await orchestrator.getAllConfigs();
    allConfigs.forEach((config) => {
      console.log(`- ${config.orgName}`);
    });
  } catch (error) {
    console.error('Error:', error);
  } finally {
    // Always close the database connection
    orchestrator.close();
    console.log('\nDatabase connection closed.');
  }
}

// Run the example
main();
