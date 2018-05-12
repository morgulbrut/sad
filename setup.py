"""A setuptools based setup module.
See:
https://packaging.python.org/en/latest/distributing.html
https://github.com/pypa/sampleproject
"""

# Always prefer setuptools over distutils
from setuptools import setup, find_packages
# To use a consistent encoding
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

# Arguments marked as "Required" below must be included for upload to PyPI.
# Fields marked as "Optional" may be commented out.

setup(
    name='sad',  # Required
    version='0.5.0',  # Required
    description='MD to xelatex to PDF',  # Required
    long_description=long_description,  # Optional
    long_description_content_type='text/markdown',  
    url='https://github.com/morgulbrut/sad',  # Optional
    author='Tillo Bosshart',  # Optional
    author_email='tillo.bosshart@gmail.com',  # Optional
    classifiers=[  # Optional
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.6',
    ],
   
    py_modules=['sad'],
    # packages=find_packages(exclude=['contrib', 'docs', 'tests']),  # Required

    install_requires=['colorlog'],  # Optional

    project_urls={  # Optional
        'Bug Reports': 'https://github.com/morgulbrut/sad/issues',
        'Funding': 'https://donate.pypi.org',
        'Say Thanks!': 'https://saythanks.io/to/morgulbrut',
        'Source': 'https://github.com/morgulbrut/sad',
    },
)
