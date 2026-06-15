#!/usr/bin/env python3
# ########################################################################### #
#   shebang: 1                                                                #
#                                                          :::      ::::::::  #
#   rag_pipeline.py                                        :+:      :+:    :+:  #
#                                                      +:+ +:+         +:+    #
#   By: npapot <npapot@student.42perpignan.fr>       +#+  +:+       +#+       #
#                                                  +#+#+#+#+#+   +#+          #
#   Created: 2026/06/11 11:47:19 by npapot              #+#    #+#            #
#   Updated: 2026/06/11 11:50:33 by npapot             ###   ########.fr      #
#                                                                             #
# ########################################################################### #

from pathlib import Path
from typing import Generator, Any
from langchain_text_splitters import RecursiveCharacterTextSplitter
from src.basemodel_config import Prompt


class RAGPipeline:
    def __init__(self) -> None:
        pass

    def ingest(
            self,
            data_directory: Path = Path("/Users/noepapot/informatic/ecole_42/circle_4/RAG/vllm-0.10.1"),
            chunk_size: int = 1500
            ) -> None:
        overlap = 50
        print(f"Starting ingestion on directory: {data_directory}")
        print(f"Chunk size is set to: {chunk_size} with overlap {overlap}")
        yielder = self._get_all_path(data_directory)
        print(next(yielder))

    def prompt(self, prompt: "Prompt", top_k: int = 5) -> None:
        print(f"User Prompt: {prompt}")
        print(f"Retrieving top {top_k} chunks")

    def model(self, model_name: str = "Qwen/Qwen3-0.6B") -> None:
        print(f"User model {model_name}")

    def _get_all_path(self, directory_path: Path) -> Generator[Path, Any, Any]:
        for file_path in directory_path.rglob("*"):
            if file_path.is_file():
                yield file_path