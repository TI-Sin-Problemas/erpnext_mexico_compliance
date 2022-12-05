from setuptools import setup, find_packages

with open("requirements.txt") as f:
	install_requires = f.read().strip().split("\n")

# get version from __version__ variable in mexico_compliance/__init__.py
from mexico_compliance import __version__ as version

setup(
	name="mexico_compliance",
	version=version,
	description="ERPNext app to serve as base to comply with Mexican Rules and Regulations",
	author="TI Sin Problemas",
	author_email="info@tisinproblemas.com",
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)
