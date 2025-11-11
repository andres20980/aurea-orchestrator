"""
Tests for agent classes
"""

import unittest
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.architect import ArchitectAgent
from agents.code import CodeAgent
from agents.review import ReviewAgent


class TestAgents(unittest.TestCase):
    """Test agent classes"""
    
    def test_architect_agent_initialization(self):
        """Test ArchitectAgent initialization"""
        agent = ArchitectAgent()
        self.assertEqual(agent.name, 'architect')
        self.assertEqual(agent.version, '1.0.0')
    
    def test_architect_agent_metadata(self):
        """Test ArchitectAgent metadata"""
        agent = ArchitectAgent()
        metadata = agent.get_metadata()
        
        self.assertEqual(metadata['agent_name'], 'architect')
        self.assertEqual(metadata['agent_version'], '1.0.0')
        self.assertIn('capabilities', metadata)
        self.assertIsInstance(metadata['capabilities'], list)
    
    def test_architect_agent_execute(self):
        """Test ArchitectAgent execution"""
        agent = ArchitectAgent()
        task = {'task_id': '123', 'type': 'design'}
        result = agent.execute(task)
        
        self.assertEqual(result['status'], 'completed')
        self.assertIn('metadata', result)
        self.assertEqual(result['metadata']['agent_version'], '1.0.0')
    
    def test_code_agent_initialization(self):
        """Test CodeAgent initialization"""
        agent = CodeAgent()
        self.assertEqual(agent.name, 'code')
        self.assertEqual(agent.version, '1.0.0')
    
    def test_code_agent_metadata(self):
        """Test CodeAgent metadata"""
        agent = CodeAgent()
        metadata = agent.get_metadata()
        
        self.assertEqual(metadata['agent_name'], 'code')
        self.assertEqual(metadata['agent_version'], '1.0.0')
        self.assertIn('capabilities', metadata)
    
    def test_code_agent_execute(self):
        """Test CodeAgent execution"""
        agent = CodeAgent()
        task = {'task_id': '456', 'type': 'generate'}
        result = agent.execute(task)
        
        self.assertEqual(result['status'], 'completed')
        self.assertIn('metadata', result)
        self.assertEqual(result['metadata']['agent_version'], '1.0.0')
    
    def test_review_agent_initialization(self):
        """Test ReviewAgent initialization"""
        agent = ReviewAgent()
        self.assertEqual(agent.name, 'review')
        self.assertEqual(agent.version, '1.0.0')
    
    def test_review_agent_metadata(self):
        """Test ReviewAgent metadata"""
        agent = ReviewAgent()
        metadata = agent.get_metadata()
        
        self.assertEqual(metadata['agent_name'], 'review')
        self.assertEqual(metadata['agent_version'], '1.0.0')
        self.assertIn('capabilities', metadata)
    
    def test_review_agent_execute(self):
        """Test ReviewAgent execution"""
        agent = ReviewAgent()
        task = {'task_id': '789', 'type': 'review'}
        result = agent.execute(task)
        
        self.assertEqual(result['status'], 'completed')
        self.assertIn('metadata', result)
        self.assertEqual(result['metadata']['agent_version'], '1.0.0')


if __name__ == '__main__':
    unittest.main()
