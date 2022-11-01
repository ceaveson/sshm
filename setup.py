from setuptools import setup, find_packages

setup(
    name='sshm',
    version='0.1.4',
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

    ],
    entry_points={
        'console_scripts': [
            'sshm = sshm:cli',
        ],
    },
)
