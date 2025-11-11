#!/usr/bin/env python3
"""
Demo script showing the complete meta-learning workflow.
"""
import time
from database import Database
from router import ModelRouter


def print_section(title):
    """Print a section header."""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")


def demo_workflow():
    """Demonstrate the complete meta-learning workflow."""
    
    print_section("AUREA ORCHESTRATOR - META-LEARNING DEMO")
    
    # Initialize system
    print("Initializing database and router...")
    db = Database("sqlite:///demo_router.db")
    router = ModelRouter(db)
    print(f"✓ Router initialized (Version {router.version})")
    print(f"✓ Available models: {', '.join(router.available_models)}")
    
    # Test inputs with different characteristics
    test_cases = [
        ("Implement a complex database algorithm with optimization", True),
        ("Write a creative story about space exploration", True),
        ("Create API documentation for authentication system", True),
        ("Design an innovative art installation project", False),
        ("Build a microservices architecture", True),
        ("Compose a poem about nature and seasons", True),
        ("Develop a machine learning model for classification", True),
        ("Brainstorm ideas for a marketing campaign", True),
        ("Implement sorting algorithms in Python", True),
        ("Write a technical specification document", False),
        ("Create a fantasy world with unique characters", True),
        ("Optimize database query performance", True),
        ("Design a user interface for mobile app", True),
        ("Debug complex code with memory leaks", True),
        ("Write imaginative dialogue for characters", True),
    ]
    
    print_section("STEP 1: ROUTING REQUESTS")
    
    routes = []
    for input_text, expected_success in test_cases:
        model, confidence, features = router.route(input_text)
        routes.append((input_text, model, confidence, features, expected_success))
        
        print(f"Input: {input_text[:50]}...")
        print(f"  → Model: {model} (confidence: {confidence:.3f})")
        print(f"  → Features: length={features['length']:.2f}, "
              f"complexity={features['complexity']:.2f}, "
              f"technical={features['technical']:.2f}, "
              f"creative={features['creative']:.2f}")
        print()
    
    print_section("STEP 2: COLLECTING FEEDBACK")
    
    feedback_count = 0
    for input_text, model, confidence, features, success in routes:
        db.add_feedback(
            input_text=input_text,
            selected_model=model,
            success=success,
            confidence_score=confidence,
            features=features
        )
        feedback_count += 1
    
    print(f"✓ Collected {feedback_count} feedback records")
    
    print_section("STEP 3: ANALYZING PATTERNS")
    
    patterns = router.analyze_patterns()
    print(f"Total records: {patterns['total_records']}")
    print(f"Success rate: {patterns['success_rate']*100:.1f}%")
    print(f"Successful predictions: {patterns['successful_records']}")
    print("\nModel Performance:")
    for model, perf in patterns['patterns']['model_performance'].items():
        total = perf['success'] + perf['failure']
        success_rate = (perf['success'] / total * 100) if total > 0 else 0
        print(f"  {model}: {perf['success']}/{total} successful ({success_rate:.1f}%)")
    
    print("\nFeature Correlations:")
    for feature, corr in patterns['patterns']['feature_correlations'].items():
        print(f"  {feature}: avg_success={corr['avg_success']:.3f}, "
              f"avg_failure={corr['avg_failure']:.3f}")
    
    print_section("STEP 4: RETRAINING THE ROUTER")
    
    print("Initiating retraining process...")
    result = router.retrain()
    
    if result['status'] == 'success':
        print("✓ Retraining successful!")
        print(f"  Old accuracy: {result['old_accuracy']*100:.2f}%")
        print(f"  Records processed: {result['records_processed']}")
        print(f"  New version: {result['new_version']}")
        print("\n Updated heuristic weights:")
        for feature, weights in result['updated_weights'].items():
            print(f"  {feature}:")
            for model, weight in weights.items():
                print(f"    {model}: {weight:.3f}")
    else:
        print(f"✗ Retraining failed: {result.get('message', 'Unknown error')}")
    
    print_section("STEP 5: VERIFYING IMPROVEMENTS")
    
    # Test a few new requests
    new_test_cases = [
        "Implement advanced algorithm for data processing",
        "Write creative content for storytelling",
        "Build technical system architecture"
    ]
    
    print("Testing routing with retrained model:\n")
    for input_text in new_test_cases:
        model, confidence, features = router.route(input_text)
        print(f"Input: {input_text}")
        print(f"  → Model: {model} (confidence: {confidence:.3f})")
        print()
    
    print_section("STEP 6: PERFORMANCE METRICS")
    
    metrics = db.get_latest_metrics()
    if metrics:
        print(f"Current accuracy: {metrics.accuracy*100:.1f}%")
        print(f"Total predictions: {metrics.total_predictions}")
        print(f"Successful predictions: {metrics.successful_predictions}")
        print(f"Router version: {metrics.version}")
        print(f"Timestamp: {metrics.timestamp}")
    
    all_metrics = db.get_all_metrics()
    if len(all_metrics) > 1:
        print(f"\nAccuracy history ({len(all_metrics)} versions):")
        for m in all_metrics:
            print(f"  v{m.version}: {m.accuracy*100:.1f}% "
                  f"({m.successful_predictions}/{m.total_predictions})")
    
    print_section("DEMO COMPLETE")
    print("The meta-learning loop has successfully:")
    print("  ✓ Routed requests to appropriate models")
    print("  ✓ Collected feedback on routing decisions")
    print("  ✓ Analyzed success/failure patterns")
    print("  ✓ Retrained the router heuristic")
    print("  ✓ Tracked performance improvements")
    print("\nThe system is now ready to continue learning and improving!")
    print("\nTo visualize results, run the API server and visit:")
    print("  http://localhost:8000/router/visualize")
    
    db.close()


if __name__ == "__main__":
    demo_workflow()
