from setuptools import setup, find_packages

setup(
    name='cnwi_gee',
    version='3.0.0',
    install_requires =[
        'earthengine-api',
        'pandas',
        'numpy',
        'tagee',
    ],
    packages=find_packages(
        include=['cnwi', 'cnwi.*'],
        exclude=['examples', 'scripts', 'bin', '.vscode']
    )
)
