from setuptools import setup
from os import path

this_dir = path.abspath(path.dirname(__file__))
with open(path.join(this_dir, 'README.md'), encoding='utf-8') as f:
    readme = f.read()

setup(
    name='supercontest',
    version='1.0.0',
    description='Client for fetching supercontest data',
    long_description=readme,
    long_description_content_type='text/markdown',
    url='https://github.com/brianmahlstedt/supercontest',
    author='Brian Mahlstedt',
    author_email='brian.mahlstedt@gmail.com',
    keywords=['supercontest', 'football', 'nfl'],
    license='MIT',
    packages=['supercontest'],
    install_requires=['requests', 'bs4'],
)
