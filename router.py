"""
Model Router with meta-learning capabilities.
"""
import re
from typing import Dict, List, Tuple, Optional
import numpy as np
from collections import defaultdict
from database import Database


class ModelRouter:
    """
    Routes requests to appropriate models based on learned heuristics.
    Supports meta-learning through feedback collection and retraining.
    """
    
    def __init__(self, db: Database):
        self.db = db
        self.available_models = [
            "gpt-4",
            "gpt-3.5-turbo",
            "claude-3",
            "llama-2"
        ]
        # Initial heuristic weights
        self.heuristic_weights = {
            'length': {'gpt-4': 0.3, 'gpt-3.5-turbo': 0.5, 'claude-3': 0.4, 'llama-2': 0.6},
            'complexity': {'gpt-4': 0.6, 'gpt-3.5-turbo': 0.3, 'claude-3': 0.5, 'llama-2': 0.2},
            'technical': {'gpt-4': 0.7, 'gpt-3.5-turbo': 0.4, 'claude-3': 0.6, 'llama-2': 0.5},
            'creative': {'gpt-4': 0.5, 'gpt-3.5-turbo': 0.6, 'claude-3': 0.7, 'llama-2': 0.4},
        }
        self.version = 1
    
    def extract_features(self, input_text: str) -> Dict[str, float]:
        """Extract features from input text."""
        words = input_text.split()
        features = {
            'length': min(len(words) / 100.0, 1.0),  # Normalized length
            'complexity': self._calculate_complexity(input_text),
            'technical': self._detect_technical_content(input_text),
            'creative': self._detect_creative_content(input_text),
        }
        return features
    
    def _calculate_complexity(self, text: str) -> float:
        """Calculate text complexity based on various factors."""
        words = text.split()
        if not words:
            return 0.0
        
        # Average word length
        avg_word_length = sum(len(word) for word in words) / len(words)
        
        # Sentence complexity (punctuation density)
        punctuation_density = sum(1 for c in text if c in '.,;:!?') / len(words)
        
        # Combine metrics
        complexity = min((avg_word_length / 10.0 + punctuation_density) / 2.0, 1.0)
        return complexity
    
    def _detect_technical_content(self, text: str) -> float:
        """Detect technical content in text."""
        technical_keywords = [
            'algorithm', 'database', 'api', 'function', 'class', 'code',
            'implementation', 'architecture', 'system', 'technical', 'programming'
        ]
        text_lower = text.lower()
        matches = sum(1 for keyword in technical_keywords if keyword in text_lower)
        return min(matches / 5.0, 1.0)
    
    def _detect_creative_content(self, text: str) -> float:
        """Detect creative content in text."""
        creative_keywords = [
            'story', 'creative', 'imagine', 'design', 'art', 'write',
            'narrative', 'poem', 'idea', 'brainstorm', 'innovative'
        ]
        text_lower = text.lower()
        matches = sum(1 for keyword in creative_keywords if keyword in text_lower)
        return min(matches / 5.0, 1.0)
    
    def route(self, input_text: str) -> Tuple[str, float, Dict[str, float]]:
        """
        Route input to the most appropriate model.
        Returns: (selected_model, confidence_score, features)
        """
        features = self.extract_features(input_text)
        
        # Calculate scores for each model
        model_scores = {}
        for model in self.available_models:
            score = 0.0
            for feature_name, feature_value in features.items():
                weight = self.heuristic_weights.get(feature_name, {}).get(model, 0.5)
                score += feature_value * weight
            model_scores[model] = score
        
        # Select model with highest score
        selected_model = max(model_scores, key=model_scores.get)
        confidence = model_scores[selected_model] / max(sum(model_scores.values()), 1.0)
        
        return selected_model, confidence, features
    
    def analyze_patterns(self) -> Dict:
        """Analyze success/failure patterns from feedback."""
        feedback_records = self.db.get_all_feedback()
        
        if not feedback_records:
            return {
                'total_records': 0,
                'success_rate': 0.0,
                'patterns': {}
            }
        
        # Aggregate patterns
        model_performance = defaultdict(lambda: {'success': 0, 'failure': 0})
        feature_success_correlation = defaultdict(lambda: {'success': [], 'failure': []})
        
        for record in feedback_records:
            model = record.selected_model
            if record.success:
                model_performance[model]['success'] += 1
            else:
                model_performance[model]['failure'] += 1
            
            # Correlate features with success
            features = record.get_features_dict()
            for feature_name, feature_value in features.items():
                if record.success:
                    feature_success_correlation[feature_name]['success'].append(feature_value)
                else:
                    feature_success_correlation[feature_name]['failure'].append(feature_value)
        
        # Calculate statistics
        total_records = len(feedback_records)
        successful_records = sum(1 for r in feedback_records if r.success)
        success_rate = successful_records / total_records if total_records > 0 else 0.0
        
        patterns = {
            'model_performance': dict(model_performance),
            'feature_correlations': {
                feature: {
                    'avg_success': np.mean(data['success']) if data['success'] else 0.0,
                    'avg_failure': np.mean(data['failure']) if data['failure'] else 0.0
                }
                for feature, data in feature_success_correlation.items()
            }
        }
        
        return {
            'total_records': total_records,
            'success_rate': success_rate,
            'successful_records': successful_records,
            'patterns': patterns
        }
    
    def retrain(self) -> Dict:
        """
        Retrain the router heuristic based on collected feedback.
        Returns metrics about the retraining process.
        """
        analysis = self.analyze_patterns()
        
        if analysis['total_records'] < 10:
            return {
                'status': 'insufficient_data',
                'message': 'Need at least 10 feedback records for retraining',
                'current_accuracy': analysis['success_rate']
            }
        
        old_accuracy = analysis['success_rate']
        
        # Update weights based on patterns
        patterns = analysis['patterns']
        model_performance = patterns['model_performance']
        feature_correlations = patterns['feature_correlations']
        
        # Adjust model weights based on performance
        for model, performance in model_performance.items():
            total = performance['success'] + performance['failure']
            if total > 0:
                success_rate = performance['success'] / total
                
                # Adjust weights for this model across features
                for feature_name in self.heuristic_weights.keys():
                    if model in self.heuristic_weights[feature_name]:
                        # Increase weight if model performs well
                        adjustment = (success_rate - 0.5) * 0.2  # -0.1 to +0.1 adjustment
                        new_weight = self.heuristic_weights[feature_name][model] + adjustment
                        # Keep weights in reasonable range
                        self.heuristic_weights[feature_name][model] = max(0.1, min(0.9, new_weight))
        
        # Adjust feature weights based on correlation
        for feature_name, correlation in feature_correlations.items():
            avg_success = correlation['avg_success']
            avg_failure = correlation['avg_failure']
            
            if feature_name in self.heuristic_weights:
                # If feature value is higher for successful cases, boost it
                if avg_success > avg_failure:
                    for model in self.heuristic_weights[feature_name]:
                        self.heuristic_weights[feature_name][model] *= 1.1
                        self.heuristic_weights[feature_name][model] = min(0.9, self.heuristic_weights[feature_name][model])
        
        # Increment version
        self.version += 1
        
        # Store metrics
        self.db.add_metrics(
            accuracy=old_accuracy,
            total_predictions=analysis['total_records'],
            successful_predictions=analysis['successful_records'],
            version=self.version
        )
        
        return {
            'status': 'success',
            'old_accuracy': old_accuracy,
            'records_processed': analysis['total_records'],
            'new_version': self.version,
            'updated_weights': self.heuristic_weights
        }
