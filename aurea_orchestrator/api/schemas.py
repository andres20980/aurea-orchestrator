"""Pydantic schemas for API validation"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, validator
import yaml


class PromptTemplateBase(BaseModel):
    """Base schema for prompt templates"""
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    template_yaml: str = Field(..., min_length=1)
    variables: Optional[List[str]] = None
    
    @validator('template_yaml')
    def validate_yaml(cls, v):
        """Validate that template_yaml is valid YAML"""
        try:
            yaml.safe_load(v)
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML format: {str(e)}")
        return v


class PromptTemplateCreate(PromptTemplateBase):
    """Schema for creating a prompt template"""
    pass


class PromptTemplateUpdate(BaseModel):
    """Schema for updating a prompt template"""
    description: Optional[str] = None
    template_yaml: Optional[str] = None
    variables: Optional[List[str]] = None
    is_active: Optional[bool] = None
    
    @validator('template_yaml')
    def validate_yaml(cls, v):
        """Validate that template_yaml is valid YAML"""
        if v is not None:
            try:
                yaml.safe_load(v)
            except yaml.YAMLError as e:
                raise ValueError(f"Invalid YAML format: {str(e)}")
        return v


class PromptTemplateResponse(PromptTemplateBase):
    """Schema for prompt template response"""
    id: int
    version: int
    created_at: datetime
    updated_at: datetime
    is_active: bool
    
    class Config:
        from_attributes = True
        
    @property
    def is_active_bool(self):
        """Convert is_active from int to bool"""
        return bool(self.is_active)


class PromptPreviewRequest(BaseModel):
    """Schema for prompt preview request"""
    template_yaml: str
    variables: Dict[str, Any]
    
    @validator('template_yaml')
    def validate_yaml(cls, v):
        """Validate that template_yaml is valid YAML"""
        try:
            yaml.safe_load(v)
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML format: {str(e)}")
        return v


class PromptPreviewResponse(BaseModel):
    """Schema for prompt preview response"""
    rendered: str
    original_yaml: str
    variables_used: Dict[str, Any]


class JobBase(BaseModel):
    """Base schema for jobs"""
    name: str = Field(..., min_length=1, max_length=255)
    input_data: Optional[Dict[str, Any]] = None


class JobCreate(JobBase):
    """Schema for creating a job"""
    prompt_template_id: Optional[int] = None
    prompt_version: Optional[int] = None


class JobResponse(JobBase):
    """Schema for job response"""
    id: int
    prompt_template_id: Optional[int] = None
    prompt_version: Optional[int] = None
    status: str
    output_data: Optional[Dict[str, Any]] = None
    created_at: datetime
    completed_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True
