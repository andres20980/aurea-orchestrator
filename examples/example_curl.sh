#!/bin/bash
# Example: Submit code executions using curl

API_URL="http://localhost:8000"

echo "=== Example 1: Simple Python Hello World ==="
curl -X POST "$API_URL/run" \
  -H "Content-Type: application/json" \
  -d '{
    "code": "print(\"Hello from sandbox!\")",
    "language": "python",
    "timeout": 30
  }' | jq .

echo -e "\n=== Example 2: JavaScript Execution ==="
curl -X POST "$API_URL/run" \
  -H "Content-Type: application/json" \
  -d '{
    "code": "console.log(\"Hello from Node.js!\"); console.log(\"Math.PI =\", Math.PI);",
    "language": "javascript",
    "timeout": 30
  }' | jq .

echo -e "\n=== Example 3: Bash Script ==="
curl -X POST "$API_URL/run" \
  -H "Content-Type: application/json" \
  -d '{
    "code": "echo \"Hello from bash!\"; ls -la; pwd",
    "language": "bash",
    "timeout": 30
  }' | jq .

echo -e "\n=== Example 4: Health Check ==="
curl -X GET "$API_URL/health" | jq .

echo -e "\n=== Example 5: With Additional Files ==="
curl -X POST "$API_URL/run" \
  -H "Content-Type: application/json" \
  -d '{
    "code": "with open(\"data.txt\", \"r\") as f:\n    print(f.read())",
    "language": "python",
    "timeout": 30,
    "readonly": true,
    "files": {
      "data.txt": "This is test data from an additional file!"
    }
  }' | jq .
