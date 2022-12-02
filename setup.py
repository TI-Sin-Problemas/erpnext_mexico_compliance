from setuptools import setup, find_packages

with open("requirements.txt") as f:
	install_requires = f.read().strip().split("\n")

# get version from __version__ variable in mexican_accounting/__init__.py
from mexican_accounting import __version__ as version

setup(
	name="mexican_accounting",
	version=version,
	description="Base ERPNext App for Compliance with Mexican Accounting",
	author="Alfredo Altamirano",
	author_email="frappe@tisinproblemas.com",
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)
