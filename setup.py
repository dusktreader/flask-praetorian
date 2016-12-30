import glob
import json

from setuptools import setup, find_packages


with open('.project_metadata.json') as meta_file:
    project_metadata = json.loads(meta_file.read())


setup(
    name=project_metadata['name'],
    version=project_metadata['release'],
    author=project_metadata['author'],
    author_email=project_metadata['author_email'],
    description=project_metadata['description'],
    license=project_metadata['license'],
    install_requires=[
        'flask-jwt',
        'passlib',
        'bcrypt',
        'py-buzz',
    ],
    extras_require={
        'dev': [
            'flake8',
            'flask-sqlalchemy',
            'freezegun',
            'pytest',
            'pytest-capturelog',
            'pytest-flask',
            'sphinx',
        ],
    },
    include_package_data=True,
    packages=find_packages(),
    scripts=glob.glob('bin/*'),
    classifiers=[
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
    ],
)
