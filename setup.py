from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="video-translator",
    version="1.0.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="A tool for translating video content using Azure services",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/video-translator",
    packages=find_packages(exclude=["tests*"]),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Multimedia :: Video",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "video-translator=main:main",
        ],
    },
    package_data={
        "": ["*.json", "*.wav", "*.mp3"],
    },
    include_package_data=True,
    test_suite="tests",
    tests_require=[
        "pytest>=7.0.0",
        "pytest-cov>=4.0.0",
        "pytest-mock>=3.10.0",
    ],
    setup_requires=[
        "wheel>=0.37.0",
    ],
)