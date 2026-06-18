#!/usr/bin/env python3
# ########################################################################### #
#   shebang: 1                                                                #
#                                                          :::      ::::::::  #
#   __init__.py                                          :+:      :+:    :+:  #
#                                                      +:+ +:+         +:+    #
#   By: npapot <npapot@student.42perpignan.fr>       +#+  +:+       +#+       #
#                                                  +#+#+#+#+#+   +#+          #
#   Created: 2026/03/18 14:06:02 by npapot              #+#    #+#            #
#   Updated: 2026/06/18 16:37:58 by npapot             ###   ########.fr      #
#                                                                             #
# ########################################################################### #

__version__ = "1.0.0"

__author__ = "Master npapot"

from .best_matching_25 import BestMatching25
from .faiss_matching import FaissMatching

__all__ = ["BestMatching25", "FaissMatching"]
