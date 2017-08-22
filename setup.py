from setuptools import setup

setup(
    name='catalearn',
    packages=['catalearn'],
    version='0.1',
    description='A module for running machine learning code on cloud GPUs',
    url='https://github.com/Catalearn/catalearn',
    download_url='https://github.com/Catalearn/catalearn/archive/0.1.tar.gz',
    author='Edward Liu',
    author_email='edward@catalearn.com',
    license='MIT',
    include_package_data=True,
    install_requires=[
        'dill',
        'requests',
        'websocket-client',
        'requests_toolbelt',
        'Ipython',
        'tqdm'
    ])
