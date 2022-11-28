# Copyright The PFDL Contributors
#
# Licensed under the MIT License.
# For details on the licensing terms, see the LICENSE file.
# SPDX-License-Identifier: MIT

"""Contains the ErrorHandler class."""

# 3rd party libraries
from antlr4.ParserRuleContext import ParserRuleContext


class ErrorHandler:
    """Keeps track of the total error amount in an PFDL file.

    Provides a method for printing an erro which counts the errors.

    Attributes:
        total_error_count: Total number of errors.
        syntax_error_count: Number of syntax errors.
        semantic_error_count: Number of static semantic errors.
        file_path: The file path to the PFDL file.
        used_in_extension: A boolean indicating if the Generator is used within the extension.
    """

    def __init__(self, file_path: str, used_in_extension: bool) -> None:
        """Initialize the object.

        Args:
            file_path: The file path to the PFDL file.
            used_in_extension: A boolean indicating if the Generator is used within the extension.
        """
        self.total_error_count: int = 0
        self.syntax_error_count: int = 0
        self.semantic_error_count: int = 0
        self.file_path: str = file_path
        self.used_in_extension: bool = used_in_extension

    def print_error(
        self,
        error_msg: str,
        line: int = 0,
        column: int = 0,
        off_symbol_length: int = 0,
        context: ParserRuleContext = None,
        syntax_error: bool = False,
    ) -> None:
        """Prints an error into the standard output.

        Args:
            error_msg: A string containing the error message
            line: The line in which the error occured
            column: The column in which the error occured
            off_symbol_length: Length of the offending symbol
            context: ANTLR Context object (lines and column will be used from this if not None)
            syntax_error: A boolean indicating whether the error is a syntax error or not.
        """
        if context:
            line = context.start.line
            column = context.start.column - 1
            off_symbol_length = len(context.start.text)
        if self.used_in_extension:
            print(error_msg)
            print(line)
            print(column + 1)  # for ext: antlr starts at column 0, LSP at column 1
            print(off_symbol_length)
        else:
            print(error_msg)
            print("File " + self.file_path + ", in line " + str(line) + ":" + str(column))

        if syntax_error:
            self.syntax_error_count = self.syntax_error_count + 1
        else:
            self.semantic_error_count = self.semantic_error_count + 1

        self.total_error_count = self.total_error_count + 1

    def has_error(self) -> bool:
        """Returns true if the total error_count is greater than zero."""
        return self.total_error_count > 0
