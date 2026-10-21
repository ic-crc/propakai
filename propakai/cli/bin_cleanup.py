# Copyright (c) 2026 His Majesty the King in Right of Canada as represented by the Minister of
# Industry through the Communications Research Centre Canada.
#
# Licensed under the MIT License
# See LICENSE file in the project root for full license text.
"""
CLI Command: propakai-bin-cleanup

Mapped via:
    [project.scripts]
    propakai-bin-cleanup = "propakai.cli.bin_cleanup:main"

Usage:
    propakai-bin-cleanup [-y|--yes]

Deletes unsuitable binaries for the current OS and processor architecture.
"""
import argparse
from propakai import _bin_utils


def main() -> None:
    """Entry point for 'propakai-bin-cleanup'."""
    parser = argparse.ArgumentParser(description="Delete unsuitable bin files")
    parser.add_argument("-y", "--yes", action="store_true", help="Proceed without prompt")
    args = parser.parse_args()
    if args.yes:
        _bin_utils.cleanup(skip_prompt=True)
    else:
        _bin_utils.cleanup(skip_prompt=False)


if __name__ == "__main__":
    main()
