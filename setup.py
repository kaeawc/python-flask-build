from setuptools import setup, find_packages

setup(
    name="python-flask-build",
    version="0.0.1",
    description="Python Flask Build",
    url="https://github.com/kaeawc/python-flask/",
    author="Jason Pearson",
    author_email="jason.d.pearson@gmail.com",
    license="MIT",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "coverage==7.6.12",
        "Delorean==1.0.0",
        "ipdb==0.13.13",
        "mock==5.1.0",
        "nose2==0.15.1",
        "pycodestyle==2.13.0",
        "requests==2.32.3",
        "tox==4.24.1",
        "PyYaml==6.0.2",
        "flask==3.1.0",
    ],
    zip_safe=False,
)
