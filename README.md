# Aurea Orchestrator

**Automated Unified Reasoning & Execution Agents**

A Python framework for comparing multiple AI models (Claude, DeepSeek, GPT) through evaluation jobs, tracking win-rates per task type, and automatically updating router weights to select the best performing model for each task.

## Features

- 🔄 **Evaluation Jobs**: Run comparative evaluations across multiple models
- 📊 **Win-Rate Tracking**: Track model performance by task type
- 🎯 **Automatic Router Updates**: Weights automatically update based on performance
- 💾 **Persistent Storage**: Evaluation results and weights persist across sessions
- 🧪 **Extensible**: Easy to add custom models, task types, and scoring functions

## Quick Start

### Installation

```bash
pip install -r requirements.txt
```

### Basic Usage

```python
from aurea.models import ModelType, TaskType
from aurea.evaluator import EvaluationRunner
from aurea.router import ModelRouter

# Initialize evaluation runner
runner = EvaluationRunner()

# Register model clients (mock or real API clients)
runner.register_model_client(ModelType.CLAUDE, your_claude_client)
runner.register_model_client(ModelType.DEEPSEEK, your_deepseek_client)
runner.register_model_client(ModelType.GPT, your_gpt_client)

# Run evaluation
comparison = runner.run_evaluation(
    task_id="task_1",
    task_type=TaskType.CODE_GENERATION,
    prompt="Write a Python function to sort a list"
)

# Check win rates
win_rates = runner.get_win_rates()
print(win_rates)

# Use router to automatically select best model
router = ModelRouter(tracker=runner.tracker, auto_update=True)
router.register_model_client(ModelType.CLAUDE, your_claude_client)
router.register_model_client(ModelType.DEEPSEEK, your_deepseek_client)
router.register_model_client(ModelType.GPT, your_gpt_client)

# Route task to best model
result = router.route(TaskType.CODE_GENERATION, "Write a binary search")
```

## Architecture

### Components

1. **Models** (`aurea/models.py`)
   - `ModelType`: Enum for supported models (Claude, DeepSeek, GPT)
   - `TaskType`: Enum for task categories
   - `EvaluationResult`: Individual model output and score
   - `ModelComparison`: Comparison results across models
   - `RouterWeights`: Model selection weights per task type

2. **Evaluation Tracker** (`aurea/tracker.py`)
   - Stores evaluation results persistently
   - Computes win rates by task type
   - Identifies best performing models

3. **Evaluation Runner** (`aurea/evaluator.py`)
   - Executes evaluation jobs
   - Compares model outputs using scoring functions
   - Supports batch evaluations

4. **Model Router** (`aurea/router.py`)
   - Routes tasks to best performing models
   - Automatically updates weights from performance data
   - Persists routing decisions

## Task Types

The system supports the following task types:
- `CODE_GENERATION`: Code writing tasks
- `SUMMARIZATION`: Text summarization
- `QUESTION_ANSWERING`: Q&A tasks
- `TRANSLATION`: Language translation
- `REASONING`: Logical reasoning tasks

## Example

Run the included example:

```bash
python example.py
```

This demonstrates:
- Running evaluations across multiple models
- Tracking win rates by task type
- Automatic router weight updates
- Model selection based on performance

## Testing

Run the test suite:

```bash
python run_tests.py
```

Or run individual test files:

```bash
PYTHONPATH=. python tests/test_evaluator.py
PYTHONPATH=. python tests/test_router.py
```

## Project Structure

```
aurea-orchestrator/
├── aurea/
│   ├── __init__.py
│   ├── models.py         # Data models
│   ├── tracker.py        # Evaluation tracking
│   ├── evaluator.py      # Evaluation jobs
│   └── router.py         # Model routing
├── tests/
│   ├── test_evaluator.py
│   └── test_router.py
├── example.py            # Usage example
├── requirements.txt
├── setup.py
└── README.md
```

## Data Storage

- **Evaluation Results**: Stored in `evaluation_results/comparisons.jsonl` (JSONL format)
- **Router Weights**: Stored in `router_weights.json` (JSON format)

## Extending

### Adding Custom Scorers

```python
def custom_scorer(prompt: str, output: str) -> float:
    """Returns a score between 0.0 and 1.0"""
    # Your scoring logic here
    return score

runner.run_evaluation(
    task_id="custom",
    task_type=TaskType.CODE_GENERATION,
    prompt="Your prompt",
    scorer=custom_scorer
)
```

### Adding New Task Types

Edit `aurea/models.py` to add new task types to the `TaskType` enum.

### Integration with Real APIs

Replace mock clients with real API clients:

```python
import anthropic

def claude_client(prompt: str) -> str:
    client = anthropic.Anthropic(api_key="your-key")
    message = client.messages.create(
        model="claude-3-opus-20240229",
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}]
    )
    return message.content[0].text

runner.register_model_client(ModelType.CLAUDE, claude_client)
```

## License

MIT License

## Additional Documentation

- [Configuration Guide](CONFIGURATION.md) - Detailed configuration and customization options
