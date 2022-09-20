import os

from setuptools import setup, find_packages


lib_folder = os.path.dirname(os.path.realpath(__file__))
requirement_path = lib_folder + "/requirements.txt"
install_requires = []  # Here we'll get: ["gunicorn", "docutils>=0.3", "lxml==0.5a7"]

if os.path.isfile(requirement_path):
    with open(requirement_path) as f:
        install_requires = f.read().splitlines()


setup(
    name="HydrodynamicUtilities",
    version="0.1.0",
    description="Utilities for reservoir engineering",
    author="Demid Maxim",
    author_email="demid.maxim@gmail.com",
    url="https://github.com/demidmaksim",
    packages=find_packages(exclude=["HydrodynamicUtilities"]),
    install_requires=install_requires,
)
