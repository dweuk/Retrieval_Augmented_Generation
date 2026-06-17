#!/usr/bin/env python3
# ########################################################################### #
#   shebang: 1                                                                #
#                                                          :::      ::::::::  #
#   code_parser.py                                       :+:      :+:    :+:  #
#                                                      +:+ +:+         +:+    #
#   By: npapot <npapot@student.42perpignan.fr>       +#+  +:+       +#+       #
#                                                  +#+#+#+#+#+   +#+          #
#   Created: 2026/06/16 11:03:50 by npapot              #+#    #+#            #
#   Updated: 2026/06/17 22:45:03 by npapot             ###   ########.fr      #
#                                                                             #
# ########################################################################### #

from .base_parser import BaseParser
from pathlib import Path
from tree_sitter import Parser
import tree_sitter_languages  # type: ignore
from typing import Any


class CodeParser(BaseParser):
    def __init__(self) -> None:
        self.parser = Parser()

        self.ext_to_lang = {
            ".cpp": "cpp",
            ".c": "c",
            ".h": "c",
            ".hpp": "cpp",
            ".cuh": "cpp",
            ".cu": "cpp",
            ".js": "javascript",
            ".ts": "typescript",
            ".java": "java",
            ".go": "go",
            ".rs": "rust"
        }

        self.queries = {
            "c": """
                (function_definition
                    declarator: (function_declarator
                        declarator: (identifier) @name)) @function
            """,
            "cpp": """
                (function_definition
                    declarator: (function_declarator
                        declarator: (identifier) @name)) @function
                (function_definition
                    declarator: (function_declarator
                        declarator: (field_identifier) @name)) @function
                (class_specifier name: (type_identifier) @name) @class
            """,
            "javascript": """
                (function_declaration name: (identifier) @name) @function
                (class_declaration name: (identifier) @name) @class
                (method_definition
                    name: (property_identifier) @name) @function
            """,
            "typescript": """
                (function_declaration name: (identifier) @name) @function
                (class_declaration name: (type_identifier) @name) @class
                (method_definition
                    name: (property_identifier) @name) @function
            """,
            "java": """
                (method_declaration name: (identifier) @name) @function
                (class_declaration name: (identifier) @name) @class
            """,
            "go": """
                (function_declaration name: (identifier) @name) @function
                (method_declaration
                    name: (field_identifier) @name) @function
                (type_declaration
                    (type_spec
                        name: (type_identifier) @name
                        type: (struct_type))) @class
            """,
            "rust": """
                (function_item name: (identifier) @name) @function
                (struct_item name: (type_identifier) @name) @class
                (impl_item type: (type_identifier) @name) @class
            """
        }

    def _extract_node_data(
        self, captures: list[tuple[Any, str]], src_code: str
    ) -> dict[int, dict[str, str]]:
        node_data: dict[int, dict[str, str]] = {}
        for node, capture_name in captures:
            parent_block = node
            valid_types = [
                'function_definition',
                'class_specifier',
                'function_declaration',
                'class_declaration',
                'method_definition',
                'method_declaration',
                'type_declaration',
                'function_item',
                'struct_item',
                'impl_item'
            ]

            while parent_block and parent_block.type not in valid_types:
                parent_block = parent_block.parent

            if not parent_block:
                parent_block = node

            block_id = parent_block.id
            if block_id not in node_data:
                func_code = src_code[
                    parent_block.start_byte:parent_block.end_byte
                ]
                node_data[block_id] = {
                    "type": "Code Block",
                    "name": "Unknown",
                    "code": func_code
                }

            if capture_name in ["function", "class"]:
                node_data[block_id]["type"] = capture_name.capitalize()
            elif capture_name == "name":
                name = src_code[node.start_byte:node.end_byte]
                node_data[block_id]["name"] = name
        return node_data

    def _extract_text(self, file_path: Path) -> str:
        try:
            file_format = file_path.suffix.lower()
            str_langage = self.ext_to_lang.get(file_format)

            with open(file_path, 'r', encoding='utf-8') as f:
                src_code = f.read()

            if not str_langage or str_langage not in self.queries:
                return src_code

            language = tree_sitter_languages.get_language(str_langage)
            self.parser.language = language
            tree = self.parser.parse(bytes(src_code, "utf8"))

            query = language.query(self.queries[str_langage])
            captures = query.captures(tree.root_node)

            node_data = self._extract_node_data(captures, src_code)

            extracted_chunks = []
            for data in node_data.values():
                extracted_data = (
                    f"{data['type']}: {data['name']}\n"
                    f"Code:\n"
                    f"{data['code']}"
                )
                extracted_chunks.append(extracted_data)

            r_val = "\n\n".join(extracted_chunks)
            if extracted_chunks:
                return r_val
            else:
                return src_code

        except Exception as e:
            print(f"Error reading file {file_path}: {e}")
            return ""
