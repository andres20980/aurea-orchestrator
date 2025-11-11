"""
Unit tests for GitOps automation module.
"""

import os
import unittest
from unittest.mock import Mock, patch, MagicMock, call
from tools.git_ops import GitOpsAutomation, GitOpsError, on_job_approved


class TestGitOpsAutomation(unittest.TestCase):
    """Test cases for GitOpsAutomation class."""
    
    def setUp(self):
        """Set up test fixtures."""
        os.environ["GITHUB_TOKEN"] = "test_token_12345"
        self.gitops = GitOpsAutomation(repo_path="/test/repo")
    
    def tearDown(self):
        """Clean up after tests."""
        if "GITHUB_TOKEN" in os.environ:
            del os.environ["GITHUB_TOKEN"]
    
    def test_init_with_token(self):
        """Test initialization with explicit token."""
        gitops = GitOpsAutomation(github_token="custom_token", repo_path="/test")
        self.assertEqual(gitops.github_token, "custom_token")
        self.assertEqual(gitops.repo_path, "/test")
    
    def test_init_without_token_raises_error(self):
        """Test initialization without token raises error."""
        del os.environ["GITHUB_TOKEN"]
        with self.assertRaises(GitOpsError) as context:
            GitOpsAutomation()
        self.assertIn("GitHub token is required", str(context.exception))
    
    def test_init_with_env_token(self):
        """Test initialization with environment token."""
        gitops = GitOpsAutomation()
        self.assertEqual(gitops.github_token, "test_token_12345")
    
    @patch('subprocess.run')
    def test_run_git_command_success(self, mock_run):
        """Test successful git command execution."""
        mock_run.return_value = Mock(stdout="success output", returncode=0)
        
        result = self.gitops._run_git_command(["status"])
        
        mock_run.assert_called_once()
        self.assertEqual(result, "success output")
    
    @patch('subprocess.run')
    def test_run_git_command_failure(self, mock_run):
        """Test git command failure handling."""
        from subprocess import CalledProcessError
        mock_run.side_effect = CalledProcessError(1, "git", stderr="error message")
        
        with self.assertRaises(GitOpsError) as context:
            self.gitops._run_git_command(["status"])
        self.assertIn("Git command failed", str(context.exception))
    
    @patch.object(GitOpsAutomation, '_run_git_command')
    def test_get_repo_info_https(self, mock_git):
        """Test repository info extraction from HTTPS URL."""
        mock_git.return_value = "https://github.com/owner/repo.git"
        
        owner, repo = self.gitops._get_repo_info()
        
        self.assertEqual(owner, "owner")
        self.assertEqual(repo, "repo")
    
    @patch.object(GitOpsAutomation, '_run_git_command')
    def test_get_repo_info_ssh(self, mock_git):
        """Test repository info extraction from SSH URL."""
        mock_git.return_value = "git@github.com:owner/repo.git"
        
        owner, repo = self.gitops._get_repo_info()
        
        self.assertEqual(owner, "owner")
        self.assertEqual(repo, "repo")
    
    @patch.object(GitOpsAutomation, '_run_git_command')
    def test_get_repo_info_invalid_url(self, mock_git):
        """Test repository info extraction with invalid URL."""
        mock_git.return_value = "https://gitlab.com/owner/repo.git"
        
        with self.assertRaises(GitOpsError):
            self.gitops._get_repo_info()
    
    @patch.object(GitOpsAutomation, '_run_git_command')
    def test_create_branch_success(self, mock_git):
        """Test successful branch creation."""
        job_id = "test-job-123"
        
        branch_name = self.gitops.create_branch(job_id)
        
        self.assertEqual(branch_name, f"gitops/job-{job_id}")
        # Verify git commands were called
        calls = mock_git.call_args_list
        self.assertTrue(any("fetch" in str(call) for call in calls))
        self.assertTrue(any("checkout" in str(call) for call in calls))
    
    @patch.object(GitOpsAutomation, '_run_git_command')
    def test_create_branch_with_custom_base(self, mock_git):
        """Test branch creation with custom base branch."""
        job_id = "test-job-456"
        
        branch_name = self.gitops.create_branch(job_id, base_branch="develop")
        
        self.assertEqual(branch_name, f"gitops/job-{job_id}")
        self.assertEqual(self.gitops.base_branch, "develop")
    
    @patch.object(GitOpsAutomation, '_run_git_command')
    def test_commit_changes_success(self, mock_git):
        """Test successful commit."""
        job_id = "test-job-789"
        mock_git.side_effect = [
            None,  # git add
            "M file.txt",  # git status --porcelain
            None,  # git commit
            "abc123def456"  # git rev-parse HEAD
        ]
        
        commit_sha = self.gitops.commit_changes(job_id)
        
        self.assertEqual(commit_sha, "abc123def456")
    
    @patch.object(GitOpsAutomation, '_run_git_command')
    def test_commit_changes_no_changes(self, mock_git):
        """Test commit with no changes."""
        job_id = "test-job-empty"
        mock_git.side_effect = [
            None,  # git add
            "",  # git status --porcelain (empty)
        ]
        
        with self.assertRaises(GitOpsError) as context:
            self.gitops.commit_changes(job_id)
        self.assertIn("No changes to commit", str(context.exception))
    
    @patch.object(GitOpsAutomation, '_run_git_command')
    def test_commit_changes_with_custom_message(self, mock_git):
        """Test commit with custom message."""
        job_id = "test-job-custom"
        custom_message = "Custom commit message"
        mock_git.side_effect = [
            None,  # git add
            "M file.txt",  # git status
            None,  # git commit
            "sha123"  # git rev-parse
        ]
        
        commit_sha = self.gitops.commit_changes(job_id, message=custom_message)
        
        # Verify custom message was used
        commit_call = [call for call in mock_git.call_args_list if "commit" in str(call)]
        self.assertTrue(any(custom_message in str(call) for call in commit_call))
    
    @patch.object(GitOpsAutomation, '_run_git_command')
    def test_commit_changes_specific_files(self, mock_git):
        """Test commit with specific files."""
        job_id = "test-job-files"
        files = ["file1.txt", "file2.py"]
        mock_git.side_effect = [
            None,  # git add file1
            None,  # git add file2
            "M file1.txt\nM file2.py",  # git status
            None,  # git commit
            "sha456"  # git rev-parse
        ]
        
        commit_sha = self.gitops.commit_changes(job_id, files=files)
        
        self.assertEqual(commit_sha, "sha456")
        # Verify files were added individually
        add_calls = [call for call in mock_git.call_args_list if "add" in str(call)]
        self.assertEqual(len(add_calls), 2)
    
    @patch.object(GitOpsAutomation, '_run_git_command')
    def test_push_branch_success(self, mock_git):
        """Test successful branch push."""
        branch_name = "gitops/job-test"
        
        self.gitops.push_branch(branch_name)
        
        mock_git.assert_called_once_with(["push", "-u", "origin", branch_name])
    
    @patch.object(GitOpsAutomation, '_run_git_command')
    def test_push_branch_failure(self, mock_git):
        """Test branch push failure."""
        branch_name = "gitops/job-fail"
        mock_git.side_effect = GitOpsError("Push failed")
        
        with self.assertRaises(GitOpsError) as context:
            self.gitops.push_branch(branch_name)
        self.assertIn("Failed to push branch", str(context.exception))
    
    @patch('requests.post')
    @patch.object(GitOpsAutomation, '_get_repo_info')
    def test_create_pull_request_success(self, mock_get_repo, mock_post):
        """Test successful PR creation."""
        mock_get_repo.return_value = ("owner", "repo")
        mock_response = Mock()
        mock_response.status_code = 201
        mock_response.json.return_value = {
            "number": 42,
            "html_url": "https://github.com/owner/repo/pull/42",
            "url": "https://api.github.com/repos/owner/repo/pulls/42",
            "state": "open"
        }
        mock_post.return_value = mock_response
        
        result = self.gitops.create_pull_request(
            job_id="test-job",
            branch_name="gitops/job-test-job"
        )
        
        self.assertEqual(result["number"], 42)
        self.assertIn("github.com", result["url"])
        self.assertEqual(result["state"], "open")
    
    @patch('requests.post')
    @patch.object(GitOpsAutomation, '_get_repo_info')
    def test_create_pull_request_failure(self, mock_get_repo, mock_post):
        """Test PR creation failure."""
        mock_get_repo.return_value = ("owner", "repo")
        mock_response = Mock()
        mock_response.status_code = 422
        mock_response.json.return_value = {"message": "Validation failed"}
        mock_post.return_value = mock_response
        
        with self.assertRaises(GitOpsError) as context:
            self.gitops.create_pull_request(
                job_id="test-job",
                branch_name="gitops/job-test-job"
            )
        self.assertIn("Failed to create PR", str(context.exception))
    
    @patch('requests.post')
    @patch.object(GitOpsAutomation, '_get_repo_info')
    def test_create_pull_request_custom_title_body(self, mock_get_repo, mock_post):
        """Test PR creation with custom title and body."""
        mock_get_repo.return_value = ("owner", "repo")
        mock_response = Mock()
        mock_response.status_code = 201
        mock_response.json.return_value = {
            "number": 10,
            "html_url": "https://github.com/owner/repo/pull/10",
            "url": "https://api.github.com/repos/owner/repo/pulls/10",
            "state": "open"
        }
        mock_post.return_value = mock_response
        
        custom_title = "Custom PR Title"
        custom_body = "Custom PR Body"
        
        result = self.gitops.create_pull_request(
            job_id="test-job",
            branch_name="gitops/job-test-job",
            title=custom_title,
            body=custom_body
        )
        
        # Verify the API was called with custom title and body
        call_args = mock_post.call_args
        self.assertEqual(call_args[1]["json"]["title"], custom_title)
        self.assertEqual(call_args[1]["json"]["body"], custom_body)
    
    @patch.object(GitOpsAutomation, 'create_pull_request')
    @patch.object(GitOpsAutomation, 'push_branch')
    @patch.object(GitOpsAutomation, 'commit_changes')
    @patch.object(GitOpsAutomation, 'create_branch')
    def test_execute_gitops_workflow_approved(self, mock_create_branch, 
                                              mock_commit, mock_push, mock_create_pr):
        """Test complete workflow execution with APPROVED status."""
        job_id = "workflow-test-123"
        mock_create_branch.return_value = f"gitops/job-{job_id}"
        mock_commit.return_value = "commit_sha_123"
        mock_create_pr.return_value = {
            "number": 99,
            "url": "https://github.com/owner/repo/pull/99"
        }
        
        result = self.gitops.execute_gitops_workflow(job_id, "APPROVED")
        
        self.assertIsNotNone(result)
        self.assertEqual(result["job_id"], job_id)
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["pr_number"], 99)
        
        # Verify all steps were called
        mock_create_branch.assert_called_once()
        mock_commit.assert_called_once()
        mock_push.assert_called_once()
        mock_create_pr.assert_called_once()
    
    @patch.object(GitOpsAutomation, 'create_branch')
    def test_execute_gitops_workflow_not_approved(self, mock_create_branch):
        """Test workflow execution with non-APPROVED status."""
        result = self.gitops.execute_gitops_workflow("test-job", "PENDING")
        
        self.assertIsNone(result)
        mock_create_branch.assert_not_called()
    
    @patch.object(GitOpsAutomation, 'create_pull_request')
    @patch.object(GitOpsAutomation, 'push_branch')
    @patch.object(GitOpsAutomation, 'commit_changes')
    @patch.object(GitOpsAutomation, 'create_branch')
    def test_execute_gitops_workflow_with_custom_params(self, mock_create_branch,
                                                        mock_commit, mock_push, mock_create_pr):
        """Test workflow with custom parameters."""
        job_id = "custom-job-456"
        custom_message = "Custom commit"
        custom_title = "Custom PR"
        custom_body = "Custom body"
        
        mock_create_branch.return_value = f"gitops/job-{job_id}"
        mock_commit.return_value = "sha789"
        mock_create_pr.return_value = {"number": 5, "url": "http://test"}
        
        result = self.gitops.execute_gitops_workflow(
            job_id=job_id,
            job_status="APPROVED",
            commit_message=custom_message,
            pr_title=custom_title,
            pr_body=custom_body
        )
        
        self.assertIsNotNone(result)
        # Verify custom message was passed
        mock_commit.assert_called_with(job_id, message=custom_message, files=None)
        # Verify custom PR params were passed
        call_kwargs = mock_create_pr.call_args[1]
        self.assertEqual(call_kwargs["title"], custom_title)
        self.assertEqual(call_kwargs["body"], custom_body)
    
    @patch.object(GitOpsAutomation, '__init__')
    @patch.object(GitOpsAutomation, 'execute_gitops_workflow')
    def test_on_job_approved_function(self, mock_execute, mock_init):
        """Test convenience function on_job_approved."""
        mock_init.return_value = None
        mock_execute.return_value = {"status": "success"}
        
        result = on_job_approved("convenience-test")
        
        mock_execute.assert_called_once_with("convenience-test", "APPROVED")
        self.assertEqual(result["status"], "success")


class TestGitOpsError(unittest.TestCase):
    """Test cases for GitOpsError exception."""
    
    def test_gitops_error_creation(self):
        """Test GitOpsError can be created and raised."""
        with self.assertRaises(GitOpsError) as context:
            raise GitOpsError("Test error message")
        
        self.assertEqual(str(context.exception), "Test error message")
    
    def test_gitops_error_is_exception(self):
        """Test GitOpsError is an Exception."""
        error = GitOpsError("test")
        self.assertIsInstance(error, Exception)


if __name__ == "__main__":
    unittest.main()
