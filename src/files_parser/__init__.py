#!/usr/bin/env python3
# ########################################################################### #
#   shebang: 1                                                                #
#                                                          :::      ::::::::  #
#   __init__.py                                          :+:      :+:    :+:  #
#                                                      +:+ +:+         +:+    #
#   By: npapot <npapot@student.42perpignan.fr>       +#+  +:+       +#+       #
#                                                  +#+#+#+#+#+   +#+          #
#   Created: 2026/03/18 14:06:02 by npapot              #+#    #+#            #
#   Updated: 2026/06/18 00:12:09 by npapot             ###   ########.fr      #
#                                                                             #
# ########################################################################### #

__version__ = "1.0.0"

__author__ = "Master npapot"

from .base_parser import BaseParser
from .text_parser import TextParser
from .pdf_parser_tabular import PDFParserTabular
from .pdf_parser_text import PDFParserText
from .dict_parser import DictParser
from .parser_factory import ParserFactory
from .code_parser import CodeParser
from .python_parser import PythonParser

__all__ = [
    "BaseParser",
    "TextParser",
    "PDFParserTabular",
    "PDFParserText",
    "DictParser",
    "ParserFactory",
    "CodeParser",
    "PythonParser",
]
