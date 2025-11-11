"""
Example usage of the aurea-orchestrator monitoring system.
"""
import time
import random
from middleware import monitor_task


# Example 1: Simple task monitoring
@monitor_task(job_id="example_job_1", task_name="text_generation", model_used="gpt-4")
def generate_text(prompt):
    """Simulate text generation."""
    time.sleep(random.uniform(0.5, 1.5))  # Simulate API call
    result = f"Generated response for: {prompt}"
    tokens = random.randint(100, 500)
    return result, tokens


# Example 2: Task returning dict
@monitor_task(job_id="example_job_2", task_name="summarization", model_used="claude-3-sonnet")
def summarize_document(document):
    """Simulate document summarization."""
    time.sleep(random.uniform(0.3, 1.0))
    summary = f"Summary of {len(document)} chars"
    return {
        'summary': summary,
        'tokens': len(document) // 4  # Rough estimate
    }


# Example 3: Custom cost estimation
def custom_cost_estimator(model_name, token_count):
    """Custom cost calculation based on your pricing."""
    pricing_tiers = {
        'premium': 0.05,
        'standard': 0.01,
        'economy': 0.001
    }
    tier = 'standard'  # Could be determined by model_name
    return (token_count / 1000.0) * pricing_tiers[tier]


@monitor_task(
    job_id="example_job_3",
    task_name="custom_processing",
    model_used="custom-model",
    estimate_cost_fn=custom_cost_estimator
)
def process_with_custom_pricing(data):
    """Task with custom cost estimation."""
    time.sleep(0.5)
    result = f"Processed {data}"
    tokens = len(data) * 2
    return result, tokens


# Example 4: Complex workflow
def run_complete_workflow():
    """Run a complete workflow with multiple tasks."""
    job_id = "workflow_example"
    
    # Step 1: Data preparation
    @monitor_task(job_id, "data_prep", "gpt-3.5-turbo")
    def prepare_data(raw_data):
        time.sleep(0.2)
        prepared = f"Prepared: {raw_data}"
        return prepared, 50
    
    # Step 2: Main processing
    @monitor_task(job_id, "main_processing", "gpt-4")
    def process_main(data):
        time.sleep(1.0)
        processed = f"Processed: {data}"
        return processed, 300
    
    # Step 3: Post-processing
    @monitor_task(job_id, "post_processing", "claude-3-haiku")
    def post_process(data):
        time.sleep(0.3)
        final = f"Final: {data}"
        return final, 100
    
    # Execute workflow
    raw = "input data"
    step1 = prepare_data(raw)
    step2 = process_main(step1[0])
    step3 = post_process(step2[0])
    
    return step3


def main():
    """Run examples."""
    print("Running aurea-orchestrator monitoring examples...\n")
    
    # Example 1
    print("Example 1: Text generation")
    result1 = generate_text("Hello, how are you?")
    print(f"Result: {result1[0]}\n")
    
    # Example 2
    print("Example 2: Document summarization")
    result2 = summarize_document("This is a long document that needs to be summarized.")
    print(f"Summary: {result2['summary']}\n")
    
    # Example 3
    print("Example 3: Custom pricing")
    result3 = process_with_custom_pricing("custom data")
    print(f"Result: {result3[0]}\n")
    
    # Example 4
    print("Example 4: Complete workflow")
    final = run_complete_workflow()
    print(f"Workflow complete: {final[0]}\n")
    
    print("\nAll examples completed!")
    print("Check metrics via API:")
    print("  curl http://localhost:4000/metrics/jobs/example_job_1")
    print("  curl http://localhost:4000/metrics/jobs/workflow_example")


if __name__ == "__main__":
    # Make sure the app is running before executing examples
    print("Note: Make sure the Flask app is running (python app.py) before running examples.\n")
    main()
