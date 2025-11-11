# Aurea Orchestrator

**Automated Unified Reasoning &amp; Execution Agents**

A meta-learning system for intelligent model routing with feedback collection, pattern analysis, and continuous improvement.

## Features

- 🎯 **Intelligent Model Routing**: Automatically routes requests to the most appropriate AI model based on learned heuristics
- 📊 **Meta-Learning Loop**: Continuously improves through feedback collection and pattern analysis
- 🔄 **Automatic Retraining**: Updates routing heuristics based on success/failure patterns
- 📈 **Performance Visualization**: Interactive charts showing accuracy improvements over time
- 🔌 **RESTful API**: Easy-to-use endpoints for routing, feedback, and retraining

## Architecture

The system consists of several key components:

1. **Model Router** (`router.py`): Core routing logic with feature extraction and heuristic-based model selection
2. **Database** (`database.py`): SQLite-based storage for feedback and performance metrics
3. **Visualization** (`visualization.py`): Chart generation for performance tracking
4. **API Server** (`main.py`): FastAPI application exposing all functionality

## Installation

```bash
# Clone the repository
git clone https://github.com/andres20980/aurea-orchestrator.git
cd aurea-orchestrator

# Install dependencies
pip install -r requirements.txt

# Install development dependencies (for testing)
pip install -r requirements-dev.txt
```

## Quick Start

### Start the API Server

```bash
python main.py
```

The server will start on `http://localhost:8000`. Visit the interactive API documentation at `http://localhost:8000/docs`.

### Basic Usage

#### 1. Route a Request

```bash
curl -X POST "http://localhost:8000/router/route" \
  -H "Content-Type: application/json" \
  -d '{"input_text": "Implement a complex database algorithm"}'
```

Response:
```json
{
  "selected_model": "gpt-4",
  "confidence_score": 0.782,
  "features": {
    "length": 0.05,
    "complexity": 0.45,
    "technical": 0.6,
    "creative": 0.0
  },
  "available_models": ["gpt-4", "gpt-3.5-turbo", "claude-3", "llama-2"],
  "router_version": 1
}
```

#### 2. Submit Feedback

```bash
curl -X POST "http://localhost:8000/router/feedback" \
  -H "Content-Type: application/json" \
  -d '{
    "input_text": "Implement a complex database algorithm",
    "selected_model": "gpt-4",
    "success": true,
    "execution_time": 2.3,
    "confidence_score": 0.782
  }'
```

#### 3. Retrain the Router

After collecting sufficient feedback (minimum 10 records), retrain the router:

```bash
curl -X POST "http://localhost:8000/router/retrain"
```

Response:
```json
{
  "status": "success",
  "metrics": {
    "old_accuracy": 75.5,
    "accuracy_gain_percent": 5.2,
    "records_processed": 45,
    "new_version": 2
  },
  "message": "Router retrained successfully. Version upgraded to 2."
}
```

#### 4. View Performance Metrics

```bash
curl "http://localhost:8000/router/metrics"
```

#### 5. Visualize Performance

Open in your browser:
```
http://localhost:8000/router/visualize
```

This displays interactive charts showing:
- Accuracy improvement over time
- Total vs successful predictions
- Performance statistics

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | API information and available endpoints |
| `/router/route` | POST | Route input to appropriate model |
| `/router/feedback` | POST | Submit feedback for routing decision |
| `/router/retrain` | POST | Retrain router heuristic |
| `/router/metrics` | GET | Get performance metrics |
| `/router/patterns` | GET | Analyze success/fail patterns |
| `/router/visualize` | GET | View performance visualizations |
| `/health` | GET | Health check |

## How It Works

### Feature Extraction

The router extracts four key features from input text:

1. **Length**: Normalized text length (words)
2. **Complexity**: Based on word length and punctuation density
3. **Technical**: Presence of technical keywords
4. **Creative**: Presence of creative keywords

### Heuristic-Based Routing

Each model has weights for each feature. The router calculates a score for each model based on the input features and selects the model with the highest score.

### Meta-Learning Loop

1. **Feedback Collection**: Store results of routing decisions (success/failure)
2. **Pattern Analysis**: Correlate features with success rates for each model
3. **Weight Updates**: Adjust heuristic weights based on performance patterns
4. **Version Tracking**: Increment router version after each retraining

### Continuous Improvement

The system learns which models perform best for different types of inputs and adjusts routing accordingly. Accuracy metrics are tracked over time to measure improvement.

## Testing

Run the test suite:

```bash
pytest test_router.py -v
```

Tests cover:
- Database operations
- Feature extraction
- Routing logic
- Pattern analysis
- Retraining functionality
- Full integration workflow

## Development

The project structure:

```
aurea-orchestrator/
├── main.py              # FastAPI application
├── router.py            # Model router with meta-learning
├── database.py          # Database models and operations
├── visualization.py     # Chart generation
├── test_router.py       # Test suite
├── requirements.txt     # Production dependencies
├── requirements-dev.txt # Development dependencies
├── .gitignore          # Git ignore rules
└── README.md           # This file
```

## Example Workflow

```python
from database import Database
from router import ModelRouter

# Initialize
db = Database()
router = ModelRouter(db)

# Route requests
model, confidence, features = router.route("Write a creative story")
print(f"Selected: {model} (confidence: {confidence:.2f})")

# Add feedback
db.add_feedback(
    input_text="Write a creative story",
    selected_model=model,
    success=True,
    confidence_score=confidence,
    features=features
)

# After collecting enough feedback, retrain
result = router.retrain()
print(f"Retraining result: {result}")

# View metrics
metrics = db.get_latest_metrics()
print(f"Current accuracy: {metrics.accuracy * 100:.1f}%")
```

## Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues.

## License

MIT License

## Authors

Aurea Orchestrator Team
