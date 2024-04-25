from setuptools import setup, find_packages

setup(
    name='templates_manager',
    version='1.0',
    packages=find_packages(),
    install_requires=[
        'certifi>=2024.2.2',
        'charset-normalizer>=3.3.2',
        'gitdb>=4.0.11',
        'GitPython>=3.1.43',
        'idna>=3.7',
        'pip>=22.3.1',
        'requests>=2.31.0',
        'setuptools>=65.5.1',
        'smmap>=5.0.1',
        'urllib3>=2.2.1',
        'wheel>=0.38.4'
    ],
)
