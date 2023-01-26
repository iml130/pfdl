# Copyright The PFDL Contributors
#
# Licensed under the MIT License.
# For details on the licensing terms, see the LICENSE file.
# SPDX-License-Identifier: MIT

"""Contains the Array class."""

# standard libraries
import copy
from typing import Any, List

# 3rd party libraries
from antlr4.ParserRuleContext import ParserRuleContext


class Array:
    """Represents an Array in the PFDL.

    Used as as an array definition or a returned array with elements in it.

    Attributes:
        type_of_elements: A string representing the type of the elements inside the array.
        values: A list of elements of the Array (empty if it is a array definition).
        length: An integer for the length of the Array. If it is not defined it gets the value -1.
        context: ANTLR context object of this class.
    """

    def __init__(
        self,
        type_of_elements: str = "",
        values: List[Any] = None,
        context: ParserRuleContext = None,
    ) -> None:
        """Initialize the object.

        Args:
            type_of_elements: A string representing the type of the elements inside the array.
            values: A list of elements of the Array (empty if it is a array definition).
            context: ANTLR context object of this class.
        """
        self.type_of_elements: str = type_of_elements
        if values:
            self.length: int = len(values)
            self.values: List[Any] = values
        else:
            self.values: List[Any] = []
            self.length: int = -1
        self.context: ParserRuleContext = context

    def __repr__(self) -> str:
        length = ""
        if self.length_defined():
            length = self.length
        return self.type_of_elements + "[" + str(length) + "]"

    def __str__(self) -> str:
        return self.__repr__()

    def __add__(self, other) -> str:
        return str(self) + other

    def __radd__(self, other) -> str:
        return other + str(self)

    def __eq__(self, __o: object) -> bool:
        if isinstance(__o, Array):
            return (
                self.values == __o.values
                and self.length == __o.length
                and self.type_of_elements == __o.type_of_elements
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

    def append_value(self, value: Any) -> None:
        """Adds an element to the array and increase the length.

        Args:
            value: The value that should be added to the array.
        """
        if self.length == -1:  # Set length to 0 for arrays with undefined length
            self.length = 0
        self.values.append(value)
        self.length = self.length + 1

    def length_defined(self) -> bool:
        """Returns whether the lenght of the array is defined.

        Returns:
            True if the length of the array is defined.
        """
        return self.length != -1
