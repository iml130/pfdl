# Copyright The PFDL Contributors
#
# Licensed under the MIT License.
# For details on the licensing terms, see the LICENSE file.
# SPDX-License-Identifier: MIT

"""Contains the start up script used in the VSCode extension.

A program that shall be executed in the VS Code extension which has a string containing a PFDL program as input as well as the name of the corresponding file.
"""

# standard libraries
import argparse

# local sources
from pfdl_scheduler.utils.parsing_utils import parse_string
from pfdl_scheduler.petri_net.generator import PetriNetGenerator


def main():
    parser = argparse.ArgumentParser(
        description="A program that shall be executed in the VS Code extension which has a string containing a PFDL program as input as well as the name of the corresponding file."
    )
    parser.add_argument("file_path", type=str, help="The requesters filepath.")
    parser.add_argument("pfdl_string", type=str, help="The content of a given PFDL file as string.")
    parser.add_argument("file_name", type=str, help="The name of the given PFDL file.")
    args = parser.parse_args()

    pfdl_string = ""
    if args.pfdl_string:
        pfdl_string = args.pfdl_string

    valid, process = parse_string(pfdl_string, used_in_extension=True)
    if valid:
        file_name = ""
        if args.file_name:
            file_name = args.file_name
        petrinet_generator = PetriNetGenerator(used_in_extension=True, file_name=file_name)
        petrinet_generator.generate_petri_net(process)


if __name__ == "__main__":
    main()
