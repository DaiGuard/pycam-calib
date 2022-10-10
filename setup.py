from setuptools import setup
from setuptools import find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

def _requires_from_file(filename):
    return open(filename).read().splitlines()

setup(    
    name='pycam_calib',
    version='0.0.1',
    description='',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/DaiGuard/pycam_calib',
    author='DaiGuard',
    author_email='daiguard0224@gmail.com',
    license='MIT',
    package_dir={'pycam-calib': '.'},
    package_data={
        'resource/pycam_calib.ui': ['resource/pycam_calib.ui'],
    },
    packages=find_packages(),
    install_requires=_requires_from_file('requirements.txt'),    
    classifiers=[
        "Programming Language :: Python :: 3",
        'Programming Language :: Python :: 3.8',
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.8',
    entry_points={
        'console_scripts': [
            'pycam_calib=pycam_calib.pycam_calib:main'
        ]
    },    
)