from setuptools import setup, find_packages

setup(
    name='cnwi_gee',
    version='4.0.1',
    install_requires =[
        'earthengine-api',
        'pandas',
        'numpy',
        'tagee',
        'geopandas'
    ],
    packages=find_packages(
        include=['cnwi', 'cnwi.*'],
        exclude=['examples', 'scripts', 'bin', '.vscode']
    )
)
