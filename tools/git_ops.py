"""
GitOps Automation Module

This module provides functionality to automate Git operations when a job status
changes to APPROVED. It creates branches, commits changes, and opens pull requests
using the GitHub API.
"""

import os
import json
import subprocess
from typing import Optional, Dict, Any
from datetime import datetime


class GitOpsError(Exception):
    """Custom exception for GitOps operations"""
    pass


class GitOpsAutomation:
    """
    Handles GitOps automation workflow including branch creation,
    commits, and PR creation via GitHub API.
    """
    
    def __init__(self, github_token: Optional[str] = None, repo_path: str = "."):
        """
        Initialize GitOps automation.
        
        Args:
            github_token: GitHub personal access token (defaults to GITHUB_TOKEN env var)
            repo_path: Path to the git repository
        """
        self.github_token = github_token or os.getenv("GITHUB_TOKEN")
        if not self.github_token:
            raise GitOpsError("GitHub token is required. Set GITHUB_TOKEN environment variable.")
        
        self.repo_path = repo_path
        self.base_branch = "main"
        
    def _run_git_command(self, args: list) -> str:
        """
        Execute a git command and return output.
        
        Args:
            args: List of command arguments
            
        Returns:
            Command output as string
            
        Raises:
            GitOpsError: If git command fails
        """
        try:
            result = subprocess.run(
                ["git"] + args,
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            raise GitOpsError(f"Git command failed: {e.stderr}")
    
    def _get_repo_info(self) -> tuple[str, str]:
        """
        Extract repository owner and name from git remote.
        
        Returns:
            Tuple of (owner, repo_name)
            
        Raises:
            GitOpsError: If unable to determine repo info
        """
        try:
            remote_url = self._run_git_command(["remote", "get-url", "origin"])
            
            # Remove .git suffix if present
            remote_url = remote_url.rstrip(".git")
            
            # Parse GitHub URL (supports both HTTPS and SSH)
            # SSH format: git@github.com:owner/repo.git
            if remote_url.startswith("git@github.com:"):
                parts = remote_url.replace("git@github.com:", "").split("/")
            # HTTPS format: https://github.com/owner/repo.git
            elif remote_url.startswith("https://github.com/"):
                # Extract path after github.com/
                path = remote_url[len("https://github.com/"):]
                parts = path.split("/")
            else:
                raise GitOpsError(f"Unsupported GitHub URL format: {remote_url}")
            
            if len(parts) >= 2:
                return parts[0], parts[1]
            
            raise GitOpsError(f"Could not parse GitHub repository from URL: {remote_url}")
        except Exception as e:
            raise GitOpsError(f"Failed to get repository info: {str(e)}")
    
    def create_branch(self, job_id: str, base_branch: Optional[str] = None) -> str:
        """
        Create a new branch with naming based on job_id.
        
        Args:
            job_id: Unique job identifier
            base_branch: Base branch to branch from (defaults to main)
            
        Returns:
            Name of the created branch
            
        Raises:
            GitOpsError: If branch creation fails
        """
        if base_branch:
            self.base_branch = base_branch
            
        branch_name = f"gitops/job-{job_id}"
        
        try:
            # Ensure we're on the base branch and up to date
            self._run_git_command(["fetch", "origin"])
            self._run_git_command(["checkout", self.base_branch])
            self._run_git_command(["pull", "origin", self.base_branch])
            
            # Create and checkout new branch
            self._run_git_command(["checkout", "-b", branch_name])
            
            return branch_name
        except GitOpsError as e:
            raise GitOpsError(f"Failed to create branch '{branch_name}': {str(e)}")
    
    def commit_changes(self, job_id: str, message: Optional[str] = None, 
                      files: Optional[list] = None) -> str:
        """
        Commit changes to the current branch.
        
        Args:
            job_id: Unique job identifier
            message: Commit message (auto-generated if not provided)
            files: List of files to commit (commits all if not specified)
            
        Returns:
            Commit SHA
            
        Raises:
            GitOpsError: If commit fails
        """
        try:
            # Add files
            if files:
                for file in files:
                    self._run_git_command(["add", file])
            else:
                self._run_git_command(["add", "."])
            
            # Check if there are changes to commit
            status = self._run_git_command(["status", "--porcelain"])
            if not status:
                raise GitOpsError("No changes to commit")
            
            # Generate commit message if not provided
            if not message:
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                message = f"GitOps: Automated commit for job {job_id} at {timestamp}"
            
            # Commit changes
            self._run_git_command(["commit", "-m", message])
            
            # Get commit SHA
            commit_sha = self._run_git_command(["rev-parse", "HEAD"])
            
            return commit_sha
        except GitOpsError as e:
            raise GitOpsError(f"Failed to commit changes: {str(e)}")
    
    def push_branch(self, branch_name: str) -> None:
        """
        Push branch to remote repository.
        
        Args:
            branch_name: Name of the branch to push
            
        Raises:
            GitOpsError: If push fails
        """
        try:
            self._run_git_command(["push", "-u", "origin", branch_name])
        except GitOpsError as e:
            raise GitOpsError(f"Failed to push branch '{branch_name}': {str(e)}")
    
    def create_pull_request(self, job_id: str, branch_name: str,
                           title: Optional[str] = None,
                           body: Optional[str] = None,
                           base_branch: Optional[str] = None) -> Dict[str, Any]:
        """
        Create a pull request using GitHub API.
        
        Args:
            job_id: Unique job identifier
            branch_name: Name of the head branch
            title: PR title (auto-generated if not provided)
            body: PR description (auto-generated if not provided)
            base_branch: Base branch for PR (defaults to main)
            
        Returns:
            Dictionary containing PR information (number, url, etc.)
            
        Raises:
            GitOpsError: If PR creation fails
        """
        try:
            import requests
        except ImportError:
            raise GitOpsError("requests library is required. Install with: pip install requests")
        
        owner, repo = self._get_repo_info()
        base = base_branch or self.base_branch
        
        # Generate title and body if not provided
        if not title:
            title = f"GitOps: Automated changes for job {job_id}"
        
        if not body:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            body = f"""## GitOps Automated Pull Request

**Job ID:** {job_id}
**Status:** APPROVED
**Timestamp:** {timestamp}

This pull request was automatically created by the GitOps automation system
when the job status changed to APPROVED.

### Changes
Please review the changes made by this automated workflow.
"""
        
        # Create PR using GitHub API
        url = f"https://api.github.com/repos/{owner}/{repo}/pulls"
        headers = {
            "Authorization": f"token {self.github_token}",
            "Accept": "application/vnd.github.v3+json"
        }
        
        data = {
            "title": title,
            "body": body,
            "head": branch_name,
            "base": base
        }
        
        response = requests.post(url, headers=headers, json=data)
        
        if response.status_code == 201:
            pr_data = response.json()
            return {
                "number": pr_data["number"],
                "url": pr_data["html_url"],
                "api_url": pr_data["url"],
                "state": pr_data["state"]
            }
        else:
            error_msg = response.json().get("message", "Unknown error")
            raise GitOpsError(f"Failed to create PR: {error_msg} (Status: {response.status_code})")
    
    def execute_gitops_workflow(self, job_id: str, job_status: str,
                                changes_files: Optional[list] = None,
                                commit_message: Optional[str] = None,
                                pr_title: Optional[str] = None,
                                pr_body: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Execute the complete GitOps workflow when job status is APPROVED.
        
        This is the main entry point that orchestrates:
        1. Branch creation
        2. Committing changes
        3. Pushing to remote
        4. Creating a pull request
        
        Args:
            job_id: Unique job identifier
            job_status: Current job status
            changes_files: Optional list of specific files to commit
            commit_message: Optional custom commit message
            pr_title: Optional custom PR title
            pr_body: Optional custom PR body
            
        Returns:
            Dictionary with workflow results if status is APPROVED, None otherwise
            
        Raises:
            GitOpsError: If any step in the workflow fails
        """
        # Only execute if status is APPROVED
        if job_status != "APPROVED":
            return None
        
        try:
            # Step 1: Create branch
            branch_name = self.create_branch(job_id)
            
            # Step 2: Commit changes
            commit_sha = self.commit_changes(job_id, message=commit_message, files=changes_files)
            
            # Step 3: Push branch
            self.push_branch(branch_name)
            
            # Step 4: Create pull request
            pr_info = self.create_pull_request(
                job_id=job_id,
                branch_name=branch_name,
                title=pr_title,
                body=pr_body
            )
            
            return {
                "job_id": job_id,
                "branch_name": branch_name,
                "commit_sha": commit_sha,
                "pr_number": pr_info["number"],
                "pr_url": pr_info["url"],
                "status": "success"
            }
        except Exception as e:
            raise GitOpsError(f"GitOps workflow failed for job {job_id}: {str(e)}")


def on_job_approved(job_id: str, **kwargs) -> Dict[str, Any]:
    """
    Convenience function to execute GitOps workflow when a job is approved.
    
    Args:
        job_id: Unique job identifier
        **kwargs: Additional arguments to pass to execute_gitops_workflow
        
    Returns:
        Dictionary with workflow results
        
    Example:
        >>> result = on_job_approved("job-12345")
        >>> print(f"PR created: {result['pr_url']}")
    """
    gitops = GitOpsAutomation()
    return gitops.execute_gitops_workflow(job_id, "APPROVED", **kwargs)
