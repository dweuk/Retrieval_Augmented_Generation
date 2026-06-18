#!/usr/bin/env python3
# ########################################################################### #
#   shebang: 1                                                                #
#                                                          :::      ::::::::  #
#   rag_orchestrator.py                                  :+:      :+:    :+:  #
#                                                      +:+ +:+         +:+    #
#   By: npapot <npapot@student.42perpignan.fr>       +#+  +:+       +#+       #
#                                                  +#+#+#+#+#+   +#+          #
#   Created: 2026/06/11 11:47:19 by npapot              #+#    #+#            #
#   Updated: 2026/06/18 16:10:31 by npapot             ###   ########.fr      #
#                                                                             #
# ########################################################################### #

from pathlib import Path
from typing import Generator, Any

from src.files_parser.parser_factory import ParserFactory
from src.hybrid_retrieval.best_matching_25 import BestMatching25
from langchain_text_splitters import (
    RecursiveCharacterTextSplitter,
    Language,
)
from src.basemodel_config import Prompt


class RagOrchestrator:
    def __init__(self) -> None:
        self.parser_factory = ParserFactory()
        self.bm25 = BestMatching25()
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
        self.chunks: list[str] = []

    def get_right_splitter(
            self,
            file_format: str
            ) -> RecursiveCharacterTextSplitter:
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
            return []

        extracted_text: str = parser.extract_text(file_path)

        if not extracted_text:
            return []

        splitter = self.get_right_splitter(file_format)
        return splitter.split_text(extracted_text)

    def ingest(
            self,
            data_directory: Path = Path(
                "/Users/noepapot/informatic/ecole_42/circle_4/RAG/vllm-0.10.1"
            ),
            chunk_size: int = 1500
            ) -> None:
        self.overlap: int = chunk_size // 20
        self.max_size: int = chunk_size + self.overlap

        if isinstance(data_directory, str):
            data_directory = Path(data_directory)

        print(f"Starting ingestion on directory: {data_directory}")
        print(
            f"Chunk size is set to: {chunk_size} "
            f"with overlap {self.overlap}"
        )

        total_chunks = 0
        for file_path in self._get_all_files(data_directory):
            file_chunks = self.ingest_helper(file_path)
            if file_chunks:
                self.chunks.extend(file_chunks)
                total_chunks += len(file_chunks)

        print(
            f"\nExtraction Complete! Total chunks ready "
            f"for WORK: {total_chunks}\n\n"
        )

    def index(self, max_chunk_size: int = 1500) -> None:
        self.bm25.index_da_chuncks(self.chunks)

    def test_bm25s(self, query: str) -> None:
        self.ingest()
        self.index()
        print(f"\n--- Testing Search for: '{query}' ---")
        self.bm25.query_da_corpus(query, k_size=3, print_yes=False)

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
