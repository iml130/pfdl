# Copyright The PFDL Contributors
#
# Licensed under the MIT License.
# For details on the licensing terms, see the LICENSE file.
# SPDX-License-Identifier: MIT

"""Contains functions which are used to load and parse PFDL files."""

# standard libraries
import re
import os
from typing import Tuple, Union
from pathlib import Path

# 3rd party libs
from antlr4.CommonTokenStream import CommonTokenStream
from antlr4.InputStream import InputStream

# local sources
from pfdl_scheduler.pfdl_base_classes import PFDLBaseClasses
from pfdl_scheduler.model.process import Process


def parse_string(
    pfdl_string: str,
    file_path: str = "",
    used_in_extension: bool = False,
    pfdl_base_classes: PFDLBaseClasses = PFDLBaseClasses("pfdl_scheduler"),
) -> Tuple[bool, Union[None, Process]]:
    """Instantiate the ANTLR lexer and parser and parses the given PFDL string.

    Arguments:
        pfdl_string: A string containing the content of a PFDL file.
        file_path: The path of the PFDL file (used for error messages).
        used_in_extension: A boolean indicating if the function is called from the extension.

    Returns:
        A boolan indicating validity of the PFDL file and the process object if so, otherwise None.
    """
    lexer = pfdl_base_classes.get_class("PFDLLexer")(InputStream(pfdl_string))
    lexer.removeErrorListeners()

    token_stream = CommonTokenStream(lexer)

    parser = pfdl_base_classes.get_class("PFDLParser")(token_stream)
    parser.removeErrorListeners()

    error_handler = pfdl_base_classes.get_class("ErrorHandler")(file_path, used_in_extension)
    error_listener = pfdl_base_classes.get_class("SyntaxErrorListener")(token_stream, error_handler)
    parser.addErrorListener(error_listener)

    tree = parser.program()

    if error_handler.has_error() is False:
        visitor = pfdl_base_classes.get_class("PFDLTreeVisitor")(error_handler, pfdl_base_classes)
        process = visitor.visit(tree)

        semantic_error_checker = pfdl_base_classes.get_class("SemanticErrorChecker")(
            error_handler, process, pfdl_base_classes
        )
        semantic_error_checker.validate_process()

        if error_handler.has_error() is False:
            return (True, process)
        return (False, process)
    return (False, None)


def parse_program(
    program: str, pfdl_base_classes: PFDLBaseClasses = PFDLBaseClasses("pfdl_scheduler")
) -> Tuple[bool, Union[None, Process], str]:
    """Loads the content of the program from either the given path or the PFDL program directly and calls the parse_string function.

    Args:
        program: Either a path to the PFDL file or directly the PFDL program as a string.

    Returns:
        A boolan indicating validity of the PFDL file, the content of the file, and the
        process object if so, otherwise None.
    """
    pfdl_string, file_path = extract_content_and_file_path(program)
    return *parse_string(pfdl_string, file_path, pfdl_base_classes=pfdl_base_classes), pfdl_string


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


def extract_content_and_file_path(program: str) -> Tuple[str, str]:
    """Extracts the file path and loads the PFDL string for a given program.

    Args:
        program: Either a path to the PFDL file or directly the PFDL program as a string.

    Returns:
        The content of the PFDL file as a string and the file path if it is contained in given the program,
        otherwise an empty string.

    """
    file_path = ""
    if os.path.exists(program):
        # PFDL program was passed as a file path
        file_path = program
        pfdl_string = load_file(program)
    else:
        # expect program to contain a PFDL string
        pfdl_string = program

    return (pfdl_string, file_path)


def load_file(file_path: str) -> str:
    """Loads the content of the file from the given path.

    Returns:
        The content of the file as a string.
    """
    pfdl_string = ""
    with open(file_path, "r", encoding="utf-8") as file:
        pfdl_string = file.read()
    return pfdl_string
