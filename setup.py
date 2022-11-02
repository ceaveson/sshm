from setuptools import setup, find_packages

setup(
    name='sshm',
    version='0.1.5',
    install_requires=[
        "attrs",
        "click",
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
        "appdirs",

    ],
    entry_points={
        'console_scripts': [
            'sshm = sshm:cli',
        ],
    },
)
