#!/usr/bin/env python3
# ########################################################################### #
#   shebang: 1                                                                #
#                                                          :::      ::::::::  #
#   __init__.py                                          :+:      :+:    :+:  #
#                                                      +:+ +:+         +:+    #
#   By: npapot <npapot@student.42perpignan.fr>       +#+  +:+       +#+       #
#                                                  +#+#+#+#+#+   +#+          #
#   Created: 2026/03/18 14:06:02 by npapot              #+#    #+#            #
#   Updated: 2026/06/15 23:40:17 by npapot             ###   ########.fr      #
#                                                                             #
# ########################################################################### #

__version__ = "1.0.0"

__author__ = "Master npapot"

from .text_class import TextFile

__all__ = ["TextFile"]
