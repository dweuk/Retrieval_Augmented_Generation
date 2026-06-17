#!/usr/bin/env python3
# ########################################################################### #
#   shebang: 1                                                                #
#                                                          :::      ::::::::  #
#   code_parser.py                                       :+:      :+:    :+:  #
#                                                      +:+ +:+         +:+    #
#   By: npapot <npapot@student.42perpignan.fr>       +#+  +:+       +#+       #
#                                                  +#+#+#+#+#+   +#+          #
#   Created: 2026/06/16 11:03:50 by npapot              #+#    #+#            #
#   Updated: 2026/06/17 21:58:09 by npapot             ###   ########.fr      #
#                                                                             #
# ########################################################################### #


from ..base_parser import BaseParser
from pathlib import Path
# from tree_sitter import Language, Parser
# import tree_sitter_languages


class CodeParser(BaseParser):

    def _extract_text(self, file_path: Path) -> str:
        try:
            with open(file_path) as f:
                return f.read()

        except Exception as e:
            print(f"Error reading PDF {file_path}: {e}")
            return ""
