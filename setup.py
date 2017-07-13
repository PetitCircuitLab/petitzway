#!/usr/bin/env python

from setuptools import setup

setup(
    name='petitzway',
    version='0.0.4',
    description='Python module for Z-Way API',
    author='Fredrik Haglund',
    author_email='fredrik@petitcircuitlab.com',
    license='BSD',
    keywords=['zwave', 'zway', 'z-way'],
    classifiers=[
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 3 :: Only'
    ],
    url='https://github.com/PetitCircuitLab/petitzway',
    packages=['petitzway'],
    install_requires=[
        'requests',
        'setuptools',
    ]
)
