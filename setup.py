from setuptools import setup, find_packages

setup(
    name='sshm',
    version='0.1.1',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "attrs==22.1.0",
        "click",
        "commonmark==0.9.1",
        "exceptiongroup==1.0.0",
        "iniconfig==1.1.1",
        "mypy-extensions==0.4.3",
        "packaging==21.3",
        "pathspec==0.10.1",
        "platformdirs==2.5.2",
        "pluggy==1.0.0",
        "Pygments==2.13.0",
        "pyparsing==3.0.9",
        "pytest==7.2.0",
        "PyYAML==6.0",
        "rich==12.6.0",
        "tomli==2.0.1",

    ],
    entry_points={
        'console_scripts': [
            'sshm = sshm.main:cli',
        ],
    },
)
