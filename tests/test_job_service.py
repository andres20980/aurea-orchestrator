"""Tests for job service"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from aurea_orchestrator.models.database import Base, PromptTemplate, Job
from aurea_orchestrator.services.prompt_service import PromptTemplateService, JobService


@pytest.fixture
def db_session():
    """Create a test database session"""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    yield session
    session.close()


class TestJobService:
    """Test JobService"""
    
    def test_create_job_without_template(self, db_session):
        """Test creating a job without a template"""
        job = JobService.create_job(
            db=db_session,
            name="test_job",
            input_data={"key": "value"}
        )
        
        assert job.id is not None
        assert job.name == "test_job"
        assert job.status == "pending"
        assert job.input_data == {"key": "value"}
        assert job.prompt_template_id is None
        assert job.prompt_version is None
    
    def test_create_job_with_template(self, db_session):
        """Test creating a job with a template"""
        # Create a template first
        template = PromptTemplateService.create_template(
            db=db_session,
            name="test_template",
            template_yaml="prompt: Hello!",
        )
        
        # Create job with template
        job = JobService.create_job(
            db=db_session,
            name="test_job",
            prompt_template_id=template.id,
            input_data={"key": "value"}
        )
        
        assert job.id is not None
        assert job.name == "test_job"
        assert job.prompt_template_id == template.id
        assert job.prompt_version == template.version
    
    def test_create_job_auto_version(self, db_session):
        """Test that job automatically records prompt version"""
        # Create a template
        template = PromptTemplateService.create_template(
            db=db_session,
            name="test_template",
            template_yaml="v1",
        )
        
        # Create job with template (version should be auto-filled)
        job = JobService.create_job(
            db=db_session,
            name="test_job",
            prompt_template_id=template.id
        )
        
        assert job.prompt_version == 1
    
    def test_get_job(self, db_session):
        """Test getting a job by ID"""
        job = JobService.create_job(
            db=db_session,
            name="test_job"
        )
        
        retrieved = JobService.get_job(db=db_session, job_id=job.id)
        assert retrieved is not None
        assert retrieved.id == job.id
        assert retrieved.name == "test_job"
    
    def test_list_jobs(self, db_session):
        """Test listing jobs"""
        JobService.create_job(db=db_session, name="job1")
        JobService.create_job(db=db_session, name="job2")
        JobService.create_job(db=db_session, name="job3")
        
        jobs = JobService.list_jobs(db=db_session)
        assert len(jobs) == 3
    
    def test_job_prompt_relationship(self, db_session):
        """Test that job correctly references prompt template"""
        template = PromptTemplateService.create_template(
            db=db_session,
            name="test_template",
            template_yaml="test",
        )
        
        job = JobService.create_job(
            db=db_session,
            name="test_job",
            prompt_template_id=template.id
        )
        
        # Retrieve job and check relationship
        retrieved_job = JobService.get_job(db=db_session, job_id=job.id)
        assert retrieved_job.prompt_template is not None
        assert retrieved_job.prompt_template.id == template.id
        assert retrieved_job.prompt_template.name == "test_template"
