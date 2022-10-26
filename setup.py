from setuptools import setup

setup(
    name='sshmanager',
    version='0.1.0',
    py_modules=['sshmanager'],
    install_requires=[
        'Click',
    ],
    entry_points={
        'console_scripts': [
            'sshmanager = sshmanager:cli',
        ],
    },
)