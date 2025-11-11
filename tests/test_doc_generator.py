"""Tests for the feature documentation generator."""

import os
import tempfile
import shutil
from datetime import datetime
import pytest

from aurea_orchestrator.doc_generator import (
    FeatureDocGenerator,
    FeatureDocumentation,
    CodeLink,
    Metric,
)


class TestCodeLink:
    """Tests for CodeLink class."""

    def test_basic_link_without_repo_url(self):
        """Test basic code link without repository URL."""
        link = CodeLink(path="src/main.py", description="Main module")
        result = link.to_markdown()
        assert result == "`Main module`"

    def test_link_with_repo_url(self):
        """Test code link with repository URL."""
        link = CodeLink(path="src/main.py", description="Main module")
        result = link.to_markdown(repo_url="https://github.com/user/repo")
        assert result == "[Main module](https://github.com/user/repo/blob/main/src/main.py)"

    def test_link_with_line_numbers(self):
        """Test code link with line numbers."""
        link = CodeLink(
            path="src/main.py",
            line_start=10,
            line_end=20,
            description="Main function"
        )
        result = link.to_markdown(repo_url="https://github.com/user/repo")
        assert result == "[Main function](https://github.com/user/repo/blob/main/src/main.py#L10-L20)"

    def test_link_with_single_line(self):
        """Test code link with single line number."""
        link = CodeLink(
            path="src/main.py",
            line_start=15,
            description="Import statement"
        )
        result = link.to_markdown(repo_url="https://github.com/user/repo")
        assert result == "[Import statement](https://github.com/user/repo/blob/main/src/main.py#L15)"

    def test_link_without_description_uses_path(self):
        """Test that path is used when description is empty."""
        link = CodeLink(path="src/utils.py")
        result = link.to_markdown()
        assert result == "`src/utils.py`"


class TestMetric:
    """Tests for Metric class."""

    def test_metric_without_description(self):
        """Test metric without description."""
        metric = Metric(name="Lines of Code", value="150")
        result = metric.to_markdown()
        assert result == "- **Lines of Code**: 150"

    def test_metric_with_description(self):
        """Test metric with description."""
        metric = Metric(
            name="Test Coverage",
            value="95%",
            description="Unit test coverage"
        )
        result = metric.to_markdown()
        assert result == "- **Test Coverage**: 95% - Unit test coverage"


class TestFeatureDocumentation:
    """Tests for FeatureDocumentation dataclass."""

    def test_default_creation_time(self):
        """Test that created_at defaults to current time."""
        doc = FeatureDocumentation(
            feature_id="test-feature",
            title="Test Feature",
            job_plan="Plan details",
            implementation="Implementation details",
            review="Review feedback"
        )
        assert doc.created_at is not None
        assert isinstance(doc.created_at, datetime)

    def test_custom_creation_time(self):
        """Test setting custom creation time."""
        custom_time = datetime(2025, 1, 1, 12, 0, 0)
        doc = FeatureDocumentation(
            feature_id="test-feature",
            title="Test Feature",
            job_plan="Plan details",
            implementation="Implementation details",
            review="Review feedback",
            created_at=custom_time
        )
        assert doc.created_at == custom_time


class TestFeatureDocGenerator:
    """Tests for FeatureDocGenerator class."""

    @pytest.fixture
    def temp_docs_dir(self):
        """Create a temporary directory for docs."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)

    @pytest.fixture
    def generator(self, temp_docs_dir):
        """Create a generator instance."""
        return FeatureDocGenerator(
            docs_dir=temp_docs_dir,
            repo_url="https://github.com/test/repo"
        )

    @pytest.fixture
    def sample_doc(self):
        """Create a sample feature documentation."""
        return FeatureDocumentation(
            feature_id="feature-001",
            title="Test Feature Implementation",
            job_plan="This is the job plan:\n- Step 1\n- Step 2",
            implementation="Implementation was done by:\n- Creating module X\n- Adding tests",
            review="Review feedback:\n- Looks good\n- Minor style fixes needed",
            code_links=[
                CodeLink(path="src/feature.py", line_start=10, line_end=50, description="Feature implementation"),
                CodeLink(path="tests/test_feature.py", description="Feature tests"),
            ],
            metrics=[
                Metric(name="Lines Added", value="200"),
                Metric(name="Test Coverage", value="98%", description="Excellent coverage"),
            ],
            author="John Doe",
            tags=["feature", "enhancement"],
            created_at=datetime(2025, 11, 11, 10, 0, 0)
        )

    def test_generate_markdown_basic(self, generator, sample_doc):
        """Test basic markdown generation."""
        markdown = generator.generate_markdown(sample_doc)
        
        assert "# Test Feature Implementation" in markdown
        assert "feature-001" in markdown
        assert "John Doe" in markdown
        assert "2025-11-11 10:00:00" in markdown

    def test_generate_markdown_sections(self, generator, sample_doc):
        """Test that all sections are included."""
        markdown = generator.generate_markdown(sample_doc)
        
        assert "## Job Plan" in markdown
        assert "## Implementation" in markdown
        assert "## Review" in markdown
        assert "## Code References" in markdown
        assert "## Metrics" in markdown

    def test_generate_markdown_content(self, generator, sample_doc):
        """Test that content is correctly included."""
        markdown = generator.generate_markdown(sample_doc)
        
        assert "This is the job plan:" in markdown
        assert "Implementation was done by:" in markdown
        assert "Review feedback:" in markdown

    def test_generate_markdown_code_links(self, generator, sample_doc):
        """Test that code links are formatted correctly."""
        markdown = generator.generate_markdown(sample_doc)
        
        assert "[Feature implementation](https://github.com/test/repo/blob/main/src/feature.py#L10-L50)" in markdown
        assert "[Feature tests](https://github.com/test/repo/blob/main/tests/test_feature.py)" in markdown

    def test_generate_markdown_metrics(self, generator, sample_doc):
        """Test that metrics are formatted correctly."""
        markdown = generator.generate_markdown(sample_doc)
        
        assert "**Lines Added**: 200" in markdown
        assert "**Test Coverage**: 98% - Excellent coverage" in markdown

    def test_generate_markdown_tags(self, generator, sample_doc):
        """Test that tags are included."""
        markdown = generator.generate_markdown(sample_doc)
        
        assert "`feature`" in markdown
        assert "`enhancement`" in markdown

    def test_save_documentation(self, generator, temp_docs_dir, sample_doc):
        """Test saving documentation to file."""
        file_path = generator.save_documentation(sample_doc)
        
        assert os.path.exists(file_path)
        assert file_path == os.path.join(temp_docs_dir, "feature-001.md")
        
        with open(file_path, "r") as f:
            content = f.read()
            assert "# Test Feature Implementation" in content

    def test_load_documentation(self, generator, temp_docs_dir, sample_doc):
        """Test loading documentation from file."""
        # First save
        generator.save_documentation(sample_doc)
        
        # Then load
        content = generator.load_documentation("feature-001")
        assert content is not None
        assert "# Test Feature Implementation" in content

    def test_load_nonexistent_documentation(self, generator):
        """Test loading documentation that doesn't exist."""
        content = generator.load_documentation("nonexistent-feature")
        assert content is None

    def test_list_features_empty(self, generator):
        """Test listing features when directory is empty."""
        features = generator.list_features()
        assert features == []

    def test_list_features(self, generator, sample_doc, temp_docs_dir):
        """Test listing features."""
        # Save a few features
        generator.save_documentation(sample_doc)
        
        doc2 = FeatureDocumentation(
            feature_id="feature-002",
            title="Another Feature",
            job_plan="Plan",
            implementation="Impl",
            review="Review"
        )
        generator.save_documentation(doc2)
        
        features = generator.list_features()
        assert len(features) == 2
        assert "feature-001" in features
        assert "feature-002" in features
        assert features == sorted(features)  # Should be sorted

    def test_generator_creates_docs_dir(self, temp_docs_dir):
        """Test that generator creates docs directory if it doesn't exist."""
        docs_dir = os.path.join(temp_docs_dir, "new_docs")
        generator = FeatureDocGenerator(docs_dir=docs_dir)
        
        doc = FeatureDocumentation(
            feature_id="test",
            title="Test",
            job_plan="Plan",
            implementation="Impl",
            review="Review"
        )
        
        generator.save_documentation(doc)
        assert os.path.exists(docs_dir)

    def test_repo_url_trailing_slash_removed(self):
        """Test that trailing slash is removed from repo URL."""
        generator = FeatureDocGenerator(
            docs_dir="/tmp",
            repo_url="https://github.com/test/repo/"
        )
        assert generator.repo_url == "https://github.com/test/repo"

    def test_minimal_documentation(self, generator):
        """Test documentation with minimal fields."""
        doc = FeatureDocumentation(
            feature_id="minimal",
            title="Minimal Feature",
            job_plan="Simple plan",
            implementation="Simple implementation",
            review="Simple review"
        )
        
        markdown = generator.generate_markdown(doc)
        assert "# Minimal Feature" in markdown
        assert "## Job Plan" in markdown
        assert "Simple plan" in markdown
        # Should not have empty sections
        assert "## Code References" not in markdown
        assert "## Metrics" not in markdown
