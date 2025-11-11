"""Setup script for Aurea Orchestrator"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="aurea-orchestrator",
    version="0.1.0",
    author="Aurea Team",
    description="Automated Unified Reasoning & Execution Agents - Evaluation System",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/andres20980/aurea-orchestrator",
    packages=find_packages(exclude=["tests*"]),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Testing",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=[
        "fastapi==0.104.1",
        "uvicorn==0.24.0",
        "pydantic==2.5.0",
        "pydantic-settings==2.1.0",
        "psycopg2-binary==2.9.9",
        "sqlalchemy==2.0.23",
        "pytest==7.4.3",
        "pytest-asyncio==0.21.1",
        "prometheus-client==0.19.0",
    ],
)
