# Copyright (c) 2026 His Majesty the King in Right of Canada as represented by the Minister of
# Industry through the Communications Research Centre Canada.
#
# Licensed under the MIT License
# See LICENSE file in the project root for full license text.
"""
CLI Command: propakai-data-cleanup

Mapped via:
    [project.scripts]
    propakai-data-cleanup = "propakai.cli.data_cleanup:main"

Usage:
    propakai-data-cleanup [-y|--yes]

Deletes all installed ITU digital maps and other ITU data files.
"""
import argparse
from propakai import _download_utils


def main() -> None:
    """Entry point for 'propakai-data-cleanup'."""
    parser = argparse.ArgumentParser(description="Delete data files")
    parser.add_argument("-y", "--yes", action="store_true", help="Proceed without prompt")
    args = parser.parse_args()
    if args.yes:
        _download_utils.delete_all_itu_files(skip_prompt=True)
    else:
        _download_utils.delete_all_itu_files(skip_prompt=False)


if __name__ == "__main__":
    main()
