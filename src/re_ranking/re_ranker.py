#!/usr/bin/env python3
# ########################################################################### #
#   shebang: 1                                                                #
#                                                          :::      ::::::::  #
#   re_ranker.py                                         :+:      :+:    :+:  #
#                                                      +:+ +:+         +:+    #
#   By: npapot <npapot@student.42perpignan.fr>       +#+  +:+       +#+       #
#                                                  +#+#+#+#+#+   +#+          #
#   Created: 2026/06/18 19:27:30 by npapot              #+#    #+#            #
#   Updated: 2026/06/19 11:12:33 by npapot             ###   ########.fr      #
#                                                                             #
# ########################################################################### #

from sentence_transformers import CrossEncoder

MODELE_RERANK = "BAAI/bge-reranker-v2-m3"


class ReRanker:
    def __init__(
            self,
            model_name: str = 'cross-encoder/ms-marco-MiniLM-L-6-v2'
            ) -> None:
        print("Loading Cross-Encoder model...")
        self.model = CrossEncoder(model_name)

    def reclassification(
                    self,
                    query: str,
                    unique_chunks: list[str],
                    k: int = 3
                ) -> list[str]:
        pairs = [(query, unique_chunk) for unique_chunk in unique_chunks]

        scores = self.model.predict(pairs)

        classement = sorted(
                zip(unique_chunks, scores), key=lambda c: c[1], reverse=True
            )

        return [texte for texte, _ in classement[:k]]
