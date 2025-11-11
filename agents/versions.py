"""
Agent Versions Management
Provides semantic versioning for all agents
"""

from typing import Dict, Optional, Tuple
from packaging import version


# Agent versions following semantic versioning (MAJOR.MINOR.PATCH)
AGENT_VERSIONS = {
    'architect': '1.0.0',
    'code': '1.0.0',
    'review': '1.0.0',
    'test': '1.0.0',
    'deploy': '1.0.0',
}


def get_agent_version(agent_name: str) -> str:
    """
    Get the version of a specific agent.
    
    Args:
        agent_name: Name of the agent (e.g., 'architect', 'code', 'review')
        
    Returns:
        Version string in semantic versioning format (MAJOR.MINOR.PATCH)
        
    Raises:
        ValueError: If agent_name is not recognized
    """
    agent_name_lower = agent_name.lower()
    if agent_name_lower not in AGENT_VERSIONS:
        raise ValueError(f"Unknown agent: {agent_name}. Available agents: {list(AGENT_VERSIONS.keys())}")
    return AGENT_VERSIONS[agent_name_lower]


def get_all_agent_versions() -> Dict[str, str]:
    """
    Get versions of all registered agents.
    
    Returns:
        Dictionary mapping agent names to their versions
    """
    return AGENT_VERSIONS.copy()


def compare_versions(version1: str, version2: str) -> int:
    """
    Compare two semantic versions.
    
    Args:
        version1: First version string (e.g., '1.0.0')
        version2: Second version string (e.g., '1.1.0')
        
    Returns:
        -1 if version1 < version2
         0 if version1 == version2
         1 if version1 > version2
    """
    v1 = version.parse(version1)
    v2 = version.parse(version2)
    
    if v1 < v2:
        return -1
    elif v1 > v2:
        return 1
    else:
        return 0


def version_has_breaking_changes(old_version: str, new_version: str) -> bool:
    """
    Check if upgrading from old_version to new_version includes breaking changes.
    According to semantic versioning, breaking changes increment the MAJOR version.
    
    Args:
        old_version: Old version string
        new_version: New version string
        
    Returns:
        True if there are breaking changes, False otherwise
    """
    old = version.parse(old_version)
    new = version.parse(new_version)
    
    return new.major > old.major
