#!/usr/bin/env python3
# ########################################################################### #
#   shebang: 1                                                                #
#                                                          :::      ::::::::  #
#   parser_factory.py                                    :+:      :+:    :+:  #
#                                                      +:+ +:+         +:+    #
#   By: npapot <npapot@student.42perpignan.fr>       +#+  +:+       +#+       #
#                                                  +#+#+#+#+#+   +#+          #
#   Created: 2026/06/16 12:00:40 by npapot              #+#    #+#            #
#   Updated: 2026/06/18 00:14:11 by npapot             ###   ########.fr      #
#                                                                             #
# ########################################################################### #

from .base_parser import BaseParser
from .text_parser import TextParser
from .dict_parser import DictParser
from .pdf_parser_tabular import PDFParserTabular
from .pdf_parser_text import PDFParserText
from .md_parser import MdParser
from .code_parser import CodeParser
from .python_parser import PythonParser
from typing import Type
from pathlib import Path
import fitz  # type: ignore


class ParserFactory:
    def __init__(self) -> None:
        self.parser_classes: dict[str, Type[BaseParser]] = {
                ".txt": TextParser,
                '.sh': TextParser,
                '.csv': TextParser,
                ".md": MdParser,
                ".html": TextParser,
                '.rst': TextParser,
                '.cpp': CodeParser,
                '.cu': CodeParser,
                '.c': CodeParser,
                '.h': CodeParser,
                '.hpp': CodeParser,
                '.cuh': CodeParser,
                '.js': CodeParser,
                '.ts': CodeParser,
                '.go': CodeParser,
                '.rs': CodeParser,
                ".py": PythonParser,
                '.java': CodeParser,
                '.json': DictParser,
                '.toml': DictParser,
                '.yaml': DictParser
            }

        self.active_parsers: dict[str, BaseParser] = {}

    def _is_tabular_pdf(self, file_path: Path) -> bool:
        try:
            with fitz.open(file_path) as doc:
                print(doc)
                page = doc[0]
                if len(page.get_drawings()) > 20:
                    return True
                return False
        except Exception:
            return False

    def get_parser(self, file_path: Path) -> BaseParser | None:
        file_format = file_path.suffix.lower()

        if file_format == "pdf":
            return (self._pdf_parser(file_format, file_path))

        if file_format not in self.parser_classes:
            return None

        if file_format not in self.active_parsers:
            BlueprintClass = self.parser_classes[file_format]
            self.active_parsers[file_format] = BlueprintClass()
            print(f"Instantiating {BlueprintClass}!!!")

        return self.active_parsers[file_format]

    def _pdf_parser(self, file_fromat: str, file_path: Path) -> BaseParser:
        if self._is_tabular_pdf(file_path):
            if 'pdf_tabular' not in self.active_parsers:
                print("Instantiating PDF Tabular Parser!!!")
                self.active_parsers['pdf_tabular'] = PDFParserTabular()
            return self.active_parsers['pdf_tabular']
        else:
            if 'pdf_text' not in self.active_parsers:
                print("Instantiating PDF Text Parser!!!")
                self.active_parsers['pdf_text'] = PDFParserText()
            return self.active_parsers['pdf_text']
