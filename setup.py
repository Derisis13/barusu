from distutils.core import setup

import setuptools

setup(name="backup_assistant",
      version='1.0', description="Python apt and dconf backup tool", author="Derisis13",
      py_modules=["main"],
      packages=setuptools.find_packages())
