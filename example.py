"""
Example usage of Aurea Orchestrator with semantic versioning
"""

from agents import ArchitectAgent, CodeAgent, ReviewAgent
from job_metadata import JobMetadata, JobMetadataStore


def main():
    """Demonstrate agent versioning and job metadata tracking"""
    
    print("=" * 60)
    print("Aurea Orchestrator - Agent Versioning Example")
    print("=" * 60)
    
    # Initialize agents
    print("\n1. Initializing agents...")
    architect = ArchitectAgent()
    code = CodeAgent()
    review = ReviewAgent()
    
    print(f"   - {architect.name}: v{architect.version}")
    print(f"   - {code.name}: v{code.version}")
    print(f"   - {review.name}: v{review.version}")
    
    # Create a job
    print("\n2. Creating a new job...")
    job = JobMetadata('job-001', 'orchestration')
    
    # Record agent versions used in this job
    print("\n3. Recording agent versions in job metadata...")
    job.add_agent_version(architect.name, architect.version)
    job.add_agent_version(code.name, code.version)
    job.add_agent_version(review.name, review.version)
    
    # Execute tasks with agents
    print("\n4. Executing tasks with agents...")
    job.update_status('running')
    
    # Architect creates design
    design_task = {'task_id': 'design-001', 'type': 'create_architecture'}
    design_result = architect.execute(design_task)
    job.add_result(design_result)
    print(f"   - Architect completed design task")
    
    # Code implements design
    code_task = {'task_id': 'code-001', 'type': 'implement', 'based_on': 'design-001'}
    code_result = code.execute(code_task)
    job.add_result(code_result)
    print(f"   - Code agent completed implementation")
    
    # Review validates code
    review_task = {'task_id': 'review-001', 'type': 'validate', 'target': 'code-001'}
    review_result = review.execute(review_task)
    job.add_result(review_result)
    print(f"   - Review agent completed validation")
    
    job.update_status('completed')
    
    # Save job metadata
    print("\n5. Saving job metadata...")
    store = JobMetadataStore()
    store.save(job)
    print(f"   - Job metadata saved to {store.storage_dir}/job-001.json")
    
    # Display job metadata
    print("\n6. Job Metadata Summary:")
    print(f"   Job ID: {job.job_id}")
    print(f"   Type: {job.job_type}")
    print(f"   Status: {job.status}")
    print(f"   Agent Versions Used:")
    for agent_name, version in job.agent_versions.items():
        print(f"     - {agent_name}: {version}")
    print(f"   Tasks Completed: {len(job.results)}")
    
    # Create a second job to demonstrate comparison
    print("\n7. Creating second job for comparison...")
    job2 = JobMetadata('job-002', 'orchestration')
    job2.add_agent_version('architect', '1.0.0')
    job2.add_agent_version('code', '1.1.0')  # Different version
    job2.add_agent_version('review', '1.0.0')
    job2.update_status('completed')
    store.save(job2)
    
    # Compare jobs
    print("\n8. Comparing job runs...")
    comparison = store.compare_runs('job-001', 'job-002')
    print("   Version differences:")
    for agent_name, diff in comparison['differences'].items():
        if diff['changed']:
            print(f"     - {agent_name}: {diff['job1_version']} -> {diff['job2_version']} (CHANGED)")
        else:
            print(f"     - {agent_name}: {diff['version']} (unchanged)")
    
    print("\n" + "=" * 60)
    print("Example completed successfully!")
    print("=" * 60)
    print("\nYou can now:")
    print("  - View jobs: python cli.py list-jobs")
    print("  - View job details: python cli.py job-info job-001")
    print("  - Compare jobs: python cli.py compare-jobs job-001 job-002")
    print("  - Check agent versions: python cli.py agents-versions")
    print("  - Or use the REST API: python api.py")


if __name__ == '__main__':
    main()
