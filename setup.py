#!/usr/bin/env python
# coding: utf-8
import os
from setuptools import setup

README = open(os.path.join(os.path.dirname(__file__), 'README.rst')).read()
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='sae-kvdb',
    version='0.1',
    packages=['xkvdb'],
    include_package_data=True,
    license='BSD License', 
    description='A simple Django app to manage kvdb of SAE.',
    long_description=README,
    url='http://ninan.sinaapp.com/',
    author='xiaoyu',
    author_email='xiaokong1937@gmail.com',
)
