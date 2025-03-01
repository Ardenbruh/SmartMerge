

from setuptools import setup, find_packages

setup(
    name='github-merge-assistant',
    version='0.1.0',
    author='Your Name',
    author_email='your.email@example.com',
    description='A GitHub Merge Assistant that helps in merging branches intelligently using AI.',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    install_requires=[
        'PyQt5',
        'PyGithub',
        'google-generativeai'
    ],
    entry_points={
        'console_scripts': [
            'github-merge-assistant=main:main',
        ],
    },
)