# Copyright The PFDL Contributors
#
# Licensed under the MIT License.
# For details on the licensing terms, see the LICENSE file.
# SPDX-License-Identifier: MIT

"""Contains the Struct class."""

# standard libraries
import copy
from dataclasses import dataclass
from typing import Dict, Union
import json

# 3rd party libraries
from antlr4.ParserRuleContext import ParserRuleContext

# local sources
from pfdl_scheduler.model.array import Array
from pfdl_scheduler.validation.error_handler import ErrorHandler


@dataclass
class Struct:
    """Represents a Struct in the PFDL.

    Data container for Services and Taskcalls.
    Used both for Struct definitons and instantiated Structs.

    Attributes:
        name: A string representing the name of the Struct.
        attributes: A dict which maps the attribute names to the defined type
                    or a value (if its a instantiated struct).
        context: ANTLR context object of this class.
        context_dict: Maps other attributes with ANTLR context objects.
    """

    def __init__(
        self,
        name: str = "",
        attributes: Dict[str, Union[str, Array, "Struct"]] = None,
        context: ParserRuleContext = None,
    ) -> None:
        """Initialize the object.

        Args:
            name: A string representing the name of the Struct.
            attributes: A dict which maps the attribute names to the defined type
                        or a value (if its a instantiated struct).
            context: ANTLR context object of this class.
        """
        self.name: str = name
        if attributes:
            self.attributes: Dict[str, Union[str, Array, "Struct"]] = attributes
        else:
            self.attributes: Dict[str, Union[str, Array, "Struct"]] = {}
        self.context: ParserRuleContext = context
        self.context_dict: Dict = {}

    def __eq__(self, __o: object) -> bool:
        if isinstance(__o, Struct):
            return (
                self.name == __o.name
                and self.attributes == __o.attributes
                and self.context == __o.context
                and self.context_dict == __o.context_dict
            )
        return False

    def __deepcopy__(self, memo):
        cls = self.__class__
        result = cls.__new__(cls)
        memo[id(self)] = result
        for attr, value in self.__dict__.items():
            try:
                setattr(result, attr, copy.deepcopy(value, memo))
            except Exception:
                setattr(result, attr, value)
        return result

    @classmethod
    def from_json(
        cls, json_string: str, error_handler: ErrorHandler, struct_context: ParserRuleContext
    ) -> "Struct":
        """Creates a Struct instance out of the given JSON string.

        Args:
            json_string: A JSON string desribing the Struct.
            error_handler: An ErrorHandler instance used for printing errors.

        Returns:
            The Struct which was created from the JSON string.
        """
        json_object = json.loads(json_string)
        struct = parse_json(json_object, error_handler, struct_context)
        return struct


def parse_json(
    json_object: Dict, error_handler: ErrorHandler, struct_context: ParserRuleContext
) -> Struct:
    """Parses the JSON Struct initialization.

    Args:
        json_object: A JSON object describing the Struct.
        error_handler: An ErrorHandler instance used for printing errors.
        struct_context: The ANTLR struct context the struct corresponds to.

    Returns:
        A Struct object representing the initialized Struct.
    """
    struct = Struct()
    struct.context = struct_context

    for identifier, value in json_object.items():
        if isinstance(value, (int, float, str, bool)):
            struct.attributes[identifier] = value
        elif isinstance(value, list):
            array = Array()
            array.context = struct_context
            struct.attributes[identifier] = array
            for element in value:
                if isinstance(element, (int, float, str, bool)):
                    if isinstance(element, bool):
                        array.type_of_elements = "boolean"
                    elif isinstance(element, (int, float)):
                        array.type_of_elements = "number"
                    else:
                        array.type_of_elements = "string"
                    array.append_value(element)
                elif isinstance(element, dict):
                    inner_struct = parse_json(element, error_handler, struct_context)
                    array.append_value(inner_struct)
        elif isinstance(value, dict):
            inner_struct = parse_json(value, error_handler, struct_context)
            struct.attributes[identifier] = inner_struct
    return struct
