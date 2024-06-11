# Copyright The PFDL Contributors
#
# Licensed under the MIT License.
# For details on the licensing terms, see the LICENSE file.
# SPDX-License-Identifier: MIT

from setuptools import setup, find_packages
from pathlib import Path
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name="pfdl_scheduler",
    version="0.9.0",
    description="Parser and Scheduler of Production Flow Description Language (PFDL) files.",
    long_description=long_description,
    long_description_content_type='text/markdown',
    author="Peter Detzner, Maximilian Hoerstrup",
    author_email="maximilian.hoerstrup@iml.fraunhofer.de",
    python_requires = ">=3.10",
    packages=find_packages(),
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3 :: Only",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        "antlr4-python3-runtime==4.9.3",
        "antlr-denter",
        "snakes",
        "requests",
    ],  # external packages as dependencies
)
