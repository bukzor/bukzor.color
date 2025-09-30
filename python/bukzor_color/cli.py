"""CLI interface for bukzor-color."""

import json
from typing import Any

import click


@click.group()
@click.version_option()
def main() -> None:
    """Color calculations and conversions CLI."""
    pass


@main.command()
@click.argument("input_color")
@click.option("--to", default="hex", help="Output format (hex, rgb, hsl, hsv)")
@click.option("--json", "output_json", is_flag=True, help="Output as JSON")
def convert(input_color: str, to: str, output_json: bool) -> None:
    """Convert colors between formats."""
    if output_json:
        result: dict[str, Any] = {
            "input": input_color,
            "output_format": to,
            "result": "TODO: implement conversion",
        }
        click.echo(json.dumps(result, indent=2))
    else:
        click.echo(f"Converting '{input_color}' to {to}: TODO: implement")


if __name__ == "__main__":
    main()
