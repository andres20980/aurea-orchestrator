from setuptools import setup, find_packages

setup(
    name="aurea-orchestrator",
    version="0.1.0",
    description="Automated Unified Reasoning & Execution Agents",
    packages=find_packages(),
    install_requires=[
        "flask>=2.3.0",
        "celery>=5.3.0",
        "redis>=4.5.0",
        "numpy>=1.24.0",
        "scikit-learn>=1.3.0",
        "python-dateutil>=2.8.0",
    ],
    python_requires=">=3.8",
)
