import os

from setuptools import setup, find_packages

from mittach import __version__ as VERSION


NAME = "mittach" # XXX: duplicates package metadata

DESC = open(os.path.join(os.path.dirname(__file__), "README.md")).read()


setup(name=NAME,
        version=VERSION,
        long_description=DESC,
        packages=find_packages(exclude=["test"]),
        include_package_data=True,
        zip_safe=False,
        install_requires=["Flask", "redis"],
        extras_require = {
            "testing": ["pytest"],
            "coverage": ["figleaf", "coverage"]
        })
