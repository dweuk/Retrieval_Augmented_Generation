#!/usr/bin/env python3
# ########################################################################### #
#   shebang: 1                                                                #
#                                                          :::      ::::::::  #
#   __init__.py                                          :+:      :+:    :+:  #
#                                                      +:+ +:+         +:+    #
#   By: npapot <npapot@student.42perpignan.fr>       +#+  +:+       +#+       #
#                                                  +#+#+#+#+#+   +#+          #
#   Created: 2026/03/18 14:06:02 by npapot              #+#    #+#            #
#   Updated: 2026/06/16 11:50:39 by npapot             ###   ########.fr      #
#                                                                             #
# ########################################################################### #

__version__ = "1.0.0"

__author__ = "Master npapot"

from .text_parser import TextParser
from .pdf_parser_tabular import PDFParserTabular
from .pdf_parser_text import PDFParserText


__all__ = ["TextParser", "PDFParserTabular", "PDFParserText"]
