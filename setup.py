# setup.py

from setuptools import setup, find_packages


def parse_requirements(file_name):
    """Helper function to parse requirements.txt into a list."""
    with open(file_name, 'r') as f:
        return [line.strip() for line in f if line and not line.startswith('#')]


setup(
    name='S3CloudManager',  # Name of your package on PyPI
    version='0.1.0',   # Version of your package
    description='A Python toolkit for managing AWS S3 resources',
    long_description=open('README.md').read(),  # Long description from README
    long_description_content_type='text/markdown',  # Specify markdown format
    author='Omolewa Adaramola',
    author_email='info@bluelambdatechnologies.com',
    url='https://github.com/bluelambdatech/S3CloudManager',  # GitHub project URL
    packages=find_packages(),  # Automatically find packages
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries',
    ],
    python_requires='>=3.6',  # Minimum Python version
    install_requires=parse_requirements('requirements.txt'),
    test_suite='tests',  # Specify your test directory for running tests
)
