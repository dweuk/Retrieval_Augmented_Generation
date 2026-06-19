#!/usr/bin/env python3
# ########################################################################### #
#   shebang: 1                                                                #
#                                                          :::      ::::::::  #
#   rag_orchestrator.py                                  :+:      :+:    :+:  #
#                                                      +:+ +:+         +:+    #
#   By: npapot <npapot@student.42perpignan.fr>       +#+  +:+       +#+       #
#                                                  +#+#+#+#+#+   +#+          #
#   Created: 2026/06/11 11:47:19 by npapot              #+#    #+#            #
#   Updated: 2026/06/19 15:36:26 by npapot             ###   ########.fr      #
#                                                                             #
# ########################################################################### #

from pathlib import Path
from typing import Generator, Any
import os
from transformers import AutoModelForCausalLM, AutoTokenizer

# from vllm import LLM, SamplingParams  # type: ignore
from src.files_parser.parser_factory import ParserFactory
from src.hybrid_retrieval import BestMatching25, FaissMatching
from src.re_ranking import ReRanker
from langchain_text_splitters import (
    RecursiveCharacterTextSplitter,
    Language,
)
from src.basemodel_config import Prompt


class RagOrchestrator:
    def __init__(self) -> None:
        self.device: str | None = None
        self.parser_factory = ParserFactory()
        self.bm25 = BestMatching25()
        self.faiss: FaissMatching | None = None
        self.re_ranker: ReRanker | None = None
        self.llm: Any = None
        self.tokenizer: Any = None
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

    def _load_llm(self, model_name: str) -> None:
        if self.llm is not None:
            return

        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.llm = AutoModelForCausalLM.from_pretrained(model_name)
        self.llm.to(self.device)
        self.llm.eval()

    def _get_faiss(self) -> FaissMatching:
        if self.faiss is None:
            self.faiss = FaissMatching()
        return self.faiss

    def _get_re_ranker(self) -> ReRanker:
        if self.re_ranker is None:
            self.re_ranker = ReRanker()
        return self.re_ranker

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

    def extend_chunks(self, data_directory: Path) -> int:
        total_chunks: int = 0
        for file_path in self._get_all_files(data_directory):
            file_chunks = self.ingest_helper(file_path)
            if file_chunks:
                self.chunks.extend(file_chunks)
                total_chunks += len(file_chunks)
        return total_chunks

    def ingest(
            self,
            data_directory: str | Path = Path("Subjects"),
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

        total_chunks = self.extend_chunks(data_directory)

        print(
            f"\nExtraction Complete! Total chunks ready "
            f"for WORK: {total_chunks}\n\n"
        )

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

    def index_helper(self, query: str, max_chunk: int) -> list[str]:
        bm25_chunks: list[str] = self.bm25.query_da_corpus(
                                            query,
                                            k_size=3,
                                            print_yes=False
                                        )
        faiss_chunks: list[str] = self._get_faiss().query_da_embedded(
                                            query,
                                            k_size=3,
                                            print_yes=False
                                        )

        combined_chunks = bm25_chunks + faiss_chunks
        unique_chunks = list(set(combined_chunks))

        best_combined_chunks = self._get_re_ranker().reclassification(
                                                    query,
                                                    unique_chunks,
                                                    max_chunk
                                                )

        return best_combined_chunks

    def _write_da_chunks(
                    self,
                    save_data: str,
                    query: str,
                    best_combined_chunks: list[str]
                ) -> None:
        chunks_dir = Path(save_data) / "chunks"
        chunks_dir.mkdir(parents=True, exist_ok=True)
        output_file = chunks_dir / "best_chunks.txt"

        with open(output_file, "w", encoding="utf-8") as f:
            f.write(f"Query: {query}\n")
            f.write("=" * 50 + "\n\n")
            for i, chunk in enumerate(best_combined_chunks):
                f.write(f"\n\n--- Winner #{i+1} ---\n")
                f.write(f"{chunk}\n\n")

            print(f"\nSaved best chunks to {output_file}\n")

    def index(
                self,
                query: str,
                max_chunks: int = 5,
                save_data: str = "data/processed",
                print_yes: bool = False
            ) -> None:
        if os.path.exists(save_data + "/faiss.index"):
            print("Libraries found on disk! Loading them instantly...")
            self.bm25.retrieve_da_data(save_data)
            self._get_faiss().retrieve_da_data(save_data)
        else:
            print("No libraries found. Starting the ingestion process...")
            self.ingest()

            if not self.chunks:
                print(
                    "🚨 CRITICAL ERROR: The data directory is empty or"
                    "invalid. Could not extract any chunks!"
                )
                return

            self.bm25.index_da_chunks(
                            self.chunks, save_data, save_to_path=True
                        )
            self._get_faiss().embed_da_chunks(
                            self.chunks, save_data, save_to_path=True
                        )

        best_combined_chunks = self.index_helper(query, max_chunks)

        if print_yes:
            print(f"\n\nTHE FINAL TOP {max_chunks} CHUNKS \n\n")
            for i, chunk in enumerate(best_combined_chunks):
                print(f"\n--- Winner #{i+1} ---")
                print(chunk)

        self._write_da_chunks(save_data, query, best_combined_chunks)

    def answer(
            self,
            query: str,
            top_k: int = 20,
            model_name: str = "Qwen/Qwen3-0.6B",
            max_tokens: int = 150,
            temperature: float = 0.7,
            top_p: float = 0.8,
            save_data: str = "data/processed",
            ) -> None:
        self.bm25.retrieve_da_data(save_data)
        self._get_faiss().retrieve_da_data(save_data)

        import torch

        if self.device is None:
            if torch.backends.mps.is_available():
                self.device = "mps"
            elif torch.cuda.is_available():
                self.device = "cuda"
            else:
                self.device = "cpu"

        best_chunks: list[str] = self.index_helper(query, top_k)
        context = "\n\n".join(best_chunks)

        final_prompt = (
                    "You are a helpful assistant. "
                    "Use only the provided context to answer the user's query."
                    " If the answer is not in the context, "
                    "say that you do not know.\n\n"
                    f"Context:\n{context}\n\n"
                    f"User's query: {query}\n"
                    "Answer: "
                )
        messages = [
                {"role": "user", "content": final_prompt},
            ]

        print("Loading LLM...")
        self._load_llm(model_name)

        inputs = self.tokenizer.apply_chat_template(
                                        messages,
                                        tokenize=True,
                                        add_generation_prompt=True,
                                        enable_thinking=False,
                                        return_dict=True,
                                        return_tensors="pt",
                                    )
        # creates PyTorch tensors that matches CUDA or MPS.
        inputs = inputs.to(self.device)

        with torch.inference_mode():
            output_ids = self.llm.generate(
                                    **inputs,
                                    max_new_tokens=max_tokens,
                                    temperature=temperature,
                                    do_sample=temperature > 0,
                                    top_p=top_p,
                                    top_k=top_k,
                                    pad_token_id=self.tokenizer.eos_token_id
                                )

        prompt_length = inputs["input_ids"].shape[1]
        answer_ids = output_ids[0, prompt_length:]
        generated_text = self.tokenizer.decode(
                                    answer_ids,
                                    skip_special_tokens=True,
                                )

        # Print the outputs.
        print("\nGenerated Output:\n" + "-" * 60)
        print(f"Prompt:    {query!r}")
        print(generated_text)
        print("-" * 60)

    # def index_bm25(self, max_chunks_size: int = 1500) -> None:
    #     self.bm25.index_da_chuncks(self.chunks)

    # def test_bm25s(self, query: str) -> None:
    #     self.ingest()
    #     self.index_bm25()
    #     print(f"\n--- Testing Search for: '{query}' ---")
    #     self.bm25.query_da_corpus(query, k_size=3, print_yes=True)

    # def index_faiss(self, max_chunk_size: int = 1500) -> None:
    #     self.faiss.embed_da_chuncks(self.chunks)

    # def test_faiss(self, query: str) -> None:
    #     self.ingest()
    #     self.index_faiss()
    #     print(f"\n--- Testing Search for: '{query}' ---")
    #     self.faiss.query_da_embedded(query, k_size=3, print_yes=True)
