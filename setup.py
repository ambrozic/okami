from setuptools import setup, find_packages

requirements = [
    "aiohttp==1.3.3",
    "async-timeout==1.1.0",
    "chardet==2.3.0",
    "lxml==3.7.3",
    "multidict==2.1.4",
    "setuptools==34.3.0",
    "yarl==0.9.8",
]
cluster_requirements = requirements + [
    "redis==2.10.5",
]
docs_requirements = requirements + [
    "sphinx==1.5.3",
    "alabaster==0.7.10",
]
tests_requirements = requirements + [
    "flake8==3.3.0",
    "codecov==2.0.5",
    "pytest-asyncio==0.5.0",
    "pytest-cov==2.4.0",
    "pytest==3.0.6",
    "pyyaml==3.12",
]

setup(
    name="okami",
    version="0.1.4",
    description="A high-level web scraping framework",
    author="ambrozic",
    author_email="ambrozic@gmail.com",
    license="BSD",
    url="",
    packages=find_packages(exclude=["tests"]),
    include_package_data=True,
    install_requires=requirements,
    extras_require={
        "cluster": cluster_requirements,
        "docs": docs_requirements,
        "tests": tests_requirements,
    },
    entry_points={
        "console_scripts": [
            "okami=okami.cli.main:main",
        ],
    },
    zip_safe=False,
    classifiers=[
        "Programming Language :: Python",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: POSIX",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Topic :: Internet",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Intended Audience :: Developers",
    ]
)
