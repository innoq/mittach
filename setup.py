import os

from setuptools import setup, find_packages


NAME = "mittach"

VERSION = open(os.path.join(os.path.dirname(__file__), NAME, "version.py"))
exec VERSION.read() # initializes __version__

DESC = open(os.path.join(os.path.dirname(__file__), "README.md")).read()


setup(name=NAME,
        version=__version__,
        long_description=DESC,
        packages=find_packages(),
        include_package_data=True,
        install_requires=["Flask", "redis"],
        extras_require = {
            "testing": ["pytest"],
            "coverage": ["figleaf", "coverage"]
        })
