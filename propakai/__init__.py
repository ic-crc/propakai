# Copyright (c) 2026 His Majesty the King in Right of Canada as represented by the Minister of
# Industry through the Communications Research Centre Canada.
#
# Licensed under the MIT License
# See LICENSE file in the project root for full license text.

"""
PropaKai is a cohesive Python package for implementations of ITU-R P. recommendations.

These recommendations, developed by the International Telecommunication Union Radiocommunication
Sector (ITU-R) Study Group 3, provide international standards and methods for predicting the
propagation of radio waves.

## Disclaimer
> This project, PropaKai, is an independent, third-party software implementation of certain ITU-R P.
recommendations. This project is not affiliated with, maintained by, authorized by, sponsored by,
or in any way officially connected with the International Telecommunication Union (ITU). Any use of
the acronym "ITU" is for descriptive and identification purposes only. For official texts and
standards, users must refer directly to the official ITU website
([www.itu.int](https://www.itu.int)).
"""

from importlib.metadata import version, PackageNotFoundError

try:
    # look up the version of the installed package
    __version__ = version("propakai")
except PackageNotFoundError:
    # if the package is not installed, we don't know the version
    __version__ = "unknown"
