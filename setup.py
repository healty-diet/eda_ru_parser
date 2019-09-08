#!/usr/bin/env python
from distutils.core import setup

INSTALL_REQUIRES = ["beautifulsoup4", "requests", "PySocks", "stem"]

PYTHON_REQUIRES = ">=3.5"

setup(
    name="eda_ru_parser",
    version="0.1",
    description="Eda.ru site parser application",
    packages=["eda_ru_parser"],
    install_requires=INSTALL_REQUIRES,
    python_requires=PYTHON_REQUIRES,
)
