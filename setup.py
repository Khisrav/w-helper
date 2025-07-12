#!/usr/bin/env python3

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="w-helper",
    version="0.1.0",
    author="W-Helper Team",
    author_email="",
    description="ASUS ROG Zephyrus G14 Control Center for Linux",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/your-username/w-helper",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: System :: Hardware",
        "Topic :: Desktop Environment :: Gnome",
    ],
    python_requires=">=3.8",
    install_requires=[
        "PyGObject>=3.42.0",
    ],
    entry_points={
        "console_scripts": [
            "w-helper=w_helper.cli:main",
        ],
        "gui_scripts": [
            "w-helper-gui=w_helper.main:main",
        ],
    },
    include_package_data=True,
    package_data={
        "w_helper": ["data/*"],
    },
) 