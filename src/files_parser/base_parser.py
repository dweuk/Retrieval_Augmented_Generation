#!/usr/bin/env python3
# ########################################################################### #
#   shebang: 1                                                                #
#                                                          :::      ::::::::  #
#   base_parser.py                                       :+:      :+:    :+:  #
#                                                      +:+ +:+         +:+    #
#   By: npapot <npapot@student.42perpignan.fr>       +#+  +:+       +#+       #
#                                                  +#+#+#+#+#+   +#+          #
#   Created: 2026/06/16 10:59:10 by npapot              #+#    #+#            #
#   Updated: 2026/06/16 11:02:25 by npapot             ###   ########.fr      #
#                                                                             #
# ########################################################################### #

from abc import ABC, abstractmethod
from pathlib import Path

class BaseParser(ABC):
    def __init__(self) -> None:
        pass

    @abstractmethod
    def _extract_text(self, file_patrh: Path) -> str:
        """
        Takes a file path and returns the extracted text as a string.
        Every specific parser MUST implement this method.
        """
        pass