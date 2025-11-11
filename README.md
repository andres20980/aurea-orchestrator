# aurea-orchestrator
Automated Unified Reasoning & Execution Agents

A Knowledge Base system for storing and querying embedded project files using pgvector in PostgreSQL and LiteLLM embeddings.

## Features

- **Vector-based Knowledge Base**: Store and search project files using semantic embeddings
- **pgvector Integration**: Efficient vector similarity search in PostgreSQL
- **LiteLLM Embeddings**: Support for multiple embedding models via LiteLLM
- **FastAPI REST API**: Easy-to-use endpoints for indexing and querying
- **File Indexing**: Index individual files or entire directories
- **Semantic Search**: Find relevant code and documentation using natural language queries

## Prerequisites

- Python 3.8+
- PostgreSQL 12+ with pgvector extension
- OpenAI API key (or other LiteLLM-supported provider)

## Setup

### 1. Install PostgreSQL and pgvector

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install postgresql postgresql-contrib
```

**macOS:**
```bash
brew install postgresql
```

**Install pgvector extension:**
```bash
# Clone and install pgvector
git clone --branch v0.5.1 https://github.com/pgvector/pgvector.git
cd pgvector
make
sudo make install
```

### 2. Create Database

```bash
# Connect to PostgreSQL
sudo -u postgres psql

# Create database and user
CREATE DATABASE aurea_db;
CREATE USER aurea_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE aurea_db TO aurea_user;
\q
```

### 3. Install Python Dependencies

```bash
# Clone the repository
git clone https://github.com/andres20980/aurea-orchestrator.git
cd aurea-orchestrator

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 4. Configure Environment

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env with your configuration
# Update DATABASE_URL with your PostgreSQL credentials
# Add your OPENAI_API_KEY
```

Example `.env`:
```
DATABASE_URL=postgresql://aurea_user:your_password@localhost:5432/aurea_db
OPENAI_API_KEY=sk-your-openai-api-key-here
EMBEDDING_MODEL=text-embedding-3-small
```

### 5. Initialize Database

```bash
# Run the database initialization script
python database.py
```

This will create the necessary tables and enable the pgvector extension.

## Usage

### Start the API Server

```bash
python main.py
```

The API will be available at `http://localhost:8000`

### API Documentation

Interactive API documentation is available at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### Sample Queries

#### 1. Index a Single File

```bash
curl -X POST "http://localhost:8000/kb/index" \
  -H "Content-Type: application/json" \
  -d '{
    "file_path": "/path/to/your/file.py",
    "content": "def hello_world():\n    print(\"Hello, World!\")"
  }'
```

**Response:**
```json
{
  "status": "success",
  "message": "File indexed successfully",
  "id": 1,
  "file_path": "/path/to/your/file.py"
}
```

#### 2. Index a Directory

```bash
curl -X POST "http://localhost:8000/kb/index" \
  -H "Content-Type: application/json" \
  -d '{
    "directory_path": "/path/to/your/project",
    "extensions": [".py", ".md", ".js"]
  }'
```

**Response:**
```json
{
  "status": "success",
  "message": "Directory indexed successfully",
  "indexed": 15,
  "files": [
    {"id": 1, "path": "/path/to/your/project/main.py"},
    {"id": 2, "path": "/path/to/your/project/README.md"}
  ],
  "errors": []
}
```

#### 3. Query the Knowledge Base

```bash
curl -X POST "http://localhost:8000/kb/query" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "How do I initialize the database?",
    "top_k": 5
  }'
```

**Response:**
```json
[
  {
    "id": 3,
    "file_path": "/path/to/project/database.py",
    "content": "def init_db():\n    ...",
    "similarity": 0.89
  },
  {
    "id": 7,
    "file_path": "/path/to/project/README.md",
    "content": "## Database Setup...",
    "similarity": 0.76
  }
]
```

### Python Usage Example

```python
from kb import KnowledgeBase

# Initialize the knowledge base
kb = KnowledgeBase()

# Index a file
file_id = kb.index_file(
    file_path="example.py",
    content="def example():\n    return 'Hello'"
)

# Index a directory
result = kb.index_directory(
    directory_path="./src",
    extensions=[".py", ".md"]
)
print(f"Indexed {result['indexed']} files")

# Query for similar content
results = kb.query(
    query_text="function that returns a greeting",
    top_k=3
)

for result in results:
    print(f"File: {result['file_path']}")
    print(f"Similarity: {result['similarity']:.2f}")
    print(f"Content: {result['content'][:100]}...")
```

## Architecture

### Components

1. **kb.py**: Core Knowledge Base module
   - Embedding generation using LiteLLM
   - File indexing and storage
   - Semantic search functionality

2. **database.py**: Database management
   - PostgreSQL connection handling
   - pgvector extension initialization
   - Table schema creation

3. **main.py**: FastAPI application
   - REST API endpoints
   - Request/response models
   - Error handling

4. **config.py**: Configuration management
   - Environment variable loading
   - Settings validation

### Database Schema

```sql
CREATE TABLE knowledge_base (
    id SERIAL PRIMARY KEY,
    file_path TEXT NOT NULL,
    content TEXT NOT NULL,
    embedding vector(1536),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX knowledge_base_embedding_idx 
ON knowledge_base 
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);
```

## API Endpoints

### GET /
Returns API information and available endpoints.

### POST /kb/index
Index files or directories into the knowledge base.

**Request Body (File):**
```json
{
  "file_path": "string",
  "content": "string"
}
```

**Request Body (Directory):**
```json
{
  "directory_path": "string",
  "extensions": ["string"]  // optional
}
```

### POST /kb/query
Query the knowledge base for similar content.

**Request Body:**
```json
{
  "query": "string",
  "top_k": 5  // optional, default: 5
}
```

**Response:**
```json
[
  {
    "id": 0,
    "file_path": "string",
    "content": "string",
    "similarity": 0.0
  }
]
```

## Advanced Configuration

### Using Different Embedding Models

You can use any embedding model supported by LiteLLM:

```bash
# OpenAI
EMBEDDING_MODEL=text-embedding-3-small

# OpenAI (larger model)
EMBEDDING_MODEL=text-embedding-3-large

# Cohere
EMBEDDING_MODEL=embed-english-v3.0

# Vertex AI
EMBEDDING_MODEL=textembedding-gecko@001
```

### Adjusting Vector Index Parameters

For larger datasets, you may want to adjust the IVFFlat index parameters:

```sql
-- Increase the number of lists for better accuracy with large datasets
CREATE INDEX knowledge_base_embedding_idx 
ON knowledge_base 
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 1000);
```

## Troubleshooting

### pgvector Extension Not Found

If you get an error about the vector extension:
```bash
ERROR: extension "vector" is not available
```

Make sure pgvector is properly installed:
```bash
cd pgvector
sudo make install
# Then reconnect to your database and try again
```

### Connection Issues

If you can't connect to PostgreSQL:
1. Check that PostgreSQL is running: `sudo systemctl status postgresql`
2. Verify your DATABASE_URL in `.env`
3. Ensure the user has proper permissions

### API Key Issues

If you get authentication errors:
1. Verify your OPENAI_API_KEY is set in `.env`
2. Check that the key is valid and has sufficient credits
3. Ensure LiteLLM supports your chosen embedding model

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License.
