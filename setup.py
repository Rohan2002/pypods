from setuptools import setup, find_packages
from pypods import __version__
def read_requirements():
    with open('requirements.txt') as req:
        return req.read().splitlines()

setup(
    name='pypods',
    version=__version__,
    packages=find_packages(),
    install_requires=read_requirements(),
    author='Rohan Deshpande',
    author_email='rohandeshpande832@gmail.com',
    description='A lightweight solution to execute Python dependencies in an isolated fashion.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/Rohan2002/pypods',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
