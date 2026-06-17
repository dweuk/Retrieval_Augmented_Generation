#!/usr/bin/env python3
# ########################################################################### #
#   shebang: 1                                                                #
#                                                          :::      ::::::::  #
#   python_parser.py                                     :+:      :+:    :+:  #
#                                                      +:+ +:+         +:+    #
#   By: npapot <npapot@student.42perpignan.fr>       +#+  +:+       +#+       #
#                                                  +#+#+#+#+#+   +#+          #
#   Created: 2026/06/16 11:03:50 by npapot              #+#    #+#            #
#   Updated: 2026/06/16 15:07:14 by npapot             ###   ########.fr      #
#                                                                             #
# ########################################################################### #


from .base_parser import BaseParser
from pathlib import Path
import ast              # type: ignore


class PythonParser(BaseParser):

    def _extract_text(self, file_path: Path) -> str:
        extracted_text = []

        try:
            with open(self.filepath, 'r', encoding='utf-8') as f:
                src_code = f.read()
                # Transformer le code en un arbre syntaxique abstrait
            tree = ast.parse(src_code)
            for node in ast.walk(tree):
                pass

        except Exception as e:
            print(f"Error reading PDF {file_path}: {e}")
            return ""

        return "\n".join(extracted_text)
