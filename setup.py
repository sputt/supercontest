from setuptools import setup, find_packages
from os import path
from io import open


this_dir = path.abspath(path.dirname(__file__))
with open(path.join(this_dir, 'requirements.txt')) as fh:
    reqs = fh.read().splitlines()


setup(
    name='supercontest',
    version='1.0.0',
    description='South Bay Supercontest',
    url='https://github.com/brianmahlstedt/supercontest',
    author='Brian Mahlstedt',
    author_email='brian.mahlstedt@gmail.com',
    packages=find_packages(),
    install_requires=reqs,
    include_package_data=True,
    entry_points = {
        'console_scripts': [
            'commit-lines=supercontest.lines:main',
            'commit-scores=supercontest.scores:main',
        ]
    }
)
