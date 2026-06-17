#!/usr/bin/env python3
from .base_parser import BaseParser
from pathlib import Path
from langchain_text_splitters import MarkdownHeaderTextSplitter


class MdParser(BaseParser):
    def extract_text(self, file_path: Path) -> str:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            headers_to_split_on = [
                ("#", "Header 1"),
                ("##", "Header 2"),
                ("###", "Header 3"),
                ("####", "Header 4"),
            ]

            markdown_splitter = MarkdownHeaderTextSplitter(
                headers_to_split_on=headers_to_split_on
            )
            md_header_splits = markdown_splitter.split_text(content)

            extracted_chunks = []
            for split in md_header_splits:
                header_path = " > ".join(split.metadata.values())
                text = split.page_content
                if header_path:
                    extracted_chunks.append(f"[{header_path}]\n{text}")
                else:
                    extracted_chunks.append(text)

            return "\n\n".join(extracted_chunks)

        except Exception as e:
            print(f"Error reading Markdown file {file_path}: {e}")
            return ""
