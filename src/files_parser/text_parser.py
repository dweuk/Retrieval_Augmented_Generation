#!/usr/bin/env python3
# ########################################################################### #
#   shebang: 1                                                                #
#                                                          :::      ::::::::  #
#   text_parser.py                                       :+:      :+:    :+:  #
#                                                      +:+ +:+         +:+    #
#   By: npapot <npapot@student.42perpignan.fr>       +#+  +:+       +#+       #
#                                                  +#+#+#+#+#+   +#+          #
#   Created: 2026/06/15 23:39:22 by npapot              #+#    #+#            #
#   Updated: 2026/06/16 12:05:04 by npapot             ###   ########.fr      #
#                                                                             #
# ########################################################################### #

from .base_parser import BaseParser
from pathlib import Path


class TextParser(BaseParser):

    def extract_text(self, file_path: Path) -> str:
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                return f.read()
        except Exception as e:
            print(f"Error reading text file {file_path}: {e}")
            return ""
