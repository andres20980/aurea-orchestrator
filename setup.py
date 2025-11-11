from setuptools import setup, find_packages

setup(
    name="aurea-orchestrator",
    version="0.1.0",
    description="Automated Unified Reasoning & Execution Agents",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[
        "pydantic>=2.0.0",
    ],
)
