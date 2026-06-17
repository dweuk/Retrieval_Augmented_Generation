#!/usr/bin/env python3
# ########################################################################### #
#   shebang: 1                                                                #
#                                                          :::      ::::::::  #
#   __init__.py                                          :+:      :+:    :+:  #
#                                                      +:+ +:+         +:+    #
#   By: npapot <npapot@student.42perpignan.fr>       +#+  +:+       +#+       #
#                                                  +#+#+#+#+#+   +#+          #
#   Created: 2026/03/18 14:06:02 by npapot              #+#    #+#            #
#   Updated: 2026/06/17 20:08:23 by npapot             ###   ########.fr      #
#                                                                             #
# ########################################################################### #

__version__ = "1.0.0"

__author__ = "Master npapot"

from .code_parser import CodeParser
from .python_parser import PythonParser

__all__ = ["PythonParser", "CodeParser"]
