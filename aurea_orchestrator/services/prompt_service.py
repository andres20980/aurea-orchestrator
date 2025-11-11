"""Service layer for prompt template operations"""

import re
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import desc
import yaml
from jinja2 import Template, TemplateSyntaxError, UndefinedError, StrictUndefined

from aurea_orchestrator.models.database import PromptTemplate, Job


class PromptTemplateService:
    """Service for managing prompt templates"""
    
    @staticmethod
    def create_template(
        db: Session,
        name: str,
        template_yaml: str,
        description: Optional[str] = None,
        variables: Optional[List[str]] = None
    ) -> PromptTemplate:
        """Create a new prompt template or new version of existing template"""
        
        # Check if template with this name already exists
        existing = db.query(PromptTemplate).filter(
            PromptTemplate.name == name
        ).order_by(desc(PromptTemplate.version)).first()
        
        version = 1
        if existing:
            # Create new version
            version = existing.version + 1
        
        template = PromptTemplate(
            name=name,
            version=version,
            description=description,
            template_yaml=template_yaml,
            variables=variables,
            is_active=1
        )
        
        db.add(template)
        db.commit()
        db.refresh(template)
        
        return template
    
    @staticmethod
    def get_template(
        db: Session,
        template_id: int
    ) -> Optional[PromptTemplate]:
        """Get a prompt template by ID"""
        return db.query(PromptTemplate).filter(
            PromptTemplate.id == template_id
        ).first()
    
    @staticmethod
    def get_template_by_name_version(
        db: Session,
        name: str,
        version: Optional[int] = None
    ) -> Optional[PromptTemplate]:
        """Get a prompt template by name and optionally version"""
        query = db.query(PromptTemplate).filter(PromptTemplate.name == name)
        
        if version is not None:
            query = query.filter(PromptTemplate.version == version)
        else:
            # Get latest version
            query = query.order_by(desc(PromptTemplate.version))
        
        return query.first()
    
    @staticmethod
    def list_templates(
        db: Session,
        skip: int = 0,
        limit: int = 100,
        active_only: bool = False
    ) -> List[PromptTemplate]:
        """List all prompt templates"""
        query = db.query(PromptTemplate)
        
        if active_only:
            query = query.filter(PromptTemplate.is_active == 1)
        
        return query.order_by(
            PromptTemplate.name,
            desc(PromptTemplate.version)
        ).offset(skip).limit(limit).all()
    
    @staticmethod
    def update_template(
        db: Session,
        template_id: int,
        description: Optional[str] = None,
        template_yaml: Optional[str] = None,
        variables: Optional[List[str]] = None,
        is_active: Optional[bool] = None
    ) -> Optional[PromptTemplate]:
        """Update a prompt template"""
        template = db.query(PromptTemplate).filter(
            PromptTemplate.id == template_id
        ).first()
        
        if not template:
            return None
        
        if description is not None:
            template.description = description
        if template_yaml is not None:
            template.template_yaml = template_yaml
        if variables is not None:
            template.variables = variables
        if is_active is not None:
            template.is_active = 1 if is_active else 0
        
        db.commit()
        db.refresh(template)
        
        return template
    
    @staticmethod
    def delete_template(
        db: Session,
        template_id: int
    ) -> bool:
        """Delete a prompt template (soft delete by setting is_active to 0)"""
        template = db.query(PromptTemplate).filter(
            PromptTemplate.id == template_id
        ).first()
        
        if not template:
            return False
        
        template.is_active = 0
        db.commit()
        
        return True
    
    @staticmethod
    def extract_variables_from_yaml(template_yaml: str) -> List[str]:
        """Extract variable names from YAML template"""
        # Find Jinja2-style variables: {{ variable_name }}
        pattern = r'\{\{\s*(\w+)\s*\}\}'
        matches = re.findall(pattern, template_yaml)
        return list(set(matches))  # Return unique variable names
    
    @staticmethod
    def render_template(
        template_yaml: str,
        variables: Dict[str, Any]
    ) -> str:
        """Render template with variables using Jinja2"""
        from jinja2 import StrictUndefined
        try:
            template = Template(template_yaml, undefined=StrictUndefined)
            rendered = template.render(**variables)
            return rendered
        except TemplateSyntaxError as e:
            raise ValueError(f"Template syntax error: {str(e)}")
        except UndefinedError as e:
            raise ValueError(f"Undefined variable in template: {str(e)}")
        except Exception as e:
            raise ValueError(f"Error rendering template: {str(e)}")
    
    @staticmethod
    def validate_template(
        template_yaml: str,
        variables: Optional[Dict[str, Any]] = None
    ) -> tuple[bool, Optional[str]]:
        """Validate template YAML and optional variables"""
        # Validate YAML syntax
        try:
            yaml.safe_load(template_yaml)
        except yaml.YAMLError as e:
            return False, f"Invalid YAML: {str(e)}"
        
        # Validate Jinja2 template syntax
        try:
            Template(template_yaml, undefined=StrictUndefined)
        except TemplateSyntaxError as e:
            return False, f"Invalid template syntax: {str(e)}"
        
        # If variables provided, try rendering
        if variables is not None:
            try:
                PromptTemplateService.render_template(template_yaml, variables)
            except ValueError as e:
                return False, str(e)
        
        return True, None


class JobService:
    """Service for managing jobs"""
    
    @staticmethod
    def create_job(
        db: Session,
        name: str,
        prompt_template_id: Optional[int] = None,
        prompt_version: Optional[int] = None,
        input_data: Optional[Dict[str, Any]] = None
    ) -> Job:
        """Create a new job"""
        
        # If prompt_template_id is provided, get the version
        if prompt_template_id and not prompt_version:
            template = db.query(PromptTemplate).filter(
                PromptTemplate.id == prompt_template_id
            ).first()
            if template:
                prompt_version = template.version
        
        job = Job(
            name=name,
            prompt_template_id=prompt_template_id,
            prompt_version=prompt_version,
            status="pending",
            input_data=input_data
        )
        
        db.add(job)
        db.commit()
        db.refresh(job)
        
        return job
    
    @staticmethod
    def get_job(db: Session, job_id: int) -> Optional[Job]:
        """Get a job by ID"""
        return db.query(Job).filter(Job.id == job_id).first()
    
    @staticmethod
    def list_jobs(
        db: Session,
        skip: int = 0,
        limit: int = 100
    ) -> List[Job]:
        """List all jobs"""
        return db.query(Job).order_by(
            desc(Job.created_at)
        ).offset(skip).limit(limit).all()
