# Copyright The PFDL Contributors
#
# Licensed under the MIT License.
# For details on the licensing terms, see the LICENSE file.
# SPDX-License-Identifier: MIT

"""Contains functions which are used to load and parse PFDL files."""

# standard libraries
import re
from typing import Tuple, Union
from pathlib import Path

# 3rd party libs
from antlr4.CommonTokenStream import CommonTokenStream
from antlr4.InputStream import InputStream

# local sources
from pfdl_scheduler.parser.pfdl_tree_visitor import PFDLTreeVisitor
from pfdl_scheduler.parser.PFDLLexer import PFDLLexer
from pfdl_scheduler.parser.PFDLParser import PFDLParser

from pfdl_scheduler.validation.error_handler import ErrorHandler
from pfdl_scheduler.validation.syntax_error_listener import SyntaxErrorListener
from pfdl_scheduler.validation.semantic_error_checker import SemanticErrorChecker

from pfdl_scheduler.model.process import Process


def parse_string(
    pfdl_string: str, file_path: str = "", used_in_extension: bool = False
) -> Tuple[bool, Union[None, Process]]:
    """Instantiate the ANTLR lexer and parser and parses the given PFDL string.

    Arguments:
        pfdl_string: A string containing the content of a PFDL file.
        file_path: The path of the PFDL file (used for error messages).
        used_in_extension: A boolean indicating if the function is called from the extension.

    Returns:
        A boolan indicating validity of the PFDL file and the process object if so, otherwise None.
    """
    lexer = PFDLLexer(InputStream(pfdl_string))
    lexer.removeErrorListeners()

    token_stream = CommonTokenStream(lexer)

    parser = PFDLParser(token_stream)
    parser.removeErrorListeners()

    error_handler = ErrorHandler(file_path, used_in_extension)
    error_listener = SyntaxErrorListener(token_stream, error_handler)
    parser.addErrorListener(error_listener)

    tree = parser.program()

    if error_handler.has_error() is False:
        visitor = PFDLTreeVisitor(error_handler)
        process = visitor.visit(tree)

        semantic_error_checker = SemanticErrorChecker(error_handler, process)
        semantic_error_checker.validate_process()

        if error_handler.has_error() is False:
            return (True, process)
        return (False, process)
    return (False, None)


def parse_file(file_path: str) -> Tuple[bool, Union[None, Process], str]:
    """Loads the content of the file from the given path and calls the parse_string function.

    Args:
        file_path: The path to the PFDL file.

    Returns:
        A boolan indicating validity of the PFDL file, the content of the file, and the
        process object if so, otherwise None.
    """
    pfdl_string = load_file(file_path)
    return *parse_string(pfdl_string, file_path), pfdl_string


def write_tokens_to_file(token_stream: CommonTokenStream) -> None:
    """Writes the given ANTLR CommonTokenStream into a file named 'token.txt'."""
    Path("./temp").mkdir(parents=True, exist_ok=True)
    with open("temp/token.txt", "w", encoding="utf-8") as file:
        pattern = re.compile("\r?\n.*")
        for token in token_stream.tokens:
            token_text = token.text
            if re.match(pattern, token.text):
                token_text = "NL"
            file.write(token_text + "\n")


def load_file(file_path: str) -> str:
    """Loads the content of the file from the given path.

    Returns:
        The content of the file as a string.
    """
    pfdl_string = ""
    with open(file_path, "r", encoding="utf-8") as file:
        pfdl_string = file.read()
    return pfdl_string
