"""
Script to generate and save the OpenAPI specification from the Aurea Orchestrator API
"""
import json
import sys
from pathlib import Path

# Add parent directory to path to import the app
sys.path.insert(0, str(Path(__file__).parent))

from orchestrator.main import app


def generate_openapi_spec(output_file: str = "openapi.json"):
    """Generate and save OpenAPI specification"""
    
    # Get the OpenAPI schema from FastAPI
    openapi_schema = app.openapi()
    
    # Save to file
    output_path = Path(__file__).parent / output_file
    with open(output_path, 'w') as f:
        json.dump(openapi_schema, f, indent=2)
    
    print(f"✅ OpenAPI specification generated successfully!")
    print(f"📄 Saved to: {output_path}")
    print(f"📊 Endpoints: {len(openapi_schema.get('paths', {}))}")
    print(f"📋 Schemas: {len(openapi_schema.get('components', {}).get('schemas', {}))}")
    
    # Also save as YAML for convenience
    try:
        import yaml
        yaml_path = Path(__file__).parent / "openapi.yaml"
        with open(yaml_path, 'w') as f:
            yaml.dump(openapi_schema, f, default_flow_style=False, sort_keys=False)
        print(f"📄 Also saved YAML version to: {yaml_path}")
    except ImportError:
        print("ℹ️  Install PyYAML to also generate YAML version: pip install pyyaml")
    
    return openapi_schema


if __name__ == "__main__":
    generate_openapi_spec()
