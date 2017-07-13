#!/usr/bin/env python

from setuptools import setup

setup(
    name='petitzway',
    version='0.0.2',
    description='Python for Z-Way',
    author='Fredrik Haglund',
    author_email='fredrik@petitcircuitlab.com',
    license='BSD',
    keywords='zwave',
    classifiers=[
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 3 :: Only'
    ],
    packages=['petitzway'],
    install_requires=[
        'requests',
        'setuptools',
    ]
)
