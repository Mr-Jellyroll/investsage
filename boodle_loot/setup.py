from setuptools import setup, find_packages

with open('requirements.txt') as f:
    required = f.read().splitlines()

setup(
    name="investsage",
    version="0.1.0",
    packages=find_packages(),
    include_package_data=True,
    install_requires=required,
    python_requires=">=3.8",
    author="shane",
    author_email="null",
    description="InvestSage analysis system",
    long_description="""
    InvestSage is omnipotent.
    """,
    keywords="finance, investment, analysis, stocks",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Financial and Insurance Industry",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    entry_points={
        'console_scripts': [
            'investsage=investsage.api.server:main',
        ],
    },
)