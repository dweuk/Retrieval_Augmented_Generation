#!/usr/bin/env python3
# ########################################################################### #
#   shebang: 1                                                                #
#                                                          :::      ::::::::  #
#   python_parser.py                                     :+:      :+:    :+:  #
#                                                      +:+ +:+         +:+    #
#   By: npapot <npapot@student.42perpignan.fr>       +#+  +:+       +#+       #
#                                                  +#+#+#+#+#+   +#+          #
#   Created: 2026/06/16 11:03:50 by npapot              #+#    #+#            #
#   Updated: 2026/06/17 19:05:11 by npapot             ###   ########.fr      #
#                                                                             #
# ########################################################################### #


from .base_parser import BaseParser
from pathlib import Path
import ast              # type: ignore


class RagCodeVisitor(ast.NodeVisitor):
    def __init__(self, src_code: str) -> None:
        self.src_code = src_code
        self.current_class = None
        self.extracted_data: list = []

    def visit_ClassDef(self, node):
        self.current_class = node.name

        doc = ast.get_docstring(node)
        self.extracted_data.append({
            "type": "class",
            "class_name": node.name,
            "docstring": doc
        })

        self.generic_visit(node)
        self.current_class = None

    def visit_FunctionDef(self, node) -> None:
        doc = ast.get_docstring(node)
        params = [arg.arg for arg in node.args.args]

        if self.current_class is not None:
            is_method = True
        else:
            is_method = False

        print(params)
        if is_method and params and params[0] == 'self':
            params.pop(0)


        func_code = ast.get_source_segment(self.original_source, node)

        self.extracted_data.append({
            "type": "method" if is_method else "function",
            "name": node.name,
            "parent_class": self.current_class,
            "parameters": params,
            "docstring": doc,
            "code": func_code
        })

        self.generic_visit(node)

    def run_rag_code_visitor(self, node) -> None:
        if node:
            self.visit_ClassDef()


class PythonParser(BaseParser):

    def format_chuncks(self, visitor: RagCodeVisitor) -> str:
        extracted_text: list = []

        for item in visitor.extracted_data:
            if item["type"] == "class":
                chunk_text = (
                    f"Class: {item['class_name']}\nDocstring: {item['docstring']}"
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

    def _extract_text(self, file_path: Path) -> str:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                src_code: str = f.read()

            tree = ast.parse(src_code)

            visitor = RagCodeVisitor(src_code)
            visitor.visit(tree)

            extracted_text: str = self.format_chuncks(visitor)
            print(ast.dump(tree, indent=4))

            return extracted_text

        except Exception as e:
            print(f"Error reading Python file {file_path}: {e}")
            return ""


if __name__ == "__main__":
    python_parser = PythonParser()
    extracted_text: str = python_parser._extract_text(Path("/Users/noepapot/informatic/ecole_42/circle_4/RAG/src/files_parser/test.py"))
    print(extracted_text)
