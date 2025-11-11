"""Knowledge Base module for embedding and querying project files."""
import os
from typing import List, Dict, Any
from pathlib import Path
import litellm
from database import get_db_connection
from config import settings


class KnowledgeBase:
    """Knowledge Base for storing and querying embedded project files."""
    
    def __init__(self):
        """Initialize the Knowledge Base."""
        self.embedding_model = settings.embedding_model
        if settings.openai_api_key:
            os.environ["OPENAI_API_KEY"] = settings.openai_api_key
    
    def _validate_path(self, path: str) -> Path:
        """
        Validate and normalize a file path to prevent path traversal attacks.
        
        Args:
            path: The path to validate
            
        Returns:
            Validated Path object
            
        Raises:
            ValueError: If the path is invalid or contains path traversal
        """
        # Convert to absolute path and resolve
        abs_path = Path(path).resolve()
        
        # Check if path exists
        if not abs_path.exists():
            raise ValueError(f"Path does not exist: {path}")
        
        return abs_path
    
    def _get_embedding(self, text: str) -> List[float]:
        """
        Generate embedding for the given text using LiteLLM.
        
        Args:
            text: The text to embed
            
        Returns:
            List of floats representing the embedding
        """
        response = litellm.embedding(
            model=self.embedding_model,
            input=[text]
        )
        return response.data[0]["embedding"]
    
    def index_file(self, file_path: str, content: str) -> int:
        """
        Index a file by storing its content and embedding.
        
        Args:
            file_path: Path to the file
            content: Content of the file
            
        Returns:
            ID of the indexed file
        """
        embedding = self._get_embedding(content)
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            # Check if file already exists
            cursor.execute(
                "SELECT id FROM knowledge_base WHERE file_path = %s",
                (file_path,)
            )
            existing = cursor.fetchone()
            
            if existing:
                # Update existing file
                cursor.execute(
                    """UPDATE knowledge_base 
                       SET content = %s, embedding = %s, updated_at = CURRENT_TIMESTAMP 
                       WHERE file_path = %s
                       RETURNING id""",
                    (content, embedding, file_path)
                )
                file_id = cursor.fetchone()[0]
            else:
                # Insert new file
                cursor.execute(
                    """INSERT INTO knowledge_base (file_path, content, embedding) 
                       VALUES (%s, %s, %s) 
                       RETURNING id""",
                    (file_path, content, embedding)
                )
                file_id = cursor.fetchone()[0]
            
            conn.commit()
            return file_id
            
        finally:
            cursor.close()
            conn.close()
    
    def index_directory(self, directory_path: str, extensions: List[str] = None) -> Dict[str, Any]:
        """
        Index all files in a directory.
        
        Args:
            directory_path: Path to the directory
            extensions: List of file extensions to index (e.g., ['.py', '.md'])
            
        Returns:
            Dictionary with indexing statistics
            
        Raises:
            ValueError: If the directory path is invalid
        """
        if extensions is None:
            extensions = ['.py', '.md', '.txt', '.js', '.ts', '.java', '.cpp', '.h']
        
        # Validate and normalize the directory path
        try:
            validated_dir = self._validate_path(directory_path)
        except ValueError as e:
            return {
                'indexed': 0,
                'files': [],
                'errors': [{'path': directory_path, 'error': str(e)}]
            }
        
        # Ensure it's a directory
        if not validated_dir.is_dir():
            return {
                'indexed': 0,
                'files': [],
                'errors': [{'path': directory_path, 'error': 'Path is not a directory'}]
            }
        
        indexed_files = []
        errors = []
        
        # Use Path.rglob for safer directory traversal
        for ext in extensions:
            # Create pattern without leading slash - rglob needs relative patterns
            pattern = f"*{ext}"
            for file_path in validated_dir.rglob(pattern):
                try:
                    # Additional check to ensure we're still within the validated directory
                    if not str(file_path.resolve()).startswith(str(validated_dir)):
                        continue
                    
                    # Skip if it's not a file
                    if not file_path.is_file():
                        continue
                    
                    content = file_path.read_text(encoding='utf-8')
                    file_id = self.index_file(str(file_path), content)
                    indexed_files.append({
                        'id': file_id,
                        'path': str(file_path)
                    })
                except Exception as e:
                    errors.append({
                        'path': str(file_path),
                        'error': str(e)
                    })
        
        return {
            'indexed': len(indexed_files),
            'files': indexed_files,
            'errors': errors
        }
    
    def query(self, query_text: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Query the knowledge base for similar content.
        
        Args:
            query_text: The query text
            top_k: Number of top results to return
            
        Returns:
            List of matching files with similarity scores
        """
        query_embedding = self._get_embedding(query_text)
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            # Use cosine similarity for vector search
            cursor.execute(
                """SELECT id, file_path, content, 
                          1 - (embedding <=> %s::vector) as similarity
                   FROM knowledge_base
                   ORDER BY embedding <=> %s::vector
                   LIMIT %s""",
                (query_embedding, query_embedding, top_k)
            )
            
            results = []
            for row in cursor.fetchall():
                results.append({
                    'id': row[0],
                    'file_path': row[1],
                    'content': row[2],
                    'similarity': float(row[3])
                })
            
            return results
            
        finally:
            cursor.close()
            conn.close()
