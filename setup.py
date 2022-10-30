from setuptools import setup

setup(
    name='sshm',
    version='0.1.0',
    py_modules=['sshm'],
    install_requires=[
        'Click',
    ],
    entry_points={
        'console_scripts': [
            'sshm = sshm:cli',
        ],
    },
)
