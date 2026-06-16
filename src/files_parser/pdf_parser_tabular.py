#!/usr/bin/env python3
# ########################################################################### #
#   shebang: 1                                                                #
#                                                          :::      ::::::::  #
#   pdf_parser_tabular.py                                :+:      :+:    :+:  #
#                                                      +:+ +:+         +:+    #
#   By: npapot <npapot@student.42perpignan.fr>       +#+  +:+       +#+       #
#                                                  +#+#+#+#+#+   +#+          #
#   Created: 2026/06/16 11:03:50 by npapot              #+#    #+#            #
#   Updated: 2026/06/16 11:53:52 by npapot             ###   ########.fr      #
#                                                                             #
# ########################################################################### #


from .base_parser import BaseParser
from pathlib import Path
import pdfplumber        # type: ignore


class PDFParserTabular(BaseParser):
    def __init__(self) -> None:
        pass

    def _extract_text(self, file_path: Path) -> str:
        extracted_text = []

        try:
            with pdfplumber.open(file_path) as document:
                for page in document.pages:
                    extracted = page.extract_text()
                    if extracted:
                        extracted_text.append(extracted)

        except Exception as e:
            print(f"Error reading PDF {file_path}: {e}")
            return ""

        return "\n".join(extracted_text)
