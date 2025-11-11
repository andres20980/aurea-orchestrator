"""Example usage of the Aurea Orchestrator"""

from aurea.models import ModelType, TaskType
from aurea.evaluator import EvaluationRunner
from aurea.router import ModelRouter


def mock_claude_client(prompt: str) -> str:
    """Mock Claude API client"""
    return f"Claude response: {prompt[:100]}... [detailed analysis]"


def mock_deepseek_client(prompt: str) -> str:
    """Mock DeepSeek API client"""
    return f"DeepSeek response: {prompt[:80]}... [concise answer]"


def mock_gpt_client(prompt: str) -> str:
    """Mock GPT API client"""
    return f"GPT response: {prompt[:90]}... [comprehensive explanation]"


def custom_scorer(prompt: str, output: str) -> float:
    """Custom scoring function"""
    # Simple heuristic: score based on output length and keywords
    score = min(len(output) / 500, 1.0) * 0.5
    
    # Bonus for detailed responses
    if "detailed" in output.lower() or "comprehensive" in output.lower():
        score += 0.3
    if "analysis" in output.lower():
        score += 0.2
    
    return min(score, 1.0)


def main():
    """Run example evaluation and routing"""
    
    print("=== Aurea Orchestrator Demo ===\n")
    
    # Initialize evaluation runner
    runner = EvaluationRunner()
    
    # Register mock model clients
    runner.register_model_client(ModelType.CLAUDE, mock_claude_client)
    runner.register_model_client(ModelType.DEEPSEEK, mock_deepseek_client)
    runner.register_model_client(ModelType.GPT, mock_gpt_client)
    
    # Define evaluation tasks
    tasks = [
        {
            "task_id": "task_1",
            "task_type": "code_generation",
            "prompt": "Write a Python function to calculate fibonacci numbers"
        },
        {
            "task_id": "task_2",
            "task_type": "code_generation",
            "prompt": "Implement a binary search algorithm in Python"
        },
        {
            "task_id": "task_3",
            "task_type": "summarization",
            "prompt": "Summarize the key features of machine learning"
        },
        {
            "task_id": "task_4",
            "task_type": "question_answering",
            "prompt": "What is the difference between supervised and unsupervised learning?"
        },
        {
            "task_id": "task_5",
            "task_type": "code_generation",
            "prompt": "Create a REST API endpoint using Flask"
        },
    ]
    
    # Run batch evaluations
    print("Running evaluations...")
    comparisons = runner.run_batch_evaluations(tasks, scorer=custom_scorer)
    
    print(f"\nCompleted {len(comparisons)} evaluations\n")
    
    # Display results
    for comp in comparisons:
        print(f"Task: {comp.task_id} ({comp.task_type.value})")
        print(f"  Winner: {comp.winner.value}")
        for model, result in comp.results.items():
            print(f"  {model.value}: score={result.score:.3f}")
        print()
    
    # Show win rates
    print("=== Win Rates by Task Type ===\n")
    win_rates = runner.get_win_rates()
    for task_type, stats in win_rates.items():
        if stats['total_evaluations'] > 0:
            print(f"{task_type}:")
            print(f"  Total evaluations: {stats['total_evaluations']}")
            for model, rate in stats['win_rates'].items():
                print(f"  {model}: {rate:.1%}")
            print()
    
    # Initialize router with automatic weight updates
    print("\n=== Model Router ===\n")
    router = ModelRouter(tracker=runner.tracker, auto_update=True)
    router.register_model_client(ModelType.CLAUDE, mock_claude_client)
    router.register_model_client(ModelType.DEEPSEEK, mock_deepseek_client)
    router.register_model_client(ModelType.GPT, mock_gpt_client)
    
    # Update weights from performance
    router.update_weights_from_performance(min_evaluations=1)
    
    # Show current weights
    weights = router.get_current_weights()
    print("Current Router Weights:")
    for task_type, model_weights in weights['weights'].items():
        print(f"\n{task_type}:")
        for model, weight in sorted(model_weights.items(), key=lambda x: x[1], reverse=True):
            print(f"  {model}: {weight:.3f}")
    
    print(f"\nLast updated: {weights['last_updated']}")
    
    # Test routing
    print("\n=== Testing Routing ===\n")
    for task_type in [TaskType.CODE_GENERATION, TaskType.SUMMARIZATION]:
        best_model = router.get_model_for_task(task_type)
        print(f"Best model for {task_type.value}: {best_model.value}")
    
    print("\n=== Demo Complete ===")


if __name__ == "__main__":
    main()
