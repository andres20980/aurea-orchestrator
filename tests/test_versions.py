"""
Tests for agent versioning functionality
"""

import unittest
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.versions import (
    get_agent_version,
    get_all_agent_versions,
    compare_versions,
    version_has_breaking_changes,
    AGENT_VERSIONS
)


class TestAgentVersions(unittest.TestCase):
    """Test agent version management"""
    
    def test_get_agent_version(self):
        """Test retrieving individual agent versions"""
        # Test valid agents
        architect_version = get_agent_version('architect')
        self.assertEqual(architect_version, '1.0.0')
        
        code_version = get_agent_version('code')
        self.assertEqual(code_version, '1.0.0')
        
        review_version = get_agent_version('review')
        self.assertEqual(review_version, '1.0.0')
    
    def test_get_agent_version_case_insensitive(self):
        """Test that agent names are case-insensitive"""
        self.assertEqual(get_agent_version('ARCHITECT'), '1.0.0')
        self.assertEqual(get_agent_version('Architect'), '1.0.0')
        self.assertEqual(get_agent_version('ArChItEcT'), '1.0.0')
    
    def test_get_agent_version_invalid(self):
        """Test error handling for invalid agent names"""
        with self.assertRaises(ValueError) as context:
            get_agent_version('invalid_agent')
        
        self.assertIn('Unknown agent', str(context.exception))
    
    def test_get_all_agent_versions(self):
        """Test retrieving all agent versions"""
        versions = get_all_agent_versions()
        
        # Check that all expected agents are present
        self.assertIn('architect', versions)
        self.assertIn('code', versions)
        self.assertIn('review', versions)
        
        # Check that it returns a copy (not the original dict)
        versions['architect'] = '999.0.0'
        self.assertEqual(AGENT_VERSIONS['architect'], '1.0.0')
    
    def test_compare_versions_equal(self):
        """Test version comparison for equal versions"""
        self.assertEqual(compare_versions('1.0.0', '1.0.0'), 0)
        self.assertEqual(compare_versions('2.5.3', '2.5.3'), 0)
    
    def test_compare_versions_less_than(self):
        """Test version comparison for less than"""
        self.assertEqual(compare_versions('1.0.0', '1.0.1'), -1)
        self.assertEqual(compare_versions('1.0.0', '1.1.0'), -1)
        self.assertEqual(compare_versions('1.0.0', '2.0.0'), -1)
    
    def test_compare_versions_greater_than(self):
        """Test version comparison for greater than"""
        self.assertEqual(compare_versions('1.0.1', '1.0.0'), 1)
        self.assertEqual(compare_versions('1.1.0', '1.0.0'), 1)
        self.assertEqual(compare_versions('2.0.0', '1.0.0'), 1)
    
    def test_version_has_breaking_changes_no_change(self):
        """Test breaking changes detection for same version"""
        self.assertFalse(version_has_breaking_changes('1.0.0', '1.0.0'))
    
    def test_version_has_breaking_changes_patch(self):
        """Test breaking changes detection for patch version bump"""
        self.assertFalse(version_has_breaking_changes('1.0.0', '1.0.1'))
    
    def test_version_has_breaking_changes_minor(self):
        """Test breaking changes detection for minor version bump"""
        self.assertFalse(version_has_breaking_changes('1.0.0', '1.1.0'))
    
    def test_version_has_breaking_changes_major(self):
        """Test breaking changes detection for major version bump"""
        self.assertTrue(version_has_breaking_changes('1.0.0', '2.0.0'))
        self.assertTrue(version_has_breaking_changes('1.5.3', '2.0.0'))
        self.assertTrue(version_has_breaking_changes('2.0.0', '3.0.0'))


if __name__ == '__main__':
    unittest.main()
