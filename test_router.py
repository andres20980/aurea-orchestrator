"""
Tests for the meta-learning router system.
"""
import pytest
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import Database, ReviewFeedback, RouterMetrics
from router import ModelRouter
from sqlalchemy import create_engine


class TestDatabase:
    """Test database functionality."""
    
    def test_create_database(self):
        """Test database creation."""
        db = Database("sqlite:///:memory:")
        assert db.session is not None
        db.close()
    
    def test_add_feedback(self):
        """Test adding feedback."""
        db = Database("sqlite:///:memory:")
        feedback = db.add_feedback(
            input_text="Test input",
            selected_model="gpt-4",
            success=True,
            execution_time=1.5,
            confidence_score=0.9,
            features={'length': 0.5, 'complexity': 0.3}
        )
        assert feedback.id is not None
        assert feedback.selected_model == "gpt-4"
        assert feedback.success == True
        db.close()
    
    def test_get_feedback(self):
        """Test retrieving feedback."""
        db = Database("sqlite:///:memory:")
        db.add_feedback("Test 1", "gpt-4", True)
        db.add_feedback("Test 2", "claude-3", False)
        
        all_feedback = db.get_all_feedback()
        assert len(all_feedback) == 2
        
        gpt4_feedback = db.get_feedback_by_model("gpt-4")
        assert len(gpt4_feedback) == 1
        db.close()
    
    def test_add_metrics(self):
        """Test adding metrics."""
        db = Database("sqlite:///:memory:")
        metrics = db.add_metrics(
            accuracy=0.85,
            total_predictions=100,
            successful_predictions=85,
            version=1
        )
        assert metrics.id is not None
        assert metrics.accuracy == 0.85
        db.close()


class TestModelRouter:
    """Test model router functionality."""
    
    def test_router_initialization(self):
        """Test router initialization."""
        db = Database("sqlite:///:memory:")
        router = ModelRouter(db)
        assert len(router.available_models) > 0
        assert router.version == 1
        db.close()
    
    def test_extract_features(self):
        """Test feature extraction."""
        db = Database("sqlite:///:memory:")
        router = ModelRouter(db)
        
        features = router.extract_features("This is a simple test")
        assert 'length' in features
        assert 'complexity' in features
        assert 'technical' in features
        assert 'creative' in features
        assert 0 <= features['length'] <= 1
        db.close()
    
    def test_technical_detection(self):
        """Test technical content detection."""
        db = Database("sqlite:///:memory:")
        router = ModelRouter(db)
        
        technical_text = "Implement a database API with algorithm optimization"
        features = router.extract_features(technical_text)
        assert features['technical'] > 0
        db.close()
    
    def test_creative_detection(self):
        """Test creative content detection."""
        db = Database("sqlite:///:memory:")
        router = ModelRouter(db)
        
        creative_text = "Write a creative story with imaginative ideas"
        features = router.extract_features(creative_text)
        assert features['creative'] > 0
        db.close()
    
    def test_route(self):
        """Test routing functionality."""
        db = Database("sqlite:///:memory:")
        router = ModelRouter(db)
        
        model, confidence, features = router.route("Test input for routing")
        assert model in router.available_models
        assert 0 <= confidence <= 1
        assert isinstance(features, dict)
        db.close()
    
    def test_analyze_patterns_empty(self):
        """Test pattern analysis with no data."""
        db = Database("sqlite:///:memory:")
        router = ModelRouter(db)
        
        patterns = router.analyze_patterns()
        assert patterns['total_records'] == 0
        assert patterns['success_rate'] == 0.0
        db.close()
    
    def test_analyze_patterns_with_data(self):
        """Test pattern analysis with data."""
        db = Database("sqlite:///:memory:")
        router = ModelRouter(db)
        
        # Add some feedback
        db.add_feedback("Test 1", "gpt-4", True, features={'length': 0.5})
        db.add_feedback("Test 2", "gpt-4", True, features={'length': 0.6})
        db.add_feedback("Test 3", "claude-3", False, features={'length': 0.3})
        
        patterns = router.analyze_patterns()
        assert patterns['total_records'] == 3
        assert patterns['successful_records'] == 2
        assert patterns['success_rate'] > 0
        assert 'model_performance' in patterns['patterns']
        db.close()
    
    def test_retrain_insufficient_data(self):
        """Test retraining with insufficient data."""
        db = Database("sqlite:///:memory:")
        router = ModelRouter(db)
        
        # Add only a few feedback records
        for i in range(5):
            db.add_feedback(f"Test {i}", "gpt-4", True)
        
        result = router.retrain()
        assert result['status'] == 'insufficient_data'
        db.close()
    
    def test_retrain_success(self):
        """Test successful retraining."""
        db = Database("sqlite:///:memory:")
        router = ModelRouter(db)
        
        # Add sufficient feedback
        for i in range(15):
            success = i % 2 == 0  # Alternate success/failure
            db.add_feedback(
                f"Test {i}", 
                "gpt-4" if i % 3 == 0 else "claude-3",
                success,
                features={'length': 0.5, 'complexity': 0.3}
            )
        
        result = router.retrain()
        assert result['status'] == 'success'
        assert result['new_version'] == 2
        assert 'updated_weights' in result
        db.close()


class TestIntegration:
    """Integration tests."""
    
    def test_full_workflow(self):
        """Test complete workflow: route -> feedback -> retrain."""
        db = Database("sqlite:///:memory:")
        router = ModelRouter(db)
        
        # 1. Route multiple requests
        test_inputs = [
            "Implement a complex algorithm for database optimization",
            "Write a creative story about adventure",
            "Create a technical API documentation",
            "Design an innovative art project"
        ]
        
        routes = []
        for input_text in test_inputs:
            model, confidence, features = router.route(input_text)
            routes.append((input_text, model, confidence, features))
        
        # 2. Add feedback for each route
        for input_text, model, confidence, features in routes:
            # Simulate success based on some criteria
            success = confidence > 0.3
            db.add_feedback(
                input_text=input_text,
                selected_model=model,
                success=success,
                confidence_score=confidence,
                features=features
            )
        
        # Add more feedback to meet minimum requirement
        for i in range(10):
            db.add_feedback(f"Additional test {i}", "gpt-4", True)
        
        # 3. Analyze patterns
        patterns = router.analyze_patterns()
        assert patterns['total_records'] >= 10
        
        # 4. Retrain
        result = router.retrain()
        assert result['status'] == 'success'
        assert result['new_version'] == 2
        
        # 5. Verify metrics were stored
        metrics = db.get_latest_metrics()
        assert metrics is not None
        assert metrics.version == 2
        
        db.close()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
