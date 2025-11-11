from setuptools import setup, find_packages

setup(
    name='aurea-orchestrator',
    version='0.1.0',
    description='Automated Unified Reasoning & Execution Agents',
    packages=find_packages(),
    install_requires=[
        'packaging>=21.0',
    ],
    python_requires='>=3.8',
)
