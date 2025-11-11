#!/bin/bash
# Test script for Aurea Orchestrator

echo "🧪 Testing Aurea Orchestrator..."
echo ""

# Check if the service is running
echo "1. Checking service health..."
response=$(curl -s http://localhost:8000/health)
if [ $? -eq 0 ]; then
    echo "✅ Service is healthy: $response"
else
    echo "❌ Service is not responding"
    exit 1
fi
echo ""

# Test creating tasks
echo "2. Creating test tasks..."
for i in {1..5}; do
    if [ $((i % 2)) -eq 0 ]; then
        model="gpt-4"
    else
        model="gpt-3.5-turbo"
    fi
    
    echo "   Creating task-$i with model $model..."
    curl -s -X POST http://localhost:8000/tasks \
        -H "Content-Type: application/json" \
        -d "{
            \"id\": \"task-$i\",
            \"description\": \"Test task number $i\",
            \"llm_model\": \"$model\",
            \"max_tokens\": 500
        }" > /dev/null
    
    if [ $? -eq 0 ]; then
        echo "   ✅ Task-$i created successfully"
    else
        echo "   ❌ Failed to create task-$i"
    fi
done
echo ""

# Get metrics summary
echo "3. Checking metrics summary..."
curl -s http://localhost:8000/metrics/summary | python -m json.tool
echo ""

# Check Prometheus metrics
echo "4. Checking Prometheus metrics endpoint..."
metrics_count=$(curl -s http://localhost:8000/metrics | grep -c "^aurea_")
echo "✅ Found $metrics_count Aurea metrics"
echo ""

# List all tasks
echo "5. Listing all tasks..."
curl -s http://localhost:8000/tasks | python -m json.tool | head -20
echo ""

echo "✅ All tests completed!"
echo ""
echo "📊 Access points:"
echo "   - Orchestrator API: http://localhost:8000"
echo "   - API Docs: http://localhost:8000/docs"
echo "   - Metrics: http://localhost:8000/metrics"
echo "   - Prometheus: http://localhost:9090"
echo "   - Grafana: http://localhost:3000 (admin/admin)"
