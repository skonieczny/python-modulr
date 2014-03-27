import os
from setuptools import setup, find_packages

root = os.path.abspath(os.path.dirname(__file__))

setup(
    name='modulr',
    version='0.0.1.dev',
    description='Modular, plugginable application base. ',
    author='Stanislaw Skonieczny',
    author_email='stanislaw.skonieczny@gmail.com',
    url='https://github.com/stanislaw-skonieczny/python-modulr',
    packages=['modulr'],
    package_dir = {'': 'src'},
    test_suite='tests',
    include_package_data=True,
    zip_safe=False,
)
