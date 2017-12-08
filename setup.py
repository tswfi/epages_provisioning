#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = [
    'zeep>=2.4.0',
]

setup_requirements = [
    # TODO(tswfi): put setup requirements (distutils extensions, etc.) here
]

test_requirements = [
    # TODO: put package test requirements here
]

setup(
    name='epages_provisioning',
    version='0.2.0',
    description="Python library for calling ePages provisioning services",
    long_description=readme + '\n\n' + history,
    author="Tatu Wikman",
    author_email='tatu.wikman@gmail.com',
    url='https://github.com/tswfi/epages_provisioning',
    packages=find_packages(include=['epages_provisioning']),
    include_package_data=True,
    install_requires=requirements,
    license="MIT license",
    zip_safe=False,
    keywords='epages_provisioning',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.6',
    ],
    test_suite='tests',
    tests_require=test_requirements,
    setup_requires=setup_requirements,
)
