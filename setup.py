from setuptools import setup

setup(
    name='vpp2code',
    author='lausek',
    version='0.0.1',
    install_requires=[
        'lark'
    ],
    entry_points={'console_scripts': ['vpp2code=vpp2code.__main__:main']}
)