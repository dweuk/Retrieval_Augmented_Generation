#!/usr/bin/env python3
from .base_parser import BaseParser
from pathlib import Path


class DictParser(BaseParser):
    def _extract_text(self, file_path: Path) -> str:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            print(f"Error reading dict file {file_path}: {e}")
            return ""
