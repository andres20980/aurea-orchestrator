"""Database management for aurea-orchestrator."""
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from config import settings


def init_db():
    """Initialize database with pgvector extension and create necessary tables."""
    # Connect to PostgreSQL
    conn = psycopg2.connect(settings.database_url)
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cursor = conn.cursor()
    
    try:
        # Enable pgvector extension
        cursor.execute("CREATE EXTENSION IF NOT EXISTS vector;")
        
        # Create knowledge_base table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS knowledge_base (
                id SERIAL PRIMARY KEY,
                file_path TEXT NOT NULL,
                content TEXT NOT NULL,
                embedding vector(1536),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        
        # Create index for vector similarity search
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS knowledge_base_embedding_idx 
            ON knowledge_base 
            USING ivfflat (embedding vector_cosine_ops)
            WITH (lists = 100);
        """)
        
        print("Database initialized successfully!")
        
    except Exception as e:
        print(f"Error initializing database: {e}")
        raise
    finally:
        cursor.close()
        conn.close()


def get_db_connection():
    """Get a database connection."""
    return psycopg2.connect(settings.database_url)


if __name__ == "__main__":
    init_db()
