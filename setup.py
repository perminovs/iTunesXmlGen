from setuptools import setup, find_packages
from os import path

with open(path.join(path.dirname(__file__), "README.md"), mode='r') as r:
    long_description = r.read()

setup(
    name="itunesxmlgen",
    version="0.1.2",
    author="Perminov Sergey",
    url="https://github.com/perminovs/iTunesXmlGen",
    description="iTunes xml generator",
    long_description=long_description,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    packages=find_packages(),
    install_requires=[
        "lxml==4.6.5",
    ],
)
