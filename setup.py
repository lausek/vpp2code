from setuptools import find_packages, setup

setup(
    name='vpp2code',
    author='lausek',
    version='0.1.0',
    description='generate java code from vpp files',
    url='https://github.com/lausek/vpp2code',
    packages=find_packages(),
    package_data={'': ['vpp2code/defgrammar.lark']},
    include_package_data=True,
    install_requires=[
        'lark'
    ],
    test_require=[
        'antlr4-python3-runtime'
    ],
    entry_points={'console_scripts': ['vpp2code=vpp2code.__main__:main']}
)
