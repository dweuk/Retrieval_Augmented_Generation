#!/usr/bin/env python3
# ########################################################################### #
#   shebang: 1                                                                #
#                                                          :::      ::::::::  #
#   python_parser.py                                     :+:      :+:    :+:  #
#                                                      +:+ +:+         +:+    #
#   By: npapot <npapot@student.42perpignan.fr>       +#+  +:+       +#+       #
#                                                  +#+#+#+#+#+   +#+          #
#   Created: 2026/06/16 11:03:50 by npapot              #+#    #+#            #
#   Updated: 2026/06/17 22:39:09 by npapot             ###   ########.fr      #
#                                                                             #
# ########################################################################### #


from .base_parser import BaseParser
from pathlib import Path
import ast
from typing import Any


class RagCodeVisitor(ast.NodeVisitor):
    def __init__(self, src_code: str) -> None:
        self.src_code = src_code
        self.current_class: str | None = None
        self.extracted_data: list[dict[str, Any]] = []

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        self.current_class = node.name

        doc = ast.get_docstring(node)
        self.extracted_data.append({
            "type": "class",
            "class_name": node.name,
            "docstring": doc
        })

        self.generic_visit(node)
        self.current_class = None

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        doc = ast.get_docstring(node)
        params = [arg.arg for arg in node.args.args]

        if self.current_class is not None:
            is_method = True
        else:
            is_method = False

        print(params)
        if is_method and params and params[0] == 'self':
            params.pop(0)

        func_code = ast.get_source_segment(self.src_code, node)

        self.extracted_data.append({
            "type": "method" if is_method else "function",
            "name": node.name,
            "parent_class": self.current_class,
            "parameters": params,
            "docstring": doc,
            "code": func_code
        })

        self.generic_visit(node)


class PythonParser(BaseParser):

    def extract_text(self, file_path: Path) -> str:
        extracted_text: str = ""

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                src_code: str = f.read()

            tree = ast.parse(src_code)

            visitor = RagCodeVisitor(src_code)
            visitor.visit(tree)

            extracted_text = self.format_chuncks(visitor)
            print(ast.dump(tree, indent=4))

            return extracted_text

        except Exception as e:
            print(f"Error reading Python file {file_path}: {e}")
            return ""

    def format_chuncks(self, visitor: RagCodeVisitor) -> str:
        extracted_text: list[str] = []

        for item in visitor.extracted_data:
            if item["type"] == "class":
                chunk_text = (
                    f"Class: {item['class_name']}\n"
                    f"Docstring: {item['docstring']}"
                )
            else:
                if item['parent_class']:
                    parent = f" belonging to class {item['parent_class']}"
                else:
                    ""
                if parent != "":
                    chunk_text = (
                        f"Method: {item['name']}{parent}\n"
                        f"Parameters: {item['parameters']}\n"
                        f"Docstring: {item['docstring']}"
                    )
                else:
                    chunk_text = (
                        f"Function: {item['name']}\n"
                        f"Parameters: {item['parameters']}\n"
                        f"Docstring: {item['docstring']}"
                    )

            extracted_text.append(chunk_text)

        return "\n\n".join(extracted_text)
