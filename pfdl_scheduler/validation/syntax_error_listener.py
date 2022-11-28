# Copyright The PFDL Contributors
#
# Licensed under the MIT License.
# For details on the licensing terms, see the LICENSE file.
# SPDX-License-Identifier: MIT

"""Contains SyntaxErrorListener class."""

# 3rd party libs
from typing import Any
from antlr4.error.ErrorListener import ErrorListener
from antlr4.CommonTokenStream import CommonTokenStream
from antlr4.error.Errors import RecognitionException
from antlr4 import Recognizer

# local sources
from pfdl_scheduler.validation.error_handler import ErrorHandler


class SyntaxErrorListener(ErrorListener):
    """Custom ErrorListener for the PFDL.

    Overrides Antlr ErrorListener class so we can use
    our ErrorHandler class for syntax errors.

    Attributes:
        token_stream: ANTLR token stream.
        error_handler: ErrorHandler instance for printing errors.
    """

    def __init__(self, token_stream: CommonTokenStream, error_handler: ErrorHandler) -> None:
        """Initialize the object.

        Args:
            token_stream: ANTLR token stream.
            error_handler: ErrorHandler instance for printing errors.
        """
        super()
        self.token_stream: CommonTokenStream = token_stream
        self.error_handler: ErrorHandler = error_handler

    def syntaxError(
        self,
        recognizer: Recognizer,
        offendingSymbol: Any,
        line: int,
        column: int,
        msg: str,
        e: RecognitionException,
    ) -> None:
        """Overwrites the ANTLR ErrorListener method to use the error handler."""
        self.error_handler.print_error(msg, line=line, column=column, syntax_error=True)
