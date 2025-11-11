"""Docker-based sandbox runner for isolated code execution."""

import docker
import os
import time
import tempfile
import shutil
from typing import Dict, Optional, List, Tuple
from pathlib import Path
import json


class SandboxRunner:
    """
    Docker-based sandbox runner with resource limits and security constraints.
    
    Features:
    - Resource limits (CPU, memory)
    - Execution timeouts
    - Read-only filesystem
    - Log and artifact capture
    - Isolated network (optional)
    """
    
    def __init__(
        self,
        image: str = "aurea-sandbox:latest",
        cpu_limit: Optional[float] = 1.0,
        memory_limit: str = "512m",
        default_timeout: int = 30,
    ):
        """
        Initialize the sandbox runner.
        
        Args:
            image: Docker image to use for sandboxing
            cpu_limit: CPU limit (e.g., 1.0 = 1 CPU core)
            memory_limit: Memory limit (e.g., "512m", "1g")
            default_timeout: Default timeout in seconds
        """
        self.image = image
        self.cpu_limit = cpu_limit
        self.memory_limit = memory_limit
        self.default_timeout = default_timeout
        self.client = docker.from_env()
        
    def run(
        self,
        code: str,
        language: str = "python",
        timeout: Optional[int] = None,
        files: Optional[Dict[str, str]] = None,
        readonly: bool = True,
        capture_artifacts: bool = True,
    ) -> Dict:
        """
        Execute code in an isolated Docker container.
        
        Args:
            code: The code to execute
            language: Programming language (python, javascript, etc.)
            timeout: Execution timeout in seconds
            files: Additional files to include {filename: content}
            readonly: Mount workspace as read-only
            capture_artifacts: Capture output files/artifacts
            
        Returns:
            Dict with execution results including stdout, stderr, exit_code, artifacts
        """
        timeout = timeout or self.default_timeout
        
        # Create temporary workspace
        workspace = tempfile.mkdtemp(prefix="sandbox_")
        artifacts_dir = os.path.join(workspace, "artifacts")
        os.makedirs(artifacts_dir, exist_ok=True)
        
        try:
            # Prepare code file
            code_file = self._get_code_filename(language)
            code_path = os.path.join(workspace, code_file)
            
            with open(code_path, 'w') as f:
                f.write(code)
            
            # Add additional files if provided
            if files:
                for filename, content in files.items():
                    file_path = os.path.join(workspace, filename)
                    with open(file_path, 'w') as f:
                        f.write(content)
            
            # Prepare execution command
            command = self._get_execution_command(language, code_file)
            
            # Configure container
            container_config = {
                "image": self.image,
                "command": command,
                "detach": True,
                "remove": False,  # Keep container to retrieve logs
                "network_disabled": True,  # Isolate from network
                "volumes": {
                    workspace: {
                        "bind": "/workspace",
                        "mode": "ro" if readonly else "rw"
                    }
                },
                "working_dir": "/workspace",
                "mem_limit": self.memory_limit,
                "nano_cpus": int(self.cpu_limit * 1e9) if self.cpu_limit else None,
                "user": "sandbox",
            }
            
            # Run container
            start_time = time.time()
            container = self.client.containers.run(**container_config)
            
            # Wait for completion with timeout
            try:
                result = container.wait(timeout=timeout)
                exit_code = result.get("StatusCode", -1)
                timed_out = False
            except Exception:
                # Timeout occurred
                container.kill()
                exit_code = -1
                timed_out = True
            
            execution_time = time.time() - start_time
            
            # Capture logs
            stdout = container.logs(stdout=True, stderr=False).decode('utf-8', errors='replace')
            stderr = container.logs(stdout=False, stderr=True).decode('utf-8', errors='replace')
            
            # Capture artifacts if requested and not readonly
            artifacts = {}
            if capture_artifacts and not readonly:
                artifacts = self._capture_artifacts(container, artifacts_dir)
            
            # Cleanup container
            container.remove(force=True)
            
            return {
                "success": exit_code == 0 and not timed_out,
                "exit_code": exit_code,
                "stdout": stdout,
                "stderr": stderr,
                "execution_time": execution_time,
                "timed_out": timed_out,
                "timeout": timeout,
                "artifacts": artifacts,
            }
            
        finally:
            # Cleanup workspace
            shutil.rmtree(workspace, ignore_errors=True)
    
    def _get_code_filename(self, language: str) -> str:
        """Get the appropriate filename for the code based on language."""
        extensions = {
            "python": "main.py",
            "javascript": "main.js",
            "node": "main.js",
            "bash": "main.sh",
            "shell": "main.sh",
        }
        return extensions.get(language.lower(), "main.txt")
    
    def _get_execution_command(self, language: str, code_file: str) -> List[str]:
        """Get the execution command for the given language."""
        commands = {
            "python": ["python3", code_file],
            "javascript": ["node", code_file],
            "node": ["node", code_file],
            "bash": ["bash", code_file],
            "shell": ["bash", code_file],
        }
        return commands.get(language.lower(), ["cat", code_file])
    
    def _capture_artifacts(self, container, artifacts_dir: str) -> Dict[str, str]:
        """Capture artifacts from the container."""
        artifacts = {}
        try:
            # List files in workspace (excluding the original code files)
            # This is a simplified implementation
            # In production, you'd want more sophisticated artifact detection
            pass
        except Exception as e:
            print(f"Error capturing artifacts: {e}")
        
        return artifacts
    
    def build_image(self, dockerfile_path: str = "Dockerfile", tag: Optional[str] = None):
        """
        Build the sandbox Docker image.
        
        Args:
            dockerfile_path: Path to Dockerfile
            tag: Tag for the image (defaults to self.image)
        """
        tag = tag or self.image
        path = os.path.dirname(dockerfile_path) or "."
        
        print(f"Building Docker image: {tag}")
        self.client.images.build(
            path=path,
            dockerfile=os.path.basename(dockerfile_path),
            tag=tag,
            rm=True,
        )
        print(f"Successfully built image: {tag}")
    
    def cleanup(self):
        """Cleanup resources."""
        try:
            # Remove any dangling containers from this runner
            containers = self.client.containers.list(
                all=True,
                filters={"ancestor": self.image}
            )
            for container in containers:
                try:
                    container.remove(force=True)
                except Exception:
                    pass
        except Exception as e:
            print(f"Error during cleanup: {e}")
