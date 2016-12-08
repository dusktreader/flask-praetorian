import glob

from setuptools import setup, find_packages


setup(
    name='flask-praetorian',
    version='0.1.0',
    author='Tucker Beck',
    author_email='tucker.beck@gmail.com',
    description='light-weight security for flask api apps using flask-jwt',
    license='MIT',
    install_requires=[
        'flask-jwt',
        'passlib>=1.7.0',
        'argon2-cffi',
    ],
    extras_require={
        'dev': [
            'pytest-capturelog',
            'restview',
        ],
        'lint': [
            'flake8',
        ],
        'test': [
            'pytest',
            'freezegun',
            'pytest-flask',
            'flask-sqlalchemy',
        ],
    },
    include_package_data=True,
    packages=find_packages(),
    scripts=glob.glob('bin/*'),
)
