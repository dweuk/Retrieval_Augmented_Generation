#!/usr/bin/env python3
# ########################################################################### #
#   shebang: 1                                                                #
#                                                          :::      ::::::::  #
#   faiss_matching.py                                    :+:      :+:    :+:  #
#                                                      +:+ +:+         +:+    #
#   By: npapot <npapot@student.42perpignan.fr>       +#+  +:+       +#+       #
#                                                  +#+#+#+#+#+   +#+          #
#   Created: 2026/06/18 15:51:03 by npapot              #+#    #+#            #
#   Updated: 2026/06/18 19:42:05 by npapot             ###   ########.fr      #
#                                                                             #
# ########################################################################### #

import faiss
from sentence_transformers import SentenceTransformer
import numpy as np


class FaissMatching:
    def __init__(self) -> None:
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.corpus: list[str] = []

    def embed_da_chuncks(
                self,
                corpus: list[str]
            ) -> None:
        self.corpus.extend(corpus)

        embeddings = self.model.encode(corpus)

        # The size of the vectors (384 for MiniLM)
        dimension = embeddings[0].shape[0]
        self.faiss_index = faiss.IndexFlatL2(dimension)

        # 3. Add to the index
        self.faiss_index.add(np.array(embeddings).astype('float32'))

    def query_da_embedded(
                self,
                query: str,
                k_size: int = 10,
                print_yes: bool = False
            ) -> list[str]:
        right_chunk: list[str] = []

        query_vector = self.model.encode([query])
        query_vector = np.array(query_vector).astype('float32')

        distances, chunk_ids = self.faiss_index.search(query_vector, k=k_size)

        for i in range(k_size):
            chunk_id = chunk_ids[0][i]
            score = distances[0][i]
            doc = self.corpus[chunk_id]
            right_chunk.append(doc)

            if print_yes:
                print(f"\n------- Rank {i+1} (Distance: {score:.2f}) -------")
                print(doc)
                print("=" * 50)

        return right_chunk
