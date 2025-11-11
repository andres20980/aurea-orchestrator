"""Tests for the Knowledge Base module."""
import os
import pytest
from unittest.mock import Mock, patch, MagicMock
from kb import KnowledgeBase


@pytest.fixture
def mock_db_connection():
    """Mock database connection."""
    with patch('kb.get_db_connection') as mock_conn:
        mock_cursor = MagicMock()
        mock_conn.return_value.cursor.return_value = mock_cursor
        yield mock_conn, mock_cursor


@pytest.fixture
def mock_litellm():
    """Mock LiteLLM embedding response."""
    with patch('kb.litellm.embedding') as mock_embed:
        mock_response = Mock()
        mock_response.data = [{"embedding": [0.1] * 1536}]
        mock_embed.return_value = mock_response
        yield mock_embed


class TestKnowledgeBase:
    """Test cases for KnowledgeBase class."""
    
    def test_initialization(self):
        """Test KnowledgeBase initialization."""
        kb = KnowledgeBase()
        assert kb.embedding_model == "text-embedding-3-small"
    
    def test_get_embedding(self, mock_litellm):
        """Test embedding generation."""
        kb = KnowledgeBase()
        embedding = kb._get_embedding("test text")
        
        assert len(embedding) == 1536
        assert embedding[0] == 0.1
        mock_litellm.assert_called_once()
    
    def test_index_file_new(self, mock_db_connection, mock_litellm):
        """Test indexing a new file."""
        mock_conn, mock_cursor = mock_db_connection
        mock_cursor.fetchone.side_effect = [None, (1,)]  # No existing file, then return ID
        
        kb = KnowledgeBase()
        file_id = kb.index_file("test.py", "print('hello')")
        
        assert file_id == 1
        assert mock_cursor.execute.call_count == 2  # SELECT and INSERT
    
    def test_index_file_update(self, mock_db_connection, mock_litellm):
        """Test updating an existing file."""
        mock_conn, mock_cursor = mock_db_connection
        mock_cursor.fetchone.side_effect = [(1,), (1,)]  # Existing file, then return ID
        
        kb = KnowledgeBase()
        file_id = kb.index_file("test.py", "print('updated')")
        
        assert file_id == 1
        assert mock_cursor.execute.call_count == 2  # SELECT and UPDATE
    
    def test_query(self, mock_db_connection, mock_litellm):
        """Test querying the knowledge base."""
        mock_conn, mock_cursor = mock_db_connection
        mock_cursor.fetchall.return_value = [
            (1, "test.py", "print('hello')", 0.95),
            (2, "main.py", "def main():", 0.87)
        ]
        
        kb = KnowledgeBase()
        results = kb.query("python function", top_k=2)
        
        assert len(results) == 2
        assert results[0]['id'] == 1
        assert results[0]['similarity'] == 0.95
        assert results[1]['id'] == 2
        assert results[1]['similarity'] == 0.87
    
    def test_index_directory(self, mock_db_connection, mock_litellm, tmp_path):
        """Test indexing a directory."""
        # Create test files
        test_file1 = tmp_path / "test1.py"
        test_file1.write_text("print('test1')")
        
        test_file2 = tmp_path / "test2.md"
        test_file2.write_text("# Test")
        
        mock_conn, mock_cursor = mock_db_connection
        mock_cursor.fetchone.side_effect = [None, (1,), None, (2,)]
        
        kb = KnowledgeBase()
        result = kb.index_directory(str(tmp_path), extensions=['.py', '.md'])
        
        assert result['indexed'] == 2
        assert len(result['files']) == 2
        assert len(result['errors']) == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
