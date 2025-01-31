from setuptools import setup, find_packages

with open('requirements.txt') as f:
    required = f.read().splitlines()

setup(
    name="boodle_loot",
    version="0.1.0",
    packages=find_packages(where="."),
    package_dir={"": "."},
    include_package_data=True,
    install_requires=required,
    python_requires=">=3.8",
    author="me",
    author_email="null",
    description="Investment analysis",
    long_description="InvestSage",
    keywords="finance, investment, analysis, stocks",
)