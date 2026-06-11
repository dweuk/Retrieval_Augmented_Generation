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
import fire
from src.basemodel_config import Prompt


class RAGPipeline:
    def __init__(self) -> None:
        pass

    def ingest(
            self,
            data_directory: Path = "../vllm-0.10.1",
            chunk_size: int = 1500,
            overlap: int = 50
            ) -> None:
        print(f"Starting ingestion on directory: {data_directory}")
        print(f"Chunk size is set to: {chunk_size} with overlap {overlap}")

    def prompt(self, prompt: "Prompt", top_k: int = 5) -> None:
        print(f"User Prompt: {prompt}")
        print(f"Retrieving top {top_k} chunks")

    def model(self, model_name: str = "Qwen/Qwen3-0.6B") -> None:
        print(f"User model {model_name}")