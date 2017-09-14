from setuptools import setup, find_packages

setup(
    name='catalearn',
    version='1.1.4',
    description='A module for running machine learning code on cloud GPUs',
    url='https://github.com/Catalearn/catalearn',
    author='Edward Liu',
    author_email='edward@catalearn.com',
    license='MIT',
    keywords='machinelearning gpu cloud',
    packages=['catalearn'],
    include_package_data=True,
    platforms='any',
    install_requires=[
        'dill',
        'requests',
        'websocket-client',
        'requests_toolbelt',
        'tqdm',
        'bs4'
    ],
    python_requires='>=3'
)
