from setuptools import find_packages, setup


with open('VERSION', 'r') as f:
    version = f.read().strip()


setup(
    name='boomerang',
    packages=find_packages(),
    include_package_data=True,
    description='Django app to asynchronously process tasks',
    url='http://github.com/infoscout/boomerang',
    version=version,
    install_requires=[
        'Django >= 1.8, < 2.0a0',
        'celery >= 3.0',
    ]
)
