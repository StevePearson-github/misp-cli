"""Main entry point for MISP CLI."""

import sys

from misp_cli.cli.app import app


def main() -> int:
    """Main entry point."""
    try:
        app()
        return 0
    except KeyboardInterrupt:
        return 130
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
