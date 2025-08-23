#!/usr/bin/env python3
"""Main entry point for AeroLOPA Crawler.

This script provides a simple interface to the AeroLOPA seat map crawler.
For more advanced options, use the CLI module directly.
"""

import sys
from pathlib import Path

# Add src to path for development
src_path = Path(__file__).parent / "src"
if src_path.exists():
    sys.path.insert(0, str(src_path))

from aerolopa_crawler.cli import main as cli_main  # noqa: E402


def main():
    """Main entry point that delegates to the CLI module."""
    try:
        cli_main()
    except KeyboardInterrupt:
        print("\nOperation cancelled by user", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()