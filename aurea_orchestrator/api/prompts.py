"""API endpoints for prompt templates"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from aurea_orchestrator.models.config import get_db
from aurea_orchestrator.api.schemas import (
    PromptTemplateCreate,
    PromptTemplateUpdate,
    PromptTemplateResponse,
    PromptPreviewRequest,
    PromptPreviewResponse
)
from aurea_orchestrator.services.prompt_service import PromptTemplateService

router = APIRouter(prefix="/prompts", tags=["prompts"])


@router.post("/", response_model=PromptTemplateResponse, status_code=201)
def create_prompt_template(
    prompt: PromptTemplateCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new prompt template or new version of existing template.
    
    If a template with the same name exists, creates a new version.
    """
    # Extract variables from template if not provided
    variables = prompt.variables
    if variables is None:
        variables = PromptTemplateService.extract_variables_from_yaml(prompt.template_yaml)
    
    # Validate template
    is_valid, error_msg = PromptTemplateService.validate_template(prompt.template_yaml)
    if not is_valid:
        raise HTTPException(status_code=400, detail=error_msg)
    
    template = PromptTemplateService.create_template(
        db=db,
        name=prompt.name,
        template_yaml=prompt.template_yaml,
        description=prompt.description,
        variables=variables
    )
    
    return template


@router.get("/", response_model=List[PromptTemplateResponse])
def list_prompt_templates(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    active_only: bool = Query(False),
    db: Session = Depends(get_db)
):
    """
    List all prompt templates.
    
    - **skip**: Number of templates to skip (for pagination)
    - **limit**: Maximum number of templates to return
    - **active_only**: If true, only return active templates
    """
    templates = PromptTemplateService.list_templates(
        db=db,
        skip=skip,
        limit=limit,
        active_only=active_only
    )
    return templates


@router.get("/{template_id}", response_model=PromptTemplateResponse)
def get_prompt_template(
    template_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific prompt template by ID."""
    template = PromptTemplateService.get_template(db=db, template_id=template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Prompt template not found")
    return template


@router.get("/by-name/{name}", response_model=PromptTemplateResponse)
def get_prompt_template_by_name(
    name: str,
    version: Optional[int] = Query(None),
    db: Session = Depends(get_db)
):
    """
    Get a prompt template by name and optionally version.
    
    If version is not specified, returns the latest version.
    """
    template = PromptTemplateService.get_template_by_name_version(
        db=db,
        name=name,
        version=version
    )
    if not template:
        raise HTTPException(status_code=404, detail="Prompt template not found")
    return template


@router.put("/{template_id}", response_model=PromptTemplateResponse)
def update_prompt_template(
    template_id: int,
    prompt_update: PromptTemplateUpdate,
    db: Session = Depends(get_db)
):
    """
    Update a prompt template.
    
    Note: This updates the specific version, it doesn't create a new version.
    To create a new version, use the POST endpoint with the same name.
    """
    # Validate template if provided
    if prompt_update.template_yaml:
        is_valid, error_msg = PromptTemplateService.validate_template(
            prompt_update.template_yaml
        )
        if not is_valid:
            raise HTTPException(status_code=400, detail=error_msg)
    
    template = PromptTemplateService.update_template(
        db=db,
        template_id=template_id,
        description=prompt_update.description,
        template_yaml=prompt_update.template_yaml,
        variables=prompt_update.variables,
        is_active=prompt_update.is_active
    )
    
    if not template:
        raise HTTPException(status_code=404, detail="Prompt template not found")
    
    return template


@router.delete("/{template_id}", status_code=204)
def delete_prompt_template(
    template_id: int,
    db: Session = Depends(get_db)
):
    """
    Delete a prompt template (soft delete).
    
    Sets the template's is_active flag to false.
    """
    success = PromptTemplateService.delete_template(db=db, template_id=template_id)
    if not success:
        raise HTTPException(status_code=404, detail="Prompt template not found")
    return None


@router.post("/preview", response_model=PromptPreviewResponse)
def preview_prompt_template(
    preview_request: PromptPreviewRequest,
    db: Session = Depends(get_db)
):
    """
    Preview a prompt template with variables.
    
    Renders the template with the provided variables and returns the result.
    """
    try:
        rendered = PromptTemplateService.render_template(
            template_yaml=preview_request.template_yaml,
            variables=preview_request.variables
        )
        
        return PromptPreviewResponse(
            rendered=rendered,
            original_yaml=preview_request.template_yaml,
            variables_used=preview_request.variables
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
