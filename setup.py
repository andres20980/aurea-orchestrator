from setuptools import setup, find_packages

setup(
    name="aurea-orchestrator",
    version="0.1.0",
    description="Automated Unified Reasoning & Execution Agents - Experiment Manager",
    author="aurea-orchestrator",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.8",
    install_requires=[
        "psycopg2-binary>=2.9.9",
        "sqlalchemy>=2.0.23",
        "pydantic>=2.5.0",
        "python-dotenv>=1.0.0",
        "alembic>=1.12.1",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.3",
            "pytest-cov>=4.1.0",
        ],
    },
)
