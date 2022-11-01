from setuptools import setup, find_packages

setup(
    name='sshm',
    version='0.1.2',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "attrs",
        "Click",
        "commonmark",
        "exceptiongroup",
        "iniconfig",
        "mypy-extensions",
        "packaging",
        "pathspec",
        "platformdirs",
        "pluggy",
        "Pygments",
        "pyparsing",
        "pytest",
        "PyYAML",
        "rich",
        "tomli",

    ],
    entry_points={
        'console_scripts': [
            'sshm = sshm.main:cli',
        ],
    },
)
