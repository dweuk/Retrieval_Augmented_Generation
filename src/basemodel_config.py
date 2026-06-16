#!/usr/bin/env python3
# ########################################################################### #
#   shebang: 1                                                                #
#                                                          :::      ::::::::  #
#   basemodel_config.py                                  :+:      :+:    :+:  #
#                                                      +:+ +:+         +:+    #
#   By: npapot <npapot@student.42perpignan.fr>       +#+  +:+       +#+       #
#                                                  +#+#+#+#+#+   +#+          #
#   Created: 2026/04/08 15:32:38 by npapot              #+#    #+#            #
#   Updated: 2026/06/16 11:42:46 by npapot             ###   ########.fr      #
#                                                                             #
# ########################################################################### #

from pydantic import BaseModel, Field


class Prompt(BaseModel):
    prompt: str = Field(min_length=1)
