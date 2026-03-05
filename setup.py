#  Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
#  SPDX-License-Identifier: MIT-0

import setuptools

with open("README.md") as fp:
    long_description = fp.read()

setuptools.setup(
    name="lex_sf_drug_reminder_blog",
    version="0.0.1",

    description="lex_sf_drug_reminder_blog",
    long_description=long_description,
    long_description_content_type="text/markdown",

    author="author",

    package_dir={"": "lex_sf_drug_reminder_blog"},
    packages=setuptools.find_packages(where="lex_sf_drug_reminder_blog"),

    install_requires=[
        "aws-cdk-lib==2.241.0",
        "constructs>=10.0.0,<11.0.0",
    ],

    python_requires=">=3.9",

    classifiers=[
        "Development Status :: 4 - Beta",

        "Intended Audience :: Developers",

        "License :: OSI Approved :: Apache Software License",

        "Programming Language :: JavaScript",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",

        "Topic :: Software Development :: Code Generators",
        "Topic :: Utilities",

        "Typing :: Typed",
    ],
)
