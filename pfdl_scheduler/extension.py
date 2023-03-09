# Copyright The PFDL Contributors
#
# Licensed under the MIT License.
# For details on the licensing terms, see the LICENSE file.
# SPDX-License-Identifier: MIT

"""Contains the start up script used in the VSCode extension.

A program executed in the VS Code extension which
has a string containing a PFDL program as input.
"""

# standard libraries
import sys

# local sources
from pfdl_scheduler.utils.parsing_utils import parse_string
from pfdl_scheduler.petri_net.generator import PetriNetGenerator


def main():
    valid, process = parse_string(sys.argv[2], used_in_extension=True)
    if valid:
        petrinet_generator = PetriNetGenerator(used_in_extension=True, file_name=sys.argv[3])
        petrinet_generator.generate_petri_net(process)


if __name__ == "__main__":
    main()
