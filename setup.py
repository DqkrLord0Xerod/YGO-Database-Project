from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="yugioh-db-generator",
    version="1.0.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="A tool for generating Yu-Gi-Oh! card databases from deck lists",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/yugioh-db-generator",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    install_requires=[
        "requests>=2.28.0",
        "tqdm>=4.65.0",
        "colorama>=0.4.6",
        "python-levenshtein>=0.21.0",
        "pyyaml>=6.0.0",
    ],
    entry_points={
        "console_scripts": [
            "yugioh-db-generator=yugioh_db_generator.__main__:main",
        ],
    },
)
