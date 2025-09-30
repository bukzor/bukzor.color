"""CLI interface for bukzor-color."""

import json
from typing import Any

import click

from bukzor_color.contrast import adjust_contrast, calculate_contrast
from bukzor_color.encodings import encodings

ENCODING_REGISTRY = {
    'hex': encodings.HexEncoding,
    'wcag-hcl': encodings.WcagHCLEncoding,
}
HexEncoding = encodings.HexEncoding
RGBEncoding = encodings.RGBEncoding
HSLEncoding = encodings.HSLEncoding
HSVEncoding = encodings.HSVEncoding
auto_parse = encodings.auto_parse


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
    try:
        # Parse input using auto-detection
        input_encoding = auto_parse(input_color)
        color = input_encoding.decode()

        # Encode to requested format
        if to == "hex":
            output_encoding = HexEncoding.encode(color)
        elif to == "rgb":
            output_encoding = RGBEncoding.encode(color)
        elif to == "hsl":
            output_encoding = HSLEncoding.encode(color)
        elif to == "hsv":
            output_encoding = HSVEncoding.encode(color)
        else:
            raise ValueError(f"Unsupported output format: {to}")

        result_value = str(output_encoding)

        if output_json:
            result: dict[str, Any] = {
                "input": input_color,
                "output_format": to,
                "result": result_value,
            }
            click.echo(json.dumps(result, indent=2))
        else:
            click.echo(result_value)

    except Exception as e:
        if output_json:
            error_result = {
                "input": input_color,
                "output_format": to,
                "error": str(e),
            }
            click.echo(json.dumps(error_result, indent=2))
        else:
            click.echo(f"Error: {e}", err=True)
        raise click.Abort()


@main.command("contrast-check")
@click.argument("foreground")
@click.argument("background")
@click.option("--json", "output_json", is_flag=True, help="Output as JSON")
def contrast_check(foreground: str, background: str, output_json: bool) -> None:
    """Check WCAG contrast ratio between two colors."""
    try:
        fg_color = auto_parse(foreground).decode()
        bg_color = auto_parse(background).decode()

        result = calculate_contrast(fg_color, bg_color)

        if output_json:
            output_data = {
                "foreground": foreground,
                "background": background,
                "contrast_ratio": float(result.ratio),
                "compliance": result.compliance_summary(),
            }
            click.echo(json.dumps(output_data, indent=2))
        else:
            click.echo(f"Contrast ratio: {result.ratio:.2f}")
            click.echo(f"AA: {'✓' if result.passes_AA else '✗'}")
            click.echo(f"AAA: {'✓' if result.passes_AAA else '✗'}")
            click.echo(f"AA Large: {'✓' if result.passes_AA_large else '✗'}")
            click.echo(f"AAA Large: {'✓' if result.passes_AAA_large else '✗'}")

    except Exception as e:
        if output_json:
            error_result = {
                "foreground": foreground,
                "background": background,
                "error": str(e),
            }
            click.echo(json.dumps(error_result, indent=2))
        else:
            click.echo(f"Error: {e}", err=True)
        raise click.Abort()


@main.command("contrast-adjust")
@click.argument("foreground")
@click.argument("background")
@click.option("--target", default="AA", help="Target WCAG level (AA, AAA, AA-large, AAA-large) or ratio")
@click.option("--adjust", default="auto", help="Which color to adjust (fg, bg, both, auto)")
@click.option("--preserve-hue", is_flag=True, default=True, help="Preserve hue during adjustment")
@click.option("--json", "output_json", is_flag=True, help="Output as JSON")
def contrast_adjust(
    foreground: str,
    background: str,
    target: str,
    adjust: str,
    preserve_hue: bool,
    output_json: bool
) -> None:
    """Adjust colors to meet target contrast ratio."""
    try:
        fg_color = auto_parse(foreground).decode()
        bg_color = auto_parse(background).decode()

        # Parse target (could be WCAG level or numeric ratio)
        try:
            from decimal import Decimal
            from bukzor_color.types import ContrastRatio
            target_ratio: ContrastRatio = ContrastRatio(Decimal(target))
            is_numeric_target = True
        except:
            # Assume it's a WCAG level
            target_ratio = target  # type: ignore[assignment]
            is_numeric_target = False

        # Validate adjust parameter
        if adjust not in ("fg", "bg", "both", "auto"):
            raise ValueError(f"Invalid adjust option: {adjust}")

        adjusted_fg, adjusted_bg, result = adjust_contrast(
            fg_color,
            bg_color,
            target_ratio,
            adjust=adjust
        )

        if output_json:
            output_data = {
                "original": {
                    "foreground": foreground,
                    "background": background,
                },
                "adjusted": {
                    "foreground": str(HexEncoding.encode(adjusted_fg)),
                    "background": str(HexEncoding.encode(adjusted_bg)),
                },
                "contrast_ratio": float(result.ratio),
                "compliance": result.compliance_summary(),
            }
            click.echo(json.dumps(output_data, indent=2))
        else:
            click.echo(f"Original: fg={foreground} bg={background}")
            click.echo(f"Adjusted: fg={HexEncoding.encode(adjusted_fg)} bg={HexEncoding.encode(adjusted_bg)}")
            click.echo(f"Contrast ratio: {result.ratio:.2f}")
            if is_numeric_target:
                meets_target: bool = result.ratio >= target_ratio  # type: ignore[operator]
            else:
                # Validate WCAG level
                if target not in ("A", "AA", "AAA", "AA-large", "AAA-large"):
                    raise ValueError(f"Invalid WCAG level: {target}")
                meets_target = result.meets_level(target)
            click.echo(f"Meets target: {'✓' if meets_target else '✗'}")

    except Exception as e:
        if output_json:
            error_result = {
                "foreground": foreground,
                "background": background,
                "error": str(e),
            }
            click.echo(json.dumps(error_result, indent=2))
        else:
            click.echo(f"Error: {e}", err=True)
        raise click.Abort()


if __name__ == "__main__":
    main()
