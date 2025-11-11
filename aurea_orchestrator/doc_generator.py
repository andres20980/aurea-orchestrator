"""
Feature Documentation Generator

This module generates comprehensive feature documentation in markdown format.
"""

import os
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass, field


@dataclass
class CodeLink:
    """Represents a link to code in the repository."""
    path: str
    line_start: Optional[int] = None
    line_end: Optional[int] = None
    description: str = ""

    def to_markdown(self, repo_url: str = "") -> str:
        """Convert to markdown link."""
        if repo_url:
            url = f"{repo_url}/blob/main/{self.path}"
            if self.line_start:
                url += f"#L{self.line_start}"
                if self.line_end and self.line_end != self.line_start:
                    url += f"-L{self.line_end}"
            link_text = self.description or self.path
            return f"[{link_text}]({url})"
        else:
            link_text = self.description or self.path
            return f"`{link_text}`"


@dataclass
class Metric:
    """Represents a metric related to the feature."""
    name: str
    value: str
    description: str = ""

    def to_markdown(self) -> str:
        """Convert to markdown format."""
        if self.description:
            return f"- **{self.name}**: {self.value} - {self.description}"
        return f"- **{self.name}**: {self.value}"


@dataclass
class FeatureDocumentation:
    """Complete feature documentation data."""
    feature_id: str
    title: str
    job_plan: str
    implementation: str
    review: str
    code_links: List[CodeLink] = field(default_factory=list)
    metrics: List[Metric] = field(default_factory=list)
    created_at: Optional[datetime] = None
    author: str = ""
    tags: List[str] = field(default_factory=list)

    def __post_init__(self):
        """Initialize default values."""
        if self.created_at is None:
            self.created_at = datetime.now()


class FeatureDocGenerator:
    """Generates feature documentation in markdown format."""

    def __init__(self, docs_dir: str = "docs/features", repo_url: str = ""):
        """
        Initialize the documentation generator.

        Args:
            docs_dir: Directory where feature docs will be saved
            repo_url: Base repository URL for code links (e.g., https://github.com/user/repo)
        """
        self.docs_dir = docs_dir
        self.repo_url = repo_url.rstrip("/")

    def generate_markdown(self, doc: FeatureDocumentation) -> str:
        """
        Generate markdown documentation for a feature.

        Args:
            doc: Feature documentation data

        Returns:
            Formatted markdown string
        """
        lines = []

        # Header
        lines.append(f"# {doc.title}")
        lines.append("")

        # Metadata
        lines.append("## Metadata")
        lines.append("")
        lines.append(f"- **Feature ID**: `{doc.feature_id}`")
        if doc.author:
            lines.append(f"- **Author**: {doc.author}")
        if doc.created_at:
            lines.append(f"- **Created**: {doc.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
        if doc.tags:
            tags_str = ", ".join(f"`{tag}`" for tag in doc.tags)
            lines.append(f"- **Tags**: {tags_str}")
        lines.append("")

        # Job Plan
        lines.append("## Job Plan")
        lines.append("")
        lines.append(doc.job_plan)
        lines.append("")

        # Implementation
        lines.append("## Implementation")
        lines.append("")
        lines.append(doc.implementation)
        lines.append("")

        # Review
        lines.append("## Review")
        lines.append("")
        lines.append(doc.review)
        lines.append("")

        # Code Links
        if doc.code_links:
            lines.append("## Code References")
            lines.append("")
            for link in doc.code_links:
                lines.append(f"- {link.to_markdown(self.repo_url)}")
            lines.append("")

        # Metrics
        if doc.metrics:
            lines.append("## Metrics")
            lines.append("")
            for metric in doc.metrics:
                lines.append(metric.to_markdown())
            lines.append("")

        return "\n".join(lines)

    def save_documentation(self, doc: FeatureDocumentation) -> str:
        """
        Save feature documentation to a markdown file.

        Args:
            doc: Feature documentation data

        Returns:
            Path to the saved file
        """
        # Ensure docs directory exists
        os.makedirs(self.docs_dir, exist_ok=True)

        # Generate markdown content
        markdown_content = self.generate_markdown(doc)

        # Save to file
        file_path = os.path.join(self.docs_dir, f"{doc.feature_id}.md")
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(markdown_content)

        return file_path

    def load_documentation(self, feature_id: str) -> Optional[str]:
        """
        Load existing documentation for a feature.

        Args:
            feature_id: Feature identifier

        Returns:
            Markdown content or None if not found
        """
        file_path = os.path.join(self.docs_dir, f"{feature_id}.md")
        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as f:
                return f.read()
        return None

    def list_features(self) -> List[str]:
        """
        List all documented features.

        Returns:
            List of feature IDs
        """
        if not os.path.exists(self.docs_dir):
            return []

        feature_ids = []
        for filename in os.listdir(self.docs_dir):
            if filename.endswith(".md"):
                feature_ids.append(filename[:-3])  # Remove .md extension
        return sorted(feature_ids)
