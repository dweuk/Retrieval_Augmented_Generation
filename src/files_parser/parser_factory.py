#!/usr/bin/env python3
# ########################################################################### #
#   shebang: 1                                                                #
#                                                          :::      ::::::::  #
#   parser_factory.py                                    :+:      :+:    :+:  #
#                                                      +:+ +:+         +:+    #
#   By: npapot <npapot@student.42perpignan.fr>       +#+  +:+       +#+       #
#                                                  +#+#+#+#+#+   +#+          #
#   Created: 2026/06/16 12:00:40 by npapot              #+#    #+#            #
#   Updated: 2026/06/16 12:17:33 by npapot             ###   ########.fr      #
#                                                                             #
# ########################################################################### #

from .pdf_parser_tabular import PDFParserTabular
from .pdf_parser_text import PDFParserText
from .text_parser import TextParser
from .base_parser import BaseParser
from typing import Type

class ParserFactory:
    def __init__(self) -> None:
        self.parser_classes: dict[str, Type[BaseParser]] = {
                ".txt": TextParser,
                ".md": TextParser,
                ".py": TextParser,
            }

        self.active_parser: dict[str, BaseParser] = {}