#!/usr/bin/env python3
# ########################################################################### #
#   shebang: 1                                                                #
#                                                          :::      ::::::::  #
#   __main__.py                                          :+:      :+:    :+:  #
#                                                      +:+ +:+         +:+    #
#   By: npapot <npapot@student.42perpignan.fr>       +#+  +:+       +#+       #
#                                                  +#+#+#+#+#+   +#+          #
#   Created: 2026/04/03 15:15:19 by npapot              #+#    #+#            #
#   Updated: 2026/06/04 13:02:07 by npapot             ###   ########.fr      #
#                                                                             #
# ########################################################################### #

import sys
from pydantic import ValidationError

def main() -> None:
    """Main programm"""
    print("Welcome to my CRAZY Retrieval Augmented Generation project!")

    try:
        print("test")

    except ValidationError as e:
        print(
            "BOMBOCLATTT"
            "CRITICAL: Data Structural Validation Failed.", file=sys.stderr
        )
        print(e, file=sys.stderr)
        sys.exit(1)
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
    main()
