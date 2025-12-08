from __future__ import annotations

import sys

from .core import run


def main(argv: list[str] | None = None) -> None:
    if argv is None:
        argv = sys.argv[1:]

    if not argv:
        print("Verwendung: python -m Auswertung <config_name|pfad/zur/config.json>")
        raise SystemExit(1)

    config_name = argv[0]
    run(config_name)


if __name__ == "__main__":
    main()
