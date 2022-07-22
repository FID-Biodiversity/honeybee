from setuptools import setup

requirements = [
    'Django>=3.2',
    'djangorestframework~=3.13',
    'geojson',
    'pysolr~=3.9',
    'biofid-python-utils@git+https://github.com/FID-Biodiversity/biofid-python-utils.git@main'
]

setup(
    name='BIOfid Honeybee',
    version='0.2.0',
    description='Map geographical document data in the Browser',
    license="AGPLv3",
    long_description='',
    long_description_content_type="text/markdown",
    author='Adrian Pachzelt',
    author_email='a.pachzelt@ub.uni-frankfurt.de',
    url="https://www.biofid.de",
    download_url='https://github.com/FID-Biodiversity/honeybee',
    python_requires='>=3.7',
    packages=['honeybee'],
    install_requires=requirements,
    extras_require={
        'dev': [
            'pytest-django',
        ]
    }
)
