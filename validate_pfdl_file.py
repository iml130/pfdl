# Copyright The PFDL Contributors
#
# Licensed under the MIT License.
# For details on the licensing terms, see the LICENSE file.
# SPDX-License-Identifier: MIT

# standard libraries
from os import listdir
from os.path import isfile, join

import argparse

from pfdl_scheduler.utils.parsing_utils import parse_program

EXAMPLES_PATH = "examples/"


def main():
    parser = argparse.ArgumentParser(description="PFDL Scheduler")
    parser.add_argument("--file_path")
    parser.add_argument("--folder_path")

    args = parser.parse_args()
    if args.file_path != None:
        parse_program(args.file_path)
    else:
        folder_path = EXAMPLES_PATH
        if args.folder_path != None:
            folder_path = args.folder_path

        example_filenames = [f for f in listdir(folder_path) if isfile(join(folder_path, f))]

        for example_filename in example_filenames:
            print("File " + example_filename + " parsed:")
            parse_program(folder_path + example_filename)
            print("\n")


if __name__ == "__main__":
    main()
