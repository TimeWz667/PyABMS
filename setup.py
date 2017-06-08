from setuptools import setup, find_packages


setup(name='Kamanian',
      version='1.012',
      packages=find_packages(),
      install_requires=['pandas', 'numpy', 'scipy', 'pcore', 'matplotlib', 'networkx'])
