#!/usr/bin/env python
"""
Example script demonstrating the Knowledge Base module.
This script shows how to use kb.py to index and query files.
"""

import os
from kb import KnowledgeBase


def demo_knowledge_base():
    """Demonstrate the Knowledge Base functionality."""
    print("=" * 60)
    print("Knowledge Base Demo")
    print("=" * 60)
    
    # Initialize the knowledge base
    print("\n1. Initializing Knowledge Base...")
    kb = KnowledgeBase()
    print("   ✓ Knowledge Base initialized")
    
    # Create some example files
    print("\n2. Creating example files...")
    os.makedirs("/tmp/kb_demo", exist_ok=True)
    
    example_files = {
        "/tmp/kb_demo/hello.py": """
def greet(name):
    \"\"\"Greet someone by name.\"\"\"
    return f"Hello, {name}!"

def main():
    print(greet("World"))

if __name__ == "__main__":
    main()
""",
        "/tmp/kb_demo/math_utils.py": """
def add(a, b):
    \"\"\"Add two numbers together.\"\"\"
    return a + b

def multiply(a, b):
    \"\"\"Multiply two numbers.\"\"\"
    return a * b

def factorial(n):
    \"\"\"Calculate the factorial of n.\"\"\"
    if n <= 1:
        return 1
    return n * factorial(n - 1)
""",
        "/tmp/kb_demo/README.md": """
# Example Project

This is a demo project to show the Knowledge Base functionality.

## Features
- Greeting functions
- Math utilities
- Factorial calculation
"""
    }
    
    for file_path, content in example_files.items():
        with open(file_path, 'w') as f:
            f.write(content)
        print(f"   ✓ Created {file_path}")
    
    # Index the files
    print("\n3. Indexing files...")
    print("   Note: This requires a database connection and API key")
    print("   Set DATABASE_URL and OPENAI_API_KEY in .env file")
    
    try:
        result = kb.index_directory("/tmp/kb_demo", extensions=['.py', '.md'])
        print(f"   ✓ Indexed {result['indexed']} files")
        for file_info in result['files']:
            print(f"     - {file_info['path']} (ID: {file_info['id']})")
        
        if result['errors']:
            print(f"   ⚠ {len(result['errors'])} errors occurred")
            for error in result['errors']:
                print(f"     - {error['path']}: {error['error']}")
        
        # Query the knowledge base
        print("\n4. Querying the knowledge base...")
        queries = [
            "function that greets someone",
            "how to calculate factorial",
            "mathematical operations"
        ]
        
        for query in queries:
            print(f"\n   Query: '{query}'")
            results = kb.query(query, top_k=2)
            for i, result in enumerate(results, 1):
                print(f"   {i}. {result['file_path']} (similarity: {result['similarity']:.2f})")
                preview = result['content'][:100].replace('\n', ' ')
                print(f"      Preview: {preview}...")
        
        print("\n" + "=" * 60)
        print("Demo completed successfully!")
        print("=" * 60)
        
    except Exception as e:
        print(f"   ✗ Error: {e}")
        print("\n   Make sure you have:")
        print("   1. PostgreSQL running with pgvector extension")
        print("   2. Database initialized (run: python database.py)")
        print("   3. .env file with DATABASE_URL and OPENAI_API_KEY")
        print("\n" + "=" * 60)
        print("Demo stopped - configuration needed")
        print("=" * 60)


if __name__ == "__main__":
    demo_knowledge_base()
