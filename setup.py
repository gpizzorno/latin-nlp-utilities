from setuptools import find_packages, setup

setup(
    name='latin_utilities',
    version='0.5',
    packages=find_packages(),
    ## Include data files
    package_data={'latin_utilities': ['data/*.*']},
    ## Metadata
    author='Gabe Pizzorno',
    description='A set of convenience tools for Natural Language Processing work with Latin treebanks and annotated corpora.',
)
