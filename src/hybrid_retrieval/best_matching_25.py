#!/usr/bin/env python3
# ########################################################################### #
#   shebang: 1                                                                #
#                                                          :::      ::::::::  #
#   best_matching_25.py                                  :+:      :+:    :+:  #
#                                                      +:+ +:+         +:+    #
#   By: npapot <npapot@student.42perpignan.fr>       +#+  +:+       +#+       #
#                                                  +#+#+#+#+#+   +#+          #
#   Created: 2026/06/18 11:42:51 by npapot              #+#    #+#            #
#   Updated: 2026/06/18 19:41:51 by npapot             ###   ########.fr      #
#                                                                             #
# ########################################################################### #

import bm25s     # type: ignore
import Stemmer   # type: ignore
from pathlib import Path


class BestMatching25:
    def __init__(self) -> None:
        self.corpus: list[str] = []
        self.retriever = bm25s.BM25(backend="numba")

    def index_da_chuncks(
                    self,
                    corpus: list[str],
                    save_data: str = "data/processed",
                    save_to_path: bool = False
                ) -> None:
        path_to_save_data = Path(save_data)
        # optional: create a stemmer
        self.stemmer = Stemmer.Stemmer("english")
        self.corpus.extend(corpus)

        # Tokenize the corpus and only keep the ids (faster and saves memory)
        corpus_tokens = bm25s.tokenize(
                    corpus, stopwords="en", stemmer=self.stemmer
                )

        # Create the BM25 model and index the corpus
        self.retriever.index(corpus_tokens)

        # You can save the arrays to a directory...
        # You can save the corpus along with the model
        if save_to_path:
            self.retriever.save(path_to_save_data)
            self.retriever.save(path_to_save_data, corpus=self.corpus)

    def query_da_corpus(
                self,
                query: str,
                k_size: int = 10,
                print_yes: bool = False
            ) -> list[str]:
        right_chunk: list[str] = []
        query_tokens = bm25s.tokenize(query, stemmer=self.stemmer)

        # Get top-k results as a tuple of (doc ids, scores).
        # Both are arrays of shape (n_queries, k).
        # To return docs instead of IDs, set the `corpus=corpus` parameter.
        if print_yes:
            results, scores = self.retriever.retrieve(
                                    query_tokens, corpus=self.corpus, k=k_size
                                )
        else:
            results, scores = self.retriever.retrieve(query_tokens, k=k_size)

        for i in range(results.shape[1]):
            doc, score = results[0, i], scores[0, i]
            right_chunk.append(doc)
            if print_yes:
                print(f"-------Rank {i+1} (score: {score:.2f}): {doc}-------")
                print(f"{doc}")
                print("=" * 50)

        return right_chunk

    def retrieve_da_data(
                self,
                save_data: str = "data/processed"
                ) -> None:
        path_to_save_data = Path(save_data)
        self.retriever.load(path_to_save_data, load_corpus=True)
