#!/usr/bin/env python3
# ########################################################################### #
#   shebang: 1                                                                #
#                                                          :::      ::::::::  #
#   rag.py                                               :+:      :+:    :+:  #
#                                                      +:+ +:+         +:+    #
#   By: npapot <npapot@student.42perpignan.fr>       +#+  +:+       +#+       #
#                                                  +#+#+#+#+#+   +#+          #
#   Created: 2026/04/03 15:15:19 by npapot              #+#    #+#            #
#   Updated: 2026/06/15 23:59:18 by npapot             ###   ########.fr      #
#                                                                             #
# ########################################################################### #

import sys
from src.rag_pipeline import RAGPipeline
import fire  # type: ignore

def rag() -> None:
    """Main programm"""
    print("Welcome to my CRAZY Retrieval Augmented Generation project!")

    try:
        print("test")
        fire.Fire(RAGPipeline)

    except EOFError as e:
        print(
            "BOMBOCLATTT"
            "CRITICAL: EOFError when reading "
            , file=sys.stderr
        )
        print(e, file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print("BOMBOCLATTT")
        print(f"Unexpected Error: {e}", file=sys.stderr)
        sys.exit(1)



if __name__ == "__main__":
    sys.exit(rag())
