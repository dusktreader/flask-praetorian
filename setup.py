import glob
import json

from setuptools import setup, find_packages


with open('.project_metadata.json') as meta_file:
    project_metadata = json.loads(meta_file.read())

with open('README.rst') as readme_file:
    long_description = readme_file.read()
    long_description_content_type = 'text/x-rst'

setup(
    name=project_metadata['name'],
    version=project_metadata['release'],
    author=project_metadata['author'],
    author_email=project_metadata['author_email'],
    description=project_metadata['description'],
    url=project_metadata['url'],
    long_description=long_description,
    long_description_content_type=long_description_content_type,
    license=project_metadata['license'],
    setup_requires=[
        'pytest-runner',
    ],
    tests_require=[
        'pytest',
    ],
    install_requires=[
        'Flask>=1.0',
        'pyjwt',
        'pendulum>=2.0',
        'passlib',
        'flask-buzz>=0.1.7',
    ],
    extras_require={
        'dev': [
            'flake8',
            'flask-cors',
            'flask-sqlalchemy',
            'freezegun',
            'pytest',
            'pytest-flask',
            'sphinx',
        ],
    },
    include_package_data=True,
    packages=find_packages(),
    scripts=glob.glob('bin/*'),
    zip_safe=False,
    classifiers=[
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
    ],
)
