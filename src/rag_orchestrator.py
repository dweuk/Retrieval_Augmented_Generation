#!/usr/bin/env python3
# ########################################################################### #
#   shebang: 1                                                                #
#                                                          :::      ::::::::  #
#   rag_orchestrator.py                                  :+:      :+:    :+:  #
#                                                      +:+ +:+         +:+    #
#   By: npapot <npapot@student.42perpignan.fr>       +#+  +:+       +#+       #
#                                                  +#+#+#+#+#+   +#+          #
#   Created: 2026/06/11 11:47:19 by npapot              #+#    #+#            #
#   Updated: 2026/06/18 00:37:12 by npapot             ###   ########.fr      #
#                                                                             #
# ########################################################################### #

from pathlib import Path
from typing import Generator, Any

from src.files_parser.parser_factory import ParserFactory
from langchain_text_splitters import (  # type: ignore
    RecursiveCharacterTextSplitter,
    Language,
)
from src.basemodel_config import Prompt


class RagOrchestrator:
    def __init__(self) -> None:
        self.parser_factory = ParserFactory()
        self.lang_mapping = {
            ".py": Language.PYTHON,
            ".js": Language.JS,
            ".ts": Language.TS,
            ".java": Language.JAVA,
            ".cpp": Language.CPP,
            ".c": Language.CPP,
            ".go": Language.GO,
            ".rs": Language.RUST,
            ".md": Language.MARKDOWN,
            ".html": Language.HTML
        }

    def get_right_splitter(self, file_format: str) -> Any:
        lang = self.lang_mapping.get(file_format)
        if lang:
            splitter = RecursiveCharacterTextSplitter.from_language(
                language=lang,
                chunk_size=self.max_size,
                chunk_overlap=self.overlap
            )
        else:
            splitter = RecursiveCharacterTextSplitter(
                chunk_size=self.max_size, chunk_overlap=self.overlap
            )

        return splitter

    def ingest_helper(self, file_path: Path) -> list[str]:
        file_format = file_path.suffix.lower()
        parser = self.parser_factory.get_parser(file_path)

        if parser is None:
            print(f"skipping the file {file_path}!!\n")
            return []

        print(f"Parsing {file_path}")
        extracted_text: str = parser.extract_text(file_path)
        final_block: list[str] = []

        if not extracted_text:
            print(f"Nothing in the file {file_path}")
            return []

        splitter = self.get_right_splitter(file_format)

        for block in extracted_text.split("\n\n"):
            if len(block) > self.max_size:
                final_block.extend(splitter.split_text(block))
            else:
                final_block.append(block)
        return final_block

    def ingest(
            self,
            data_directory: Path = Path(
                "/Users/noepapot/informatic/ecole_42/circle_4/RAG/vllm-0.10.1"
            ),
            chunk_size: int = 1500
            ) -> None:
        self.overlap: int = chunk_size // 20
        self.max_size: int = chunk_size + self.overlap
        print(f"Starting ingestion on directory: {data_directory}")
        print(
            f"Chunk size is set to: {chunk_size} "
            f"with overlap {self.overlap}"
        )
        for file_path in self._get_all_files(data_directory):
            self.ingest_helper(file_path)

    def prompt(self, prompt: "Prompt", top_k: int = 5) -> None:
        print(f"User Prompt: {prompt}")
        print(f"Retrieving top {top_k} chunks")

    def model(self, model_name: str = "Qwen/Qwen3-0.6B") -> None:
        print(f"User model {model_name}")

    def _get_all_files(
                    self,
                    directory_path: Path
                    ) -> Generator[Path, Any, Any]:
        for file_path in directory_path.rglob("*"):
            if file_path.is_file():
                yield file_path
