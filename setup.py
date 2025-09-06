"""
Setup script para wa-core - Gerenciador funcional do WhatsApp
"""
from setuptools import setup, find_packages
import os

# Lê o README para usar como long_description
def read_readme():
    readme_path = os.path.join(os.path.dirname(__file__), 'README.md')
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as f:
            return f.read()
    return ""

# Lê os requirements
def read_requirements():
    requirements_path = os.path.join(os.path.dirname(__file__), 'requirements.txt')
    if os.path.exists(requirements_path):
        with open(requirements_path, 'r', encoding='utf-8') as f:
            return [line.strip() for line in f if line.strip() and not line.startswith('#')]
    return []

setup(
    name="wa-core",
    version="1.0.0",
    author="WhatsApp Assistant Team",
    author_email="contact@whatsapp-assistant.com",
    description="Gerenciador funcional do WhatsApp para assistentes, bots e automações",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/your-username/wa-core",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Communications :: Chat",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Internet :: WWW/HTTP :: Browsers",
    ],
    python_requires=">=3.8",
    install_requires=read_requirements(),
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=21.0",
            "flake8>=3.8",
            "mypy>=0.800",
        ],
        "docs": [
            "sphinx>=4.0",
            "sphinx-rtd-theme>=0.5",
        ],
    },
    entry_points={
        "console_scripts": [
            "wa-core=wa_core.cli:main",
        ],
    },
    keywords="whatsapp, automation, selenium, bot, assistant, web-scraping",
    project_urls={
        "Bug Reports": "https://github.com/your-username/wa-core/issues",
        "Source": "https://github.com/your-username/wa-core",
        "Documentation": "https://wa-core.readthedocs.io/",
    },
)
