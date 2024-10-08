# Copyright The PFDL Contributors
#
# Licensed under the MIT License.
# For details on the licensing terms, see the LICENSE file.
# SPDX-License-Identifier: MIT

"""Helper functions used in the project (especially in the SemanticErrorChecker)."""

# standard libraries
from typing import Dict, List, Union
import operator

# local sources
from pfdl_scheduler.model.struct import Struct
from pfdl_scheduler.model.task import Task


def get_type_of_variable_list(
    var_list: List[str], task: Task, struct_definitions: Dict[str, Struct]
) -> str:
    """Iterates over the given variable list and gets the type of the last element.

    Returns:
        Type of the last element in the variable list as string.
    """
    current_struct = struct_definitions[task.variables[var_list[0]]]
    for i in range(1, len(var_list) - 1):
        current_struct = struct_definitions[current_struct.attributes[var_list[i]]]
    variable_type = current_struct.attributes[var_list[len(var_list) - 1]]
    return variable_type


def is_con(string: str) -> bool:
    """Checks if the given string is a condition element in the PFDL.

    A condition element can be a PFDL string, boolean or number

    Returns:
        True if the given string is a condition element in the PFDL.
    """
    return is_string(string) or is_boolean(string) or is_number(string)


def is_string(string: str) -> bool:
    """Check if the given parameter is a string in the DSL: It should start and end with '"'.

    Returns:
        True if the given string is a string in the DSL.
    """
    if isinstance(string, str) and string.startswith('"') and string.endswith('"'):
        return True
    return False


def is_boolean(string: str) -> bool:
    """Checks if the given string can be casted to a boolean.

    Returns:
        True if the given string can be casted to a boolean.
    """
    if string in ("true", "false"):
        return True
    return False


def is_number(string: str) -> bool:
    """Checks if the given string can be casted to a number (int or float).

    Returns:
        True if the given string can be casted to a number.
    """
    if is_float(string) or is_int(string):
        return True
    return False


def is_float(string: str) -> bool:
    """Checks if the given string can be casted to a float.

    Returns:
        True if the given string can be casted to a float.
    """
    try:
        float(string)
    except (TypeError, ValueError):
        return False
    else:
        return True


def is_int(string: str) -> bool:
    """Checks if the given string can be casted to an integer.

    Returns:
        True if the given string can be casted to an integer.
    """
    try:
        int(string)
    except (TypeError, ValueError):
        return False
    else:
        return True


def cast_element(string: str) -> Union[str, int, float, bool]:
    """Tries to cast the given string to a primitive datatype.

    Returns:
        The casted element if casting was successful, otherwise the input string
    """
    if is_int(string):
        return int(string)
    elif is_float(string):
        return float(string)
    elif is_boolean(string):
        return string == "true"
    elif is_string(string):
        return string.replace('"', "")
    return string


def parse_operator(op: str) -> operator:
    """Parses a PFDL operator in form of a string into a Python executable operator func."""
    ops = {
        ">": operator.gt,
        ">=": operator.ge,
        "<": operator.lt,
        "<=": operator.le,
        "==": operator.eq,
        "!=": operator.ne,
        "And": operator.and_,
        "Or": operator.or_,
        "+": operator.add,
        "-": operator.sub,
        "*": operator.mul,
        "/": operator.truediv,
    }
    return ops[op]
