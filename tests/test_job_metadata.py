"""
Tests for job metadata functionality
"""

import unittest
import sys
import os
import tempfile
import shutil

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from job_metadata import JobMetadata, JobMetadataStore


class TestJobMetadata(unittest.TestCase):
    """Test job metadata management"""
    
    def test_job_metadata_initialization(self):
        """Test JobMetadata initialization"""
        metadata = JobMetadata('job123', 'orchestration')
        
        self.assertEqual(metadata.job_id, 'job123')
        self.assertEqual(metadata.job_type, 'orchestration')
        self.assertEqual(metadata.status, 'initialized')
        self.assertIsNotNone(metadata.created_at)
    
    def test_add_agent_version(self):
        """Test adding agent versions to job metadata"""
        metadata = JobMetadata('job123', 'orchestration')
        
        metadata.add_agent_version('architect', '1.0.0')
        metadata.add_agent_version('code', '1.0.0')
        
        self.assertEqual(metadata.agent_versions['architect'], '1.0.0')
        self.assertEqual(metadata.agent_versions['code'], '1.0.0')
    
    def test_add_result(self):
        """Test adding results to job metadata"""
        metadata = JobMetadata('job123', 'orchestration')
        
        result1 = {'status': 'success', 'output': 'test1'}
        result2 = {'status': 'success', 'output': 'test2'}
        
        metadata.add_result(result1)
        metadata.add_result(result2)
        
        self.assertEqual(len(metadata.results), 2)
        self.assertEqual(metadata.results[0]['data'], result1)
        self.assertEqual(metadata.results[1]['data'], result2)
    
    def test_update_status(self):
        """Test updating job status"""
        metadata = JobMetadata('job123', 'orchestration')
        
        metadata.update_status('running')
        self.assertEqual(metadata.status, 'running')
        self.assertIsNotNone(metadata.updated_at)
        
        metadata.update_status('completed')
        self.assertEqual(metadata.status, 'completed')
    
    def test_to_dict(self):
        """Test converting metadata to dictionary"""
        metadata = JobMetadata('job123', 'orchestration')
        metadata.add_agent_version('architect', '1.0.0')
        metadata.update_status('completed')
        
        data = metadata.to_dict()
        
        self.assertEqual(data['job_id'], 'job123')
        self.assertEqual(data['job_type'], 'orchestration')
        self.assertEqual(data['status'], 'completed')
        self.assertIn('architect', data['agent_versions'])
    
    def test_to_json(self):
        """Test converting metadata to JSON"""
        metadata = JobMetadata('job123', 'orchestration')
        metadata.add_agent_version('code', '1.0.0')
        
        json_str = metadata.to_json()
        
        self.assertIsInstance(json_str, str)
        self.assertIn('job123', json_str)
        self.assertIn('code', json_str)
    
    def test_from_dict(self):
        """Test creating metadata from dictionary"""
        data = {
            'job_id': 'job456',
            'job_type': 'test',
            'created_at': '2023-01-01T00:00:00',
            'status': 'completed',
            'agent_versions': {'review': '1.0.0'},
            'results': []
        }
        
        metadata = JobMetadata.from_dict(data)
        
        self.assertEqual(metadata.job_id, 'job456')
        self.assertEqual(metadata.job_type, 'test')
        self.assertEqual(metadata.status, 'completed')
        self.assertEqual(metadata.agent_versions['review'], '1.0.0')


class TestJobMetadataStore(unittest.TestCase):
    """Test job metadata storage"""
    
    def setUp(self):
        """Set up temporary directory for tests"""
        self.temp_dir = tempfile.mkdtemp()
        self.store = JobMetadataStore(self.temp_dir)
    
    def tearDown(self):
        """Clean up temporary directory"""
        shutil.rmtree(self.temp_dir)
    
    def test_save_and_load(self):
        """Test saving and loading metadata"""
        metadata = JobMetadata('job123', 'orchestration')
        metadata.add_agent_version('architect', '1.0.0')
        metadata.update_status('completed')
        
        self.store.save(metadata)
        
        loaded = self.store.load('job123')
        
        self.assertIsNotNone(loaded)
        self.assertEqual(loaded.job_id, 'job123')
        self.assertEqual(loaded.status, 'completed')
        self.assertEqual(loaded.agent_versions['architect'], '1.0.0')
    
    def test_load_nonexistent(self):
        """Test loading non-existent job"""
        loaded = self.store.load('nonexistent')
        self.assertIsNone(loaded)
    
    def test_list_jobs(self):
        """Test listing all jobs"""
        metadata1 = JobMetadata('job1', 'type1')
        metadata2 = JobMetadata('job2', 'type2')
        
        self.store.save(metadata1)
        self.store.save(metadata2)
        
        jobs = self.store.list_jobs()
        
        self.assertEqual(len(jobs), 2)
        self.assertIn('job1', jobs)
        self.assertIn('job2', jobs)
    
    def test_compare_runs(self):
        """Test comparing two job runs"""
        metadata1 = JobMetadata('job1', 'orchestration')
        metadata1.add_agent_version('architect', '1.0.0')
        metadata1.add_agent_version('code', '1.0.0')
        
        metadata2 = JobMetadata('job2', 'orchestration')
        metadata2.add_agent_version('architect', '1.1.0')  # Different version
        metadata2.add_agent_version('code', '1.0.0')  # Same version
        
        self.store.save(metadata1)
        self.store.save(metadata2)
        
        comparison = self.store.compare_runs('job1', 'job2')
        
        self.assertIn('differences', comparison)
        self.assertTrue(comparison['differences']['architect']['changed'])
        self.assertFalse(comparison['differences']['code']['changed'])
    
    def test_compare_runs_nonexistent(self):
        """Test comparing with non-existent job"""
        metadata1 = JobMetadata('job1', 'orchestration')
        self.store.save(metadata1)
        
        comparison = self.store.compare_runs('job1', 'nonexistent')
        
        self.assertIn('error', comparison)
        self.assertFalse(comparison['job2_found'])


if __name__ == '__main__':
    unittest.main()
