# Copyright The PFDL Contributors
#
# Licensed under the MIT License.
# For details on the licensing terms, see the LICENSE file.
# SPDX-License-Identifier: MIT

"""Contains Instance class."""

# standard libraries
import copy
from numbers import Number
from typing import Dict, Union

# 3rd party libs
from antlr4.ParserRuleContext import ParserRuleContext

# local sources
## PFDL base sources
from pfdl_scheduler.model.array import Array
from pfdl_scheduler.pfdl_base_classes import PFDLBaseClasses
from pfdl_scheduler.validation.error_handler import ErrorHandler


class Instance:
    """Represents an Instance in the PFDL.

    Attributes:
        name: A string representing the name of the Instance.
        attributes: A dict mapping the attribute names with their values.
        struct_name: A string refering to the Struct this Instance instanciates.
        context: ANTLR context object of this class.
        attribute_contexts: A dict that maps the attribute names to their ANTLR contexts.
    """

    def __init__(
        self,
        name: str = "",
        attributes: Dict[str, Union[str, Number, bool, "Instance"]] = None,
        struct_name: str = "",
        context: ParserRuleContext = None,
    ) -> None:
        """Initialize the object.

        Args:
            name: A string representing the name of the Instance.
            attributes: A dict mapping the attribute names with their values.
            struct_name: A string refering to the Struct this Instance instanciates.
            context: ANTLR context object of this class.
        """
        self.name: str = name

        if attributes:
            self.attributes: Dict[str, Union[str, Number, bool, "Instance"]] = attributes
        else:
            self.attributes: Dict[str, Union[str, Number, bool, "Instance"]] = {}

        self.struct_name: str = struct_name
        self.context: ParserRuleContext = context
        self.attribute_contexts: Dict = {}

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
        cls,
        json_object: Dict,
        error_handler: ErrorHandler,
        struct_context: ParserRuleContext,
        pfdl_base_classes=PFDLBaseClasses,
    ):
        return parse_json(json_object, error_handler, struct_context, pfdl_base_classes)


def parse_json(
    json_object: Dict,
    error_handler: ErrorHandler,
    instance_context: ParserRuleContext,
    pfdl_base_classes=PFDLBaseClasses,
) -> Instance:
    """Parses the JSON Struct initialization.

    Returns:
        An Instance object representing the initialized instance.
    """
    instance = pfdl_base_classes.get_class("Instance")()
    instance.context = instance_context
    for identifier, value in json_object.items():
        if isinstance(value, (int, str, bool)):
            instance.attributes[identifier] = value
        elif isinstance(value, list):
            array = pfdl_base_classes.get_class("Array")()
            instance.attributes[identifier] = array
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
                    inner_struct = parse_json(element, error_handler)
                    array.append_value(inner_struct)
        elif isinstance(value, dict):
            inner_struct = parse_json(value, error_handler, instance_context, pfdl_base_classes)
            instance.attributes[identifier] = inner_struct

    return instance
