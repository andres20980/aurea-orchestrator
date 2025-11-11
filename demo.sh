#!/bin/bash
# Demo script for Aurea Orchestrator Prompt Registry

set -e

echo "========================================="
echo "Aurea Orchestrator - Prompt Registry Demo"
echo "========================================="
echo ""

# Start server in background
echo "Starting server..."
python -m aurea_orchestrator.main > /tmp/demo_server.log 2>&1 &
SERVER_PID=$!
sleep 5

echo "Server started (PID: $SERVER_PID)"
echo ""

# 1. Create prompt template v1
echo "1. Creating prompt template (version 1)..."
curl -s -X POST "http://localhost:8000/prompts/" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "greeting",
    "description": "Friendly greeting template",
    "template_yaml": "system: You are a helpful assistant.\nuser: Hello {{ name }}!"
  }' | python -m json.tool
echo ""

# 2. Create prompt template v2
echo "2. Creating new version of the same template (version 2)..."
curl -s -X POST "http://localhost:8000/prompts/" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "greeting",
    "description": "Updated greeting template",
    "template_yaml": "system: You are a helpful assistant.\nuser: Welcome {{ name }}! How can I help you today?"
  }' | python -m json.tool
echo ""

# 3. List all templates
echo "3. Listing all templates..."
curl -s "http://localhost:8000/prompts/" | python -m json.tool
echo ""

# 4. Get specific version
echo "4. Getting specific version (v1)..."
curl -s "http://localhost:8000/prompts/by-name/greeting?version=1" | python -m json.tool
echo ""

# 5. Get latest version
echo "5. Getting latest version..."
curl -s "http://localhost:8000/prompts/by-name/greeting" | python -m json.tool
echo ""

# 6. Preview template
echo "6. Previewing template with variables..."
curl -s -X POST "http://localhost:8000/prompts/preview" \
  -H "Content-Type: application/json" \
  -d '{
    "template_yaml": "greeting: Hello {{ name }}, your role is {{ role }}!",
    "variables": {"name": "Alice", "role": "Developer"}
  }' | python -m json.tool
echo ""

# 7. Create job with template
echo "7. Creating job with template (automatically records version)..."
curl -s -X POST "http://localhost:8000/jobs/" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "greet_user",
    "prompt_template_id": 1,
    "input_data": {"user": "Alice"}
  }' | python -m json.tool
echo ""

# 8. Create another job with different version
echo "8. Creating job with newer template version..."
curl -s -X POST "http://localhost:8000/jobs/" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "greet_user_v2",
    "prompt_template_id": 2,
    "input_data": {"user": "Bob"}
  }' | python -m json.tool
echo ""

# 9. List jobs
echo "9. Listing all jobs (shows which prompt version was used)..."
curl -s "http://localhost:8000/jobs/" | python -m json.tool
echo ""

# 10. Get specific job
echo "10. Getting specific job details..."
curl -s "http://localhost:8000/jobs/1" | python -m json.tool
echo ""

# Cleanup
echo "Stopping server..."
kill $SERVER_PID
wait $SERVER_PID 2>/dev/null || true

echo ""
echo "Demo completed successfully!"
echo "Database file created: aurea_orchestrator.db"
