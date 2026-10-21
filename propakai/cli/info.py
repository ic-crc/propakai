# Copyright (c) 2026 His Majesty the King in Right of Canada as represented by the Minister of
# Industry through the Communications Research Centre Canada.
#
# Licensed under the MIT License
# See LICENSE file in the project root for full license text.
"""
CLI Command: propakai-info

Mapped via:
    [project.scripts]
    propakai-info = "propakai.cli.info:main"

Usage:
    propakai-info

Print basic package information.
"""
from pathlib import Path
from propakai import __version__
from propakai import _download_utils


def main():
    """Entry point for 'propakai-info'."""
    print(f'propakai version: {__version__}')
    package_dir = Path(__file__).parent.parent
    print(f'Package location: {package_dir}')
    print(f'ITU data files location: {_download_utils.install_dir()}')


if __name__ == "__main__":
    main()
