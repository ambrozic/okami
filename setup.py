from setuptools import find_packages, os, setup

with open(os.path.join(os.path.abspath(os.path.dirname(__file__)), "okami/__init__.py")) as f:
    META = {x[0]: x[1].strip()[1: -1] for x in [l.split(" = ", 1) for l in f.readlines() if not l.find("__")]}

with open("readme.md") as f:
    long_description = f.read()

setup(
    name="okami",
    version=META["__version__"],
    author="ambrozic",
    author_email="ambrozic@gmail.com",
    maintainer="ambrozic",
    maintainer_email="ambrozic@gmail.com",
    description="A high-level web scraping framework",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="BSD",
    url="https://github.com/ambrozic/okami",
    project_urls={
        "Code": "https://github.com/ambrozic/okami",
        "Documentation": "https://ambrozic.github.io/okami",
    },
    keywords="scraping framework",
    packages=find_packages(exclude=["tests"]),
    include_package_data=True,
    python_requires=">=3.6",
    install_requires=[
        "aiohttp>=3.2.0,<4.0",
        "attrs>=18.1.0,<19.0",
        "click>=6.0,<7.0",
        "lxml>=4.0,<5.0",
        "multidict>=4.0,<5.0",
        "sqlitedict>=1.5,<1.6",
    ],
    extras_require={
        "docs": [
            "mkdocs-material==3.0.3",
            "mkdocs==1.0.1",
            "pygments==2.2.0",
            "pymdown-extensions==4.12",
        ],
        "tests": [
            "codecov==2.0.15",
            "flake8==3.5.0",
            "markupsafe==1.0",
            "pipdeptree==0.13.0",
            "pytest-asyncio==0.9.0",
            "pytest-cov==2.5.1",
            "pytest-freezegun==0.2.0",
            "pytest==3.7.1",
            "pyyaml==3.13",
        ],
    },
    entry_points={
        "console_scripts": [
            "okami=okami.cli:main",
        ],
    },
    zip_safe=False,
    classifiers=[
        "Programming Language :: Python",
        "Environment :: Web Environment",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: POSIX",
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Topic :: Internet",
        "Topic :: Software Development :: Libraries :: Application Frameworks",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Intended Audience :: Developers",
    ]
)
