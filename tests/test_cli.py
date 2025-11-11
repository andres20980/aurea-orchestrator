"""Test suite for Aurea CLI commands."""

import pytest
from typer.testing import CliRunner
from aurea.cli import app

runner = CliRunner()


def test_main_help():
    """Test that main help command works."""
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "Aurea Orchestrator" in result.stdout
    assert "request" in result.stdout
    assert "status" in result.stdout
    assert "approve" in result.stdout
    assert "simulate" in result.stdout
    assert "metrics" in result.stdout


def test_request_command():
    """Test the request command."""
    result = runner.invoke(app, ["request", "Test task"])
    assert result.exit_code == 0
    assert "Request submitted successfully" in result.stdout
    assert "Test task" in result.stdout
    assert "req-" in result.stdout


def test_request_with_options():
    """Test the request command with priority and agent options."""
    result = runner.invoke(
        app, ["request", "Deploy service", "--priority", "high", "--agent", "deploy-agent"]
    )
    assert result.exit_code == 0
    assert "high" in result.stdout
    assert "deploy-agent" in result.stdout


def test_status_with_id():
    """Test status command with request ID."""
    result = runner.invoke(app, ["status", "req-12345"])
    assert result.exit_code == 0
    assert "req-12345" in result.stdout
    assert "Status" in result.stdout


def test_status_all():
    """Test status command with --all flag."""
    result = runner.invoke(app, ["status", "--all"])
    assert result.exit_code == 0
    assert "All Requests Status" in result.stdout
    assert "Request ID" in result.stdout


def test_status_no_args():
    """Test status command without arguments fails appropriately."""
    result = runner.invoke(app, ["status"])
    assert result.exit_code == 1
    assert "Please provide a request ID or use --all flag" in result.stdout


def test_approve_command():
    """Test the approve command."""
    result = runner.invoke(app, ["approve", "req-12345"])
    assert result.exit_code == 0
    assert "approved" in result.stdout
    assert "req-12345" in result.stdout


def test_approve_with_comment():
    """Test approve command with comment."""
    result = runner.invoke(
        app, ["approve", "req-12345", "--comment", "Looks good"]
    )
    assert result.exit_code == 0
    assert "Looks good" in result.stdout


def test_simulate_command():
    """Test the simulate command."""
    result = runner.invoke(app, ["simulate", "test-scenario"])
    assert result.exit_code == 0
    assert "Starting simulation" in result.stdout
    assert "test-scenario" in result.stdout
    assert "Simulation completed" in result.stdout


def test_simulate_with_options():
    """Test simulate command with all options."""
    result = runner.invoke(
        app,
        [
            "simulate",
            "load-test",
            "--duration",
            "120",
            "--agents",
            "5",
            "--verbose",
        ],
    )
    assert result.exit_code == 0
    assert "120s" in result.stdout
    assert "5" in result.stdout
    assert "Initializing agents" in result.stdout


def test_metrics_command():
    """Test the metrics command."""
    result = runner.invoke(app, ["metrics"])
    assert result.exit_code == 0
    assert "Aurea Orchestrator Metrics" in result.stdout
    assert "24h" in result.stdout
    assert "Total Requests" in result.stdout


def test_metrics_with_range():
    """Test metrics command with custom range."""
    result = runner.invoke(app, ["metrics", "--range", "7d"])
    assert result.exit_code == 0
    assert "7d" in result.stdout


def test_metrics_with_export():
    """Test metrics command with export option."""
    result = runner.invoke(app, ["metrics", "--export", "json"])
    assert result.exit_code == 0
    assert "Metrics exported" in result.stdout
    assert "metrics-24h.json" in result.stdout


def test_request_help():
    """Test help for request command."""
    result = runner.invoke(app, ["request", "--help"])
    assert result.exit_code == 0
    assert "Submit a new request" in result.stdout
    assert "priority" in result.stdout
    assert "agent" in result.stdout


def test_status_help():
    """Test help for status command."""
    result = runner.invoke(app, ["status", "--help"])
    assert result.exit_code == 0
    assert "Check the status" in result.stdout


def test_approve_help():
    """Test help for approve command."""
    result = runner.invoke(app, ["approve", "--help"])
    assert result.exit_code == 0
    assert "Approve a pending request" in result.stdout


def test_simulate_help():
    """Test help for simulate command."""
    result = runner.invoke(app, ["simulate", "--help"])
    assert result.exit_code == 0
    assert "Run a simulation scenario" in result.stdout


def test_metrics_help():
    """Test help for metrics command."""
    result = runner.invoke(app, ["metrics", "--help"])
    assert result.exit_code == 0
    assert "View orchestrator metrics" in result.stdout
