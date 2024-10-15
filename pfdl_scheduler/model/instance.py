# Copyright The PFDL Contributors
#
# Licensed under the MIT License.
# For details on the licensing terms, see the LICENSE file.
# SPDX-License-Identifier: MIT

"""Contains Instance class."""

# standard libraries
import uuid
from numbers import Number
from typing import Dict, Union

# 3rd party libs
from antlr4.ParserRuleContext import ParserRuleContext

# local sources
## PFDL base sources
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

    @classmethod
    def from_json(
        cls,
        json_object: Dict,
        error_handler: ErrorHandler,
        struct_context: ParserRuleContext,
        instance_class="Instance",
    ):
        return parse_json(json_object, error_handler, struct_context, instance_class)


def parse_json(
    json_object: Dict,
    error_handler: ErrorHandler,
    instance_context: ParserRuleContext,
    instance_class=Instance,
) -> Instance:
    """Parses the JSON Struct initialization.

    Returns:
        An Instance object representing the initialized instance.
    """
    instance = instance_class()
    instance.context = instance_context
    for identifier, value in json_object.items():
        if isinstance(value, (int, str, bool)):
            instance.attributes[identifier] = value
        elif isinstance(value, list):
            if error_handler and instance_context:
                error_msg = "Array definition in JSON are not supported in the PFDL."
                error_handler.print_error(error_msg, context=instance_context)
        elif isinstance(value, dict):
            inner_struct = parse_json(value, error_handler, instance_context)
            instance.attributes[identifier] = inner_struct

    return instance
