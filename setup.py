from setuptools import setup, find_packages

setup(
    name="vl",
    version="0.1.0",
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "vl=vl.cli:main",
        ],
    },
    description="An ultrafast CSV viewer in terminals",
    author="User",
    author_email="user@example.com",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)