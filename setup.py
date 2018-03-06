from setuptools import setup

setup(
    name='cp_fake',
    version='1.0',
    description='',
    classifiers=[
        'Operating System :: POSIX',
        'Programming Language :: Python :: 3.6',
    ],
    author='Andrey Maksimov',
    author_email='midnightcowboy@rape.lol',
    url='https://github.com/nndii/cloudpayments_fake',
    keywords=['ticketscloud', 'cloudpayments'],
    packages=['cp_fake'],
    install_requires=['aiohttp'],
)
