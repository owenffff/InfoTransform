#!/usr/bin/env python3
"""
Generate a dependency license report for legal team review.

This script uses pip-licenses to generate a formatted table of all Python dependencies
with their versions and licenses.

Usage:
    python scripts/generate_licenses.py [--format FORMAT] [--output FILE]

Formats:
    - plain (default): Simple text table
    - markdown: Markdown table format
    - csv: CSV format for Excel import
    - json: JSON format
"""

import subprocess
import sys
import argparse
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(
        description="Generate dependency license report for InfoTransform backend"
    )
    parser.add_argument(
        "--format",
        choices=["plain", "markdown", "csv", "json"],
        default="markdown",
        help="Output format (default: markdown)",
    )
    parser.add_argument(
        "--output",
        type=str,
        help="Output file path (default: prints to stdout)",
    )
    parser.add_argument(
        "--with-urls",
        action="store_true",
        help="Include project URLs in the output",
    )
    parser.add_argument(
        "--with-authors",
        action="store_true",
        help="Include author information",
    )

    args = parser.parse_args()

    # Build the pip-licenses command
    cmd = ["uv", "run", "pip-licenses"]

    # Add format
    if args.format == "plain":
        cmd.extend(["--format=plain"])
    elif args.format == "markdown":
        cmd.extend(["--format=markdown"])
    elif args.format == "csv":
        cmd.extend(["--format=csv"])
    elif args.format == "json":
        cmd.extend(["--format=json"])

    # Add optional flags
    if args.with_urls:
        cmd.append("--with-urls")
    if args.with_authors:
        cmd.append("--with-authors")

    # Add sorting and other options
    cmd.extend(
        [
            "--order=name",  # Sort by package name
            "--with-description",  # Include package descriptions
        ]
    )

    try:
        # Run the command
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True,
        )

        output = result.stdout

        # Add header for legal team
        header = f"""# InfoTransform Backend - Open Source Software Dependencies
# License Report for Legal Review
# Generated: {__import__("datetime").datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

"""

        if args.format == "markdown":
            output = header + output
        elif args.format == "csv":
            # CSV doesn't need the header with markdown formatting
            header = f"# InfoTransform Backend - OSS Dependencies License Report\n# Generated: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
            output = header + output

        # Output to file or stdout
        if args.output:
            output_path = Path(args.output)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(output)
            print(f"License report saved to: {output_path}")
        else:
            print(output)

    except subprocess.CalledProcessError as e:
        print(f"Error running pip-licenses: {e}", file=sys.stderr)
        if e.stderr:
            print(e.stderr, file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
