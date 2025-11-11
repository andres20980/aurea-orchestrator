"""
Example usage of GitOps automation.

This script demonstrates how to use the GitOps automation
to create branches, commit changes, and open PRs when a job
is approved.
"""

import sys
from tools.git_ops import GitOpsAutomation, GitOpsError, on_job_approved


def example_basic_usage():
    """Basic example of using GitOps automation."""
    try:
        # Simple one-line usage when job is approved
        result = on_job_approved("job-12345")
        
        if result:
            print(f"✓ GitOps workflow completed successfully!")
            print(f"  - Branch: {result['branch_name']}")
            print(f"  - Commit: {result['commit_sha']}")
            print(f"  - PR #{result['pr_number']}: {result['pr_url']}")
        else:
            print("Job status was not APPROVED, no action taken.")
            
    except GitOpsError as e:
        print(f"✗ GitOps workflow failed: {e}", file=sys.stderr)
        sys.exit(1)


def example_advanced_usage():
    """Advanced example with custom configuration."""
    try:
        # Initialize GitOps automation
        gitops = GitOpsAutomation(repo_path=".")
        
        job_id = "job-67890"
        job_status = "APPROVED"  # This would come from your job system
        
        # Execute workflow with custom messages
        result = gitops.execute_gitops_workflow(
            job_id=job_id,
            job_status=job_status,
            commit_message=f"Apply approved changes for {job_id}",
            pr_title=f"[Automated] Changes for job {job_id}",
            pr_body="""## Automated Job Changes

This PR contains changes that were automatically approved and applied.

**Review carefully before merging.**
"""
        )
        
        if result:
            print(f"✓ GitOps workflow completed!")
            print(f"  - Job ID: {result['job_id']}")
            print(f"  - PR URL: {result['pr_url']}")
        
    except GitOpsError as e:
        print(f"✗ Error: {e}", file=sys.stderr)
        sys.exit(1)


def example_step_by_step():
    """Example showing each step of the workflow."""
    try:
        gitops = GitOpsAutomation()
        
        job_id = "job-99999"
        
        # Step 1: Create branch
        print(f"Creating branch for job {job_id}...")
        branch_name = gitops.create_branch(job_id)
        print(f"✓ Branch created: {branch_name}")
        
        # Step 2: Commit changes
        print("Committing changes...")
        commit_sha = gitops.commit_changes(
            job_id=job_id,
            message=f"Automated changes for {job_id}"
        )
        print(f"✓ Changes committed: {commit_sha[:8]}")
        
        # Step 3: Push branch
        print("Pushing branch to remote...")
        gitops.push_branch(branch_name)
        print(f"✓ Branch pushed")
        
        # Step 4: Create PR
        print("Creating pull request...")
        pr_info = gitops.create_pull_request(
            job_id=job_id,
            branch_name=branch_name
        )
        print(f"✓ PR created: {pr_info['url']}")
        
    except GitOpsError as e:
        print(f"✗ Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    print("=== GitOps Automation Examples ===\n")
    
    print("Example 1: Basic Usage")
    print("-" * 40)
    # Uncomment to run:
    # example_basic_usage()
    print("(Commented out - uncomment to run)\n")
    
    print("Example 2: Advanced Usage")
    print("-" * 40)
    # Uncomment to run:
    # example_advanced_usage()
    print("(Commented out - uncomment to run)\n")
    
    print("Example 3: Step-by-Step")
    print("-" * 40)
    # Uncomment to run:
    # example_step_by_step()
    print("(Commented out - uncomment to run)\n")
    
    print("\nTo use these examples:")
    print("1. Set your GITHUB_TOKEN environment variable")
    print("2. Uncomment the example you want to run")
    print("3. Run: python example_usage.py")
