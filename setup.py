from setuptools import find_packages

from isc_ops.setup_tools import setup, current_version


setup(
    name='boomerang',
    packages=find_packages(),
    include_package_data=True,
    description='Django app to asynchronously process tasks',
    url='http://github.com/infoscout/boomerang',
    version=current_version(),
)
