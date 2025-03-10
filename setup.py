import os
from setuptools import setup, find_packages

# Read the long description from the README file
with open(os.path.join(os.path.dirname(__file__), "README.md"), encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="vl-csv-viewer",  # Changed package name to be more descriptive
    version="0.4.3",
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "vl=vl.cli:main",
            "vll=vl.pager:main",
        ],
    },
    description="An ultrafast CSV viewer in terminals",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Contributors",
    author_email="user@example.com",
    url="https://github.com/w9/vl-csv-viewer",
    project_urls={
        "Bug Tracker": "https://github.com/w9/vl-csv-viewer/issues",
        "Source Code": "https://github.com/w9/vl-csv-viewer",
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Text Processing :: General",
        "Topic :: Utilities",
    ],
    keywords="csv, viewer, terminal, console, table, data, visualization",
    python_requires=">=3.6",
    include_package_data=True,
    test_suite="tests",
    tests_require=[
        "pytest",
        "pytest-cov",
    ],
)