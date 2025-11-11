# Configuration Guide

This guide explains how to configure and customize the Aurea Orchestrator.

## Configuration Files

### Router Weights (`router_weights.json`)

The router automatically creates and updates this file. Example structure:

```json
{
  "weights": {
    "code_generation": {
      "claude": 0.75,
      "deepseek": 0.15,
      "gpt": 0.10
    },
    "summarization": {
      "claude": 0.60,
      "deepseek": 0.20,
      "gpt": 0.20
    }
  },
  "last_updated": "2025-11-11T08:00:00.000000"
}
```

### Evaluation Results (`evaluation_results/comparisons.jsonl`)

Stores evaluation results in JSONL format. Each line is a JSON object representing one comparison:

```json
{"task_id": "task_1", "task_type": "code_generation", "prompt": "...", "results": {...}, "winner": "claude", "timestamp": "..."}
```

## Custom Scoring Functions

Create custom scoring functions for domain-specific evaluation:

```python
def code_quality_scorer(prompt: str, output: str) -> float:
    """Score code outputs based on quality metrics"""
    score = 0.0
    
    # Check for documentation
    if '"""' in output or "'''" in output:
        score += 0.2
    
    # Check for error handling
    if 'try' in output and 'except' in output:
        score += 0.2
    
    # Check for type hints
    if '->' in output:
        score += 0.2
    
    # Length-based component
    score += min(len(output) / 1000, 0.4)
    
    return min(score, 1.0)

# Use in evaluation
comparison = runner.run_evaluation(
    task_id="code_task_1",
    task_type=TaskType.CODE_GENERATION,
    prompt="Write a well-documented function",
    scorer=code_quality_scorer
)
```

## Model Client Integration

### OpenAI GPT

```python
from openai import OpenAI

def gpt_client(prompt: str) -> str:
    client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

runner.register_model_client(ModelType.GPT, gpt_client)
```

### Anthropic Claude

```python
import anthropic

def claude_client(prompt: str) -> str:
    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    message = client.messages.create(
        model="claude-3-opus-20240229",
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}]
    )
    return message.content[0].text

runner.register_model_client(ModelType.CLAUDE, claude_client)
```

### DeepSeek

```python
from openai import OpenAI

def deepseek_client(prompt: str) -> str:
    client = OpenAI(
        api_key=os.environ["DEEPSEEK_API_KEY"],
        base_url="https://api.deepseek.com"
    )
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

runner.register_model_client(ModelType.DEEPSEEK, deepseek_client)
```

## Advanced Configuration

### Minimum Evaluations for Router Updates

Control when the router updates weights:

```python
router = ModelRouter(auto_update=True)

# Update weights only if at least 10 evaluations exist
router.update_weights_from_performance(min_evaluations=10)
```

### Custom Task Types

Add new task types by editing `aurea/models.py`:

```python
class TaskType(str, Enum):
    CODE_GENERATION = "code_generation"
    SUMMARIZATION = "summarization"
    QUESTION_ANSWERING = "question_answering"
    TRANSLATION = "translation"
    REASONING = "reasoning"
    # Add your custom types
    DATA_ANALYSIS = "data_analysis"
    IMAGE_DESCRIPTION = "image_description"
```

### Batch Processing

Process multiple tasks efficiently:

```python
tasks = [
    {
        "task_id": f"batch_{i}",
        "task_type": "code_generation",
        "prompt": f"Task {i} prompt"
    }
    for i in range(100)
]

results = runner.run_batch_evaluations(tasks, scorer=custom_scorer)
```

## Environment Variables

Store API keys in environment variables:

```bash
export OPENAI_API_KEY="your-openai-key"
export ANTHROPIC_API_KEY="your-anthropic-key"
export DEEPSEEK_API_KEY="your-deepseek-key"
```

Or use a `.env` file (requires `python-dotenv`):

```python
from dotenv import load_dotenv
load_dotenv()
```

## Performance Tuning

### Storage Location

Change where data is stored:

```python
tracker = EvaluationTracker(storage_path="/path/to/results")
router = ModelRouter(weights_path="/path/to/weights.json")
```

### Disable Auto-Update

For manual control over weight updates:

```python
router = ModelRouter(auto_update=False)

# Manually trigger updates when desired
router.update_weights_from_performance()
```

## Best Practices

1. **Start with sufficient evaluations**: Run at least 10-20 evaluations per task type before relying on router weights
2. **Use appropriate scorers**: Customize scoring functions for your specific domain
3. **Monitor win rates**: Regularly check win rates to understand model performance
4. **Version control weights**: Track `router_weights.json` changes to see how routing evolves
5. **Test with mock clients**: Use mock clients during development to avoid API costs
