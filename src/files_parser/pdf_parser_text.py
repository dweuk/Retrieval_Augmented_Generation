#!/usr/bin/env python3
# ########################################################################### #
#   shebang: 1                                                                #
#                                                          :::      ::::::::  #
#   pdf_parser_text.py                                   :+:      :+:    :+:  #
#                                                      +:+ +:+         +:+    #
#   By: npapot <npapot@student.42perpignan.fr>       +#+  +:+       +#+       #
#                                                  +#+#+#+#+#+   +#+          #
#   Created: 2026/06/16 11:03:50 by npapot              #+#    #+#            #
#   Updated: 2026/06/16 11:29:44 by npapot             ###   ########.fr      #
#                                                                             #
# ########################################################################### #


from .base_parser import BaseParser
from pathlib import Path
import fitz


class PDFParserText(BaseParser):
    def __init__(self) -> None:
        pass

    def _extract_text(self, file_path: Path) -> str:
        extracted_text = []

        try:
            with fitz.open(file_path) as document:
                for page_num in range(len(document)):
                    page = document.load_page(page_num)
                    page_text = page.get_text()
                    extracted_text.append(page_text)

        except Exception as e:
            print(f"Error reading PDF {file_path}: {e}")
            return ""

        return "\n".join(extracted_text)
