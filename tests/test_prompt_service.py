"""Tests for prompt template service"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from aurea_orchestrator.models.database import Base, PromptTemplate
from aurea_orchestrator.services.prompt_service import PromptTemplateService


@pytest.fixture
def db_session():
    """Create a test database session"""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    yield session
    session.close()


class TestPromptTemplateService:
    """Test PromptTemplateService"""
    
    def test_create_template(self, db_session):
        """Test creating a prompt template"""
        template = PromptTemplateService.create_template(
            db=db_session,
            name="test_template",
            template_yaml="prompt: Hello {{ name }}!",
            description="Test template",
            variables=["name"]
        )
        
        assert template.id is not None
        assert template.name == "test_template"
        assert template.version == 1
        assert template.description == "Test template"
        assert template.variables == ["name"]
        assert template.is_active == 1
    
    def test_create_template_new_version(self, db_session):
        """Test creating a new version of existing template"""
        # Create first version
        template1 = PromptTemplateService.create_template(
            db=db_session,
            name="test_template",
            template_yaml="prompt: Hello {{ name }}!",
            variables=["name"]
        )
        
        # Create second version
        template2 = PromptTemplateService.create_template(
            db=db_session,
            name="test_template",
            template_yaml="prompt: Hi {{ name }}, welcome!",
            variables=["name"]
        )
        
        assert template1.version == 1
        assert template2.version == 2
        assert template1.id != template2.id
    
    def test_get_template(self, db_session):
        """Test getting a template by ID"""
        template = PromptTemplateService.create_template(
            db=db_session,
            name="test_template",
            template_yaml="prompt: Hello!",
        )
        
        retrieved = PromptTemplateService.get_template(db=db_session, template_id=template.id)
        assert retrieved is not None
        assert retrieved.id == template.id
        assert retrieved.name == "test_template"
    
    def test_get_template_by_name_version(self, db_session):
        """Test getting template by name and version"""
        # Create two versions
        PromptTemplateService.create_template(
            db=db_session,
            name="test_template",
            template_yaml="v1",
        )
        template2 = PromptTemplateService.create_template(
            db=db_session,
            name="test_template",
            template_yaml="v2",
        )
        
        # Get specific version
        retrieved = PromptTemplateService.get_template_by_name_version(
            db=db_session,
            name="test_template",
            version=2
        )
        assert retrieved is not None
        assert retrieved.version == 2
        assert retrieved.template_yaml == "v2"
        
        # Get latest version (should be v2)
        latest = PromptTemplateService.get_template_by_name_version(
            db=db_session,
            name="test_template"
        )
        assert latest is not None
        assert latest.version == 2
    
    def test_list_templates(self, db_session):
        """Test listing templates"""
        PromptTemplateService.create_template(
            db=db_session,
            name="template1",
            template_yaml="test1",
        )
        PromptTemplateService.create_template(
            db=db_session,
            name="template2",
            template_yaml="test2",
        )
        
        templates = PromptTemplateService.list_templates(db=db_session)
        assert len(templates) == 2
    
    def test_update_template(self, db_session):
        """Test updating a template"""
        template = PromptTemplateService.create_template(
            db=db_session,
            name="test_template",
            template_yaml="original",
            description="Original description"
        )
        
        updated = PromptTemplateService.update_template(
            db=db_session,
            template_id=template.id,
            description="Updated description",
            template_yaml="updated"
        )
        
        assert updated is not None
        assert updated.description == "Updated description"
        assert updated.template_yaml == "updated"
    
    def test_delete_template(self, db_session):
        """Test deleting a template (soft delete)"""
        template = PromptTemplateService.create_template(
            db=db_session,
            name="test_template",
            template_yaml="test",
        )
        
        success = PromptTemplateService.delete_template(
            db=db_session,
            template_id=template.id
        )
        
        assert success is True
        
        # Template should still exist but be inactive
        retrieved = PromptTemplateService.get_template(db=db_session, template_id=template.id)
        assert retrieved is not None
        assert retrieved.is_active == 0
    
    def test_extract_variables_from_yaml(self):
        """Test extracting variables from YAML template"""
        template_yaml = """
        prompt: Hello {{ name }}!
        context: You are {{ role }} helping with {{ task }}.
        """
        
        variables = PromptTemplateService.extract_variables_from_yaml(template_yaml)
        assert set(variables) == {"name", "role", "task"}
    
    def test_render_template(self):
        """Test rendering template with variables"""
        template_yaml = "Hello {{ name }}!"
        variables = {"name": "World"}
        
        rendered = PromptTemplateService.render_template(template_yaml, variables)
        assert rendered == "Hello World!"
    
    def test_render_template_with_missing_variable(self):
        """Test rendering template with missing variable"""
        template_yaml = "Hello {{ name }}!"
        variables = {}
        
        with pytest.raises(ValueError, match="Undefined variable"):
            PromptTemplateService.render_template(template_yaml, variables)
    
    def test_validate_template_valid(self):
        """Test validating a valid template"""
        template_yaml = "prompt: Hello {{ name }}!"
        
        is_valid, error_msg = PromptTemplateService.validate_template(template_yaml)
        assert is_valid is True
        assert error_msg is None
    
    def test_validate_template_invalid_yaml(self):
        """Test validating invalid YAML"""
        template_yaml = "invalid: yaml: content: [unclosed"
        
        is_valid, error_msg = PromptTemplateService.validate_template(template_yaml)
        assert is_valid is False
        assert error_msg is not None
    
    def test_validate_template_with_variables(self):
        """Test validating template with variables"""
        template_yaml = "Hello {{ name }}!"
        variables = {"name": "World"}
        
        is_valid, error_msg = PromptTemplateService.validate_template(
            template_yaml,
            variables
        )
        assert is_valid is True
        assert error_msg is None
