# aurea-orchestrator
Automated Unified Reasoning & Execution Agents

## Overview

This repository provides GitOps automation tools that automatically create branches, commit changes, and open pull requests when job statuses are approved.

## Features

- **Automated Branch Creation**: Creates branches with job-specific naming (`gitops/job-{job_id}`)
- **Automated Commits**: Commits changes with customizable messages
- **GitHub PR Creation**: Opens pull requests via GitHub API
- **Status-Driven Workflow**: Triggers only when job status is `APPROVED`

## Installation

1. Clone this repository:
```bash
git clone https://github.com/andres20980/aurea-orchestrator.git
cd aurea-orchestrator
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## GitHub Token Setup

### Required Permissions

To use the GitOps automation, you need a GitHub Personal Access Token with the following permissions:

- **`repo`** (Full control of private repositories)
  - `repo:status` - Access commit status
  - `repo_deployment` - Access deployment status
  - `public_repo` - Access public repositories
  - `repo:invite` - Access repository invitations
  
- **`workflow`** (Update GitHub Action workflows) - Optional, if working with workflows

### Creating a GitHub Token

1. Go to GitHub Settings → Developer settings → Personal access tokens → Tokens (classic)
2. Click "Generate new token (classic)"
3. Give your token a descriptive name (e.g., "aurea-orchestrator-gitops")
4. Select the required scopes listed above
5. Click "Generate token"
6. **Copy the token immediately** (you won't be able to see it again)

### Setting the Token

Set the token as an environment variable:

```bash
export GITHUB_TOKEN="your_github_token_here"
```

Or add it to your `.bashrc`, `.zshrc`, or `.bash_profile`:

```bash
echo 'export GITHUB_TOKEN="your_github_token_here"' >> ~/.bashrc
source ~/.bashrc
```

## Usage

### Basic Usage

The simplest way to trigger the GitOps workflow when a job is approved:

```python
from tools.git_ops import on_job_approved

# Automatically creates branch, commits, and opens PR
result = on_job_approved("job-12345")

if result:
    print(f"PR created: {result['pr_url']}")
```

### Advanced Usage

For more control over the workflow:

```python
from tools.git_ops import GitOpsAutomation

# Initialize the automation
gitops = GitOpsAutomation(repo_path=".")

# Execute workflow with custom parameters
result = gitops.execute_gitops_workflow(
    job_id="job-67890",
    job_status="APPROVED",
    commit_message="Apply approved changes",
    pr_title="[Automated] Job 67890 Changes",
    pr_body="This PR contains automatically approved changes."
)

if result:
    print(f"Success! PR #{result['pr_number']}: {result['pr_url']}")
```

### Step-by-Step Workflow

You can also execute each step individually:

```python
from tools.git_ops import GitOpsAutomation

gitops = GitOpsAutomation()
job_id = "job-99999"

# Step 1: Create branch
branch_name = gitops.create_branch(job_id)

# Step 2: Commit changes
commit_sha = gitops.commit_changes(job_id, message="Custom message")

# Step 3: Push to remote
gitops.push_branch(branch_name)

# Step 4: Create pull request
pr_info = gitops.create_pull_request(job_id, branch_name)
print(f"PR URL: {pr_info['url']}")
```

## Workflow Details

### When a Job is Approved

1. **Branch Creation**: A new branch is created with the pattern `gitops/job-{job_id}`
   - Based on the `main` branch (configurable)
   - Automatically fetches and pulls latest changes

2. **Commit Changes**: All changes are committed
   - Default message: `GitOps: Automated commit for job {job_id} at {timestamp}`
   - Can specify custom commit message
   - Can commit specific files or all changes

3. **Push to Remote**: The branch is pushed to GitHub
   - Sets upstream tracking automatically

4. **Create Pull Request**: A PR is opened via GitHub API
   - Default title: `GitOps: Automated changes for job {job_id}`
   - Default body includes job details and timestamp
   - Can customize title and description

### Branch Naming Convention

Branches are named using the pattern: `gitops/job-{job_id}`

Examples:
- Job ID `12345` → Branch `gitops/job-12345`
- Job ID `abc-xyz-789` → Branch `gitops/job-abc-xyz-789`

## Examples

See `example_usage.py` for complete working examples:

```bash
python example_usage.py
```

## Testing

Run the test suite:

```bash
python -m pytest test_git_ops.py -v
```

Or using unittest:

```bash
python -m unittest test_git_ops.py -v
```

## API Reference

### `GitOpsAutomation`

Main class for GitOps automation.

**Constructor:**
```python
GitOpsAutomation(github_token=None, repo_path=".")
```

**Methods:**

- `create_branch(job_id, base_branch=None)` - Create a new branch
- `commit_changes(job_id, message=None, files=None)` - Commit changes
- `push_branch(branch_name)` - Push branch to remote
- `create_pull_request(job_id, branch_name, title=None, body=None, base_branch=None)` - Create PR
- `execute_gitops_workflow(job_id, job_status, ...)` - Execute complete workflow

### `on_job_approved(job_id, **kwargs)`

Convenience function that executes the complete GitOps workflow for an approved job.

## Error Handling

All operations raise `GitOpsError` on failure:

```python
from tools.git_ops import GitOpsError

try:
    result = on_job_approved("job-123")
except GitOpsError as e:
    print(f"GitOps failed: {e}")
```

## Security Considerations

- **Never commit the GitHub token** to the repository
- Use environment variables for sensitive data
- Rotate tokens regularly
- Use tokens with minimal required permissions
- Consider using GitHub Apps for production deployments

## Troubleshooting

### "GitHub token is required" error

Make sure you've set the `GITHUB_TOKEN` environment variable:
```bash
export GITHUB_TOKEN="your_token_here"
```

### "Failed to create PR" error

- Verify your token has `repo` permissions
- Check that the base branch exists
- Ensure you're not creating a duplicate PR

### "No changes to commit" error

Make sure there are actual file changes before running the workflow.

## Contributing

Contributions are welcome! Please ensure:
- Code follows existing style
- Tests pass: `python -m unittest test_git_ops.py`
- Documentation is updated

## License

MIT License - See LICENSE file for details
