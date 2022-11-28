# Copyright The PFDL Contributors
#
# Licensed under the MIT License.
# For details on the licensing terms, see the LICENSE file.
# SPDX-License-Identifier: MIT

from setuptools import setup

setup(
    name="PFDL Scheduler",
    version="0.9.1",
    description="Execution engine for Production Flow Description Language (PFDL) files.",
    author="Peter Detzner, Maximilian Hoerstrup",
    author_email="maximilian.hoerstrup@iml.fraunhofer.de",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3 :: Only",
    ],
    install_requires=[
        "antlr4-python3-runtime==4.9.3",
        "antlr-denter",
        "snakes",
    ],  # external packages as dependencies
)
