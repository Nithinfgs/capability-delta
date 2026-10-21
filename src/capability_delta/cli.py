"""Command-line interface. Never connects to or executes an MCP server."""

from __future__ import annotations

import argparse
import json
import sys
from typing import Any

from jsonschema.exceptions import SchemaError
from referencing.exceptions import Unresolvable

from .core import catalog, compare, load


def render(report: dict[str, Any], markdown: bool = False) -> str:
    lines = [("# " if markdown else "") + "Capability Delta: " + report["status"]]
    lines.append(f"{len(report['changes'])} changed tools; {len(report['fixtures'])} fixtures")
    for item in report["changes"]:
        lines.append(f"- {item['kind']}: {json.dumps(item['tool'], ensure_ascii=True)}")
        for edit in item["changes"]:
            lines.append(f"  - {edit['kind']} {json.dumps(edit['path'], ensure_ascii=True)}")
    for item in report["fixtures"]:
        lines.append(f"- fixture {json.dumps(item['id'], ensure_ascii=True)}: {item['status']}")
        for error in item["errors"]:
            lines.append(f"  - {json.dumps(error['path'])}: {error['rule']}")
    lines.append("Passing fixtures are examples, not proof of full compatibility.")
    if markdown:
        # Escape untrusted catalog text so it cannot inject Markdown/HTML links or images.
        import html

        return "<pre>" + html.escape("\n".join(lines)) + "</pre>\n"
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("baseline")
    parser.add_argument("candidate")
    parser.add_argument("--fixtures", help="JSON array of saved input/output examples")
    parser.add_argument("--format", choices=["text", "json", "markdown"], default="text")
    parser.add_argument("--fail-on", choices=["change", "regression", "never"], default="change")
    args = parser.parse_args()
    try:
        report = compare(
            catalog(load(args.baseline)),
            catalog(load(args.candidate)),
            load(args.fixtures) if args.fixtures else None,
        )
        output = (
            json.dumps(report, indent=2, ensure_ascii=True) + "\n"
            if args.format == "json"
            else render(report, args.format == "markdown")
        )
        sys.stdout.write(output)
        return int(
            (args.fail_on == "change" and report["status"] != "unchanged")
            or (args.fail_on == "regression" and report["status"] == "regression")
        )
    except (OSError, ValueError, SchemaError, Unresolvable, RecursionError) as exc:
        print(f"capability-delta: {json.dumps(str(exc), ensure_ascii=True)}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
