#!/usr/bin/env python3
from .base_parser import BaseParser
from pathlib import Path
import json
import yaml  # type: ignore
import tomli
from typing import Any
from langchain_text_splitters import RecursiveJsonSplitter


class DictParser(BaseParser):
    def extract_text(self, file_path: Path) -> str:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            extension = file_path.suffix.lower()
            data: dict[str, Any] = {}

            if extension == '.json':
                data = json.loads(content)
            elif extension in ['.yaml', '.yml']:
                data = yaml.safe_load(content)
            elif extension == '.toml':
                data = tomli.loads(content)
            else:
                return content

            json_splitter = RecursiveJsonSplitter(max_chunk_size=1500)
            chunks = json_splitter.split_text(json_data=data)

            return "\n\n".join(chunks)

        except Exception as e:
            print(f"Error reading dict file {file_path}: {e}")
            return ""
