# Copyright The PFDL Contributors
#
# Licensed under the MIT License.
# For details on the licensing terms, see the LICENSE file.
# SPDX-License-Identifier: MIT

"""Merges multiple grammar files into a single grammar file."""

import argparse
import re
import subprocess
from pathlib import Path
from typing import Dict, List

PLUGIN_ENTRY_POINT = "// {Plugin_Move_To_Front}"
LEXER_PLUGIN_INSERTION_POINT = "// {Plugin_Insertion_Point}"

# Regular expression to match grammar rules including the custom entry point for plugins
rule_pattern = re.compile(r"((\/\/\s*\{Plugin_Move_To_Front\}\s*\n)?\w+\s*:\s*[^;]+;)")


def extract_rules(grammar_content: str) -> Dict[str, str]:
    """Extracts rules from a given grammar content while preserving the original formatting.

    Args:
        grammar_content: The entire content of the grammar

    Returns:
        A dictionary of rule names and their entire formatted content.
    """
    rules = {}
    for match in rule_pattern.finditer(grammar_content):
        rule = match.group(0)
        rule_name = rule.split(":")[0].strip()
        rules[rule_name] = rule
    return rules


def merge_parser(base_grammar: str, new_grammar: str) -> str:
    """Merges two parser contents while preserving the format of the base grammar.

    Args:
        base_grammar: The base grammar content.
        new_grammar: The new grammar content to be merged.

    Returns:
        The merged grammar content as a string.
    """
    base_rules = extract_rules(base_grammar)
    new_rules = extract_rules(new_grammar)

    merged_grammar = base_grammar  # Start with the base grammar as-is

    for rule_name, new_rule in new_rules.items():
        move_rule_to_the_front = False
        if new_rule.strip().startswith(PLUGIN_ENTRY_POINT):
            move_rule_to_the_front = True
            new_rule = new_rule.replace(PLUGIN_ENTRY_POINT, "").strip()
            rule_name = rule_name.replace(PLUGIN_ENTRY_POINT, "").strip()

        if rule_name in base_rules:
            # Add new alternative to the existing rule
            base_rule = base_rules[rule_name]
            # Find the position before the semicolon to insert the new alternative
            if move_rule_to_the_front:
                insert_pos = base_rule.find(":") + 1
                merged_grammar = merged_grammar.replace(
                    base_rule,
                    base_rule[:insert_pos]
                    + new_rule.split(":")[1].strip().rstrip(";")
                    + " | "
                    + base_rule[insert_pos:],
                )
            else:
                insert_pos = base_rule.rfind(";")
                merged_grammar = merged_grammar.replace(
                    base_rule,
                    base_rule[:insert_pos]
                    + " | "
                    + new_rule.split(":")[1].strip().rstrip(";")
                    + base_rule[insert_pos:],
                )
        else:
            # Add new rule at the end of the grammar with appropriate formatting
            merged_grammar += "\n\n" + new_rule

    return merged_grammar


def merge_lexer(base_lexer: str, new_lexer: str) -> str:
    """Merges two lexer contents while preserving the format of the base lexer.

    Args:
        base_lexer: The base lexer content.
        new_lexer: The new lexer content to be merged.

    Returns:
        The merged lexer content as a string.
    """
    merged_grammar = base_lexer  # Start with the base grammar as-is

    insert_position = merged_grammar.find(LEXER_PLUGIN_INSERTION_POINT)
    merged_grammar = (
        merged_grammar[:insert_position] + new_lexer + "\n\n" + merged_grammar[insert_position:]
    )

    return merged_grammar


def merge_multiple_parsers(parser_files: List[str]) -> str:
    """Merge multiple grammar files.

    Args:
        parser_files: A list of file paths to the grammar files.

    Returns:
        The merged grammar content as a string.
    """
    with open(parser_files[0], "r") as file:
        base_grammar = file.read()

    for grammar_file in parser_files[1:]:
        with open(grammar_file, "r") as file:
            new_grammar = file.read()
        base_grammar = merge_parser(base_grammar, new_grammar)
    return base_grammar


def merge_multiple_lexers(lexer_files: List[str]) -> str:
    """Merge multiple lexer files.

    Args:
        lexer_files: A list of file paths to the lexer files.

    Returns:
        The merged lexer content as a string.
    """
    with open(lexer_files[0], "r") as file:
        base_grammar = file.read()

    for grammar_file in lexer_files[1:]:
        with open(grammar_file, "r") as file:
            new_grammar = file.read()
        base_grammar = merge_lexer(base_grammar, new_grammar)
    return base_grammar


if __name__ == "__main__":

    script_description = """
    This script merges multiple grammar and lexer files into single grammar and lexer files respectively.
    It then generates the corresponding ANTLR parser and lexer files for Python3.

    Usage:
        python grammar_merge.py <parser_files> <lexer_files>

    Arguments:
        parser_files: List of file paths to the grammar files to be merged.
        lexer_files: List of file paths to the lexer files to be merged.

    Example:
        python grammar_merge.py parser1.g4 parser2.g4 lexer1.g4 lexer2.g4
    """
    parser = argparse.ArgumentParser(
        prog="PFDL grammar merge script",
        description=script_description,
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument("parser_files", type=str, nargs="+")
    parser.add_argument("lexer_files", type=str, nargs="+")

    args = parser.parse_args()

    parser_files = ["../../pfdl_grammar/PFDLParser.g4", *args.parser_files]
    merged_parser = merge_multiple_parsers(parser_files)

    lexer_files = ["../../pfdl_grammar/PFDLLexer.g4", *args.lexer_files]
    merged_lexer = merge_multiple_lexers(lexer_files)

    file = Path("parser/PFDLParser.g4")
    file.parent.mkdir(parents=True, exist_ok=True)
    file.write_text(merged_parser)

    file = Path("parser/PFDLLexer.g4")
    file.write_text(merged_lexer)

    subprocess.call(
        [
            "antlr4",
            "-v",
            "4.9.3",
            "-Dlanguage=Python3",
            "-visitor",
            "parser/PFDLLexer.g4",
            "parser/PFDLParser.g4",
        ]
    )
