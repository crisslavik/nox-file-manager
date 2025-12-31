#!/usr/bin/env python
"""
NOX VFX File Manager Setup
"""

from setuptools import setup, find_packages
import os

# Read README for long description
def read_readme():
    readme_path = os.path.join(os.path.dirname(__file__), 'README.md')
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as f:
            return f.read()
    return "NOX VFX File Manager - Unified file management for VFX pipelines"

# Read requirements
def read_requirements():
    requirements_path = os.path.join(os.path.dirname(__file__), 'requirements.txt')
    requirements = []
    if os.path.exists(requirements_path):
        with open(requirements_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and not line.startswith('-'):
                    requirements.append(line)
    return requirements

setup(
    name="nox-file-manager",
    version="1.0.0",
    description="Unified file management system for VFX studios",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    author="NOX VFX",
    author_email="cristian@noxvfx.com",
    url="https://github.com/noxvfx/nox-file-manager",
    license="MIT",
    
    # Package configuration
    packages=find_packages(),
    include_package_data=True,
    package_data={
        'config': ['*.yaml'],
        'ui': ['resources/**/*'],
    },
    
    # Dependencies
    install_requires=read_requirements(),
    
    # Python version requirement
    python_requires=">=3.8",
    
    # Entry points
    entry_points={
        'console_scripts': [
            'nox-installer=install:main',
        ],
    },
    
    # Classification
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Multimedia :: Graphics",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    
    # Keywords
    keywords="vfx pipeline file management nuke houdini maya blender shotgrid",
    
    # Project URLs
    project_urls={
        "Bug Reports": "https://github.com/noxvfx/nox-file-manager/issues",
        "Source": "https://github.com/noxvfx/nox-file-manager",
        "Documentation": "https://github.com/noxvfx/nox-file-manager/docs",
    },
)