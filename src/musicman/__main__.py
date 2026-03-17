"""Entry point for musicman."""

import sys

from musicman.app import create_app


def main():
    app = create_app()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
