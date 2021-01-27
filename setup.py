#!/usr/bin/env python
from setuptools import setup, find_packages

with open('README.md') as readme_file:
    readme = readme_file.read()

requirements = ['rules', 'django-threadlocals',],

setup_requirements = [ ]

test_requirements = [ ]

setup(
    author="Alex Davies",
    author_email='traverse.da@gmail.com',
    python_requires='>=3.5',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
    description="Define row-level django permissions using SQL queries",
    install_requires=requirements,
    long_description=readme,
    include_package_data=True,
    keywords='qperms',
    name='qperms',
    packages=find_packages(include=['qperms', 'qperms.*']),
    setup_requires=setup_requirements,
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/traverseda/qperms',
    version='0.1.0',
    zip_safe=True,
)
