from distutils.core import setup

import setuptools

setup(name="barusu",
      version='1.0', description="Python tool for apt, flatpak and dconf tool", author="Derisis13",
      py_modules=["main"],
      packages=setuptools.find_packages())
