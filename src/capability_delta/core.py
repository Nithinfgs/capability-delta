"""Deterministic catalog diffs and fixture-based compatibility evidence."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator
from referencing import Registry

MAX_BYTES = 5 * 1024 * 1024


class ContractError(ValueError):
    """Invalid or unsupported contract input."""


def canonical(value: Any) -> str:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True, allow_nan=False
    )


def fingerprint(value: Any) -> str:
    return hashlib.sha256(canonical(value).encode()).hexdigest()


def _pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ContractError(f"Duplicate JSON key: {key!r}")
        result[key] = value
    return result


def _reject_constant(value: str) -> Any:
    raise ContractError(f"Non-JSON number: {value}")


def load(path: str) -> Any:
    with Path(path).open("rb") as stream:
        data = stream.read(MAX_BYTES + 1)
    if len(data) > MAX_BYTES:
        raise ContractError("Input exceeds 5 MiB")
    result = json.loads(data, object_pairs_hook=_pairs, parse_constant=_reject_constant)
    check_depth(result)
    return result


def check_depth(value: Any, depth: int = 0) -> None:
    if depth > 64:
        raise ContractError("JSON nesting exceeds 64 levels")
    if isinstance(value, dict):
        for item in value.values():
            check_depth(item, depth + 1)
    elif isinstance(value, list):
        for item in value:
            check_depth(item, depth + 1)


def validate_schema(schema: Any) -> None:
    if not isinstance(schema, dict) or schema.get("type") != "object":
        raise ContractError("MCP input/output schemas must have type: object")
    dialect = schema.get("$schema", "https://json-schema.org/draft/2020-12/schema")
    if dialect not in (
        "https://json-schema.org/draft/2020-12/schema",
        "https://json-schema.org/draft/2020-12/schema#",
    ):
        raise ContractError("Only JSON Schema Draft 2020-12 is supported")

    def walk(node: Any) -> None:
        if isinstance(node, dict):
            for key, value in node.items():
                if key in ("$ref", "$dynamicRef") and (
                    not isinstance(value, str) or not value.startswith("#")
                ):
                    raise ContractError("Only document-local schema references are supported")
                if key == "$id":
                    raise ContractError("Schema $id is unsupported; use document-local references")
                walk(value)
        elif isinstance(node, list):
            for item in node:
                walk(item)

    walk(schema)
    Draft202012Validator.check_schema(schema)


def catalog(value: Any) -> dict[str, dict[str, Any]]:
    if not isinstance(value, dict):
        raise ContractError("Catalog must be an object")
    if "result" in value:
        if "error" in value:
            raise ContractError("JSON-RPC error is not a catalog")
        value = value["result"]
    if not isinstance(value, dict) or not isinstance(value.get("tools"), list):
        raise ContractError("Expected tools/list result containing tools array")
    if value.get("nextCursor") is not None:
        raise ContractError("Paginated catalog: collect every page and remove nextCursor first")
    result: dict[str, dict[str, Any]] = {}
    for tool in value["tools"]:
        if not isinstance(tool, dict) or not isinstance(tool.get("name"), str) or not tool["name"]:
            raise ContractError("Every tool needs a nonempty string name")
        name = tool["name"]
        if name in result:
            raise ContractError(f"Duplicate tool: {name!r}")
        validate_schema(tool.get("inputSchema"))
        if "outputSchema" in tool:
            validate_schema(tool["outputSchema"])
        if "description" in tool and not isinstance(tool["description"], str):
            raise ContractError("Tool description must be a string")
        if "annotations" in tool and not isinstance(tool["annotations"], dict):
            raise ContractError("Tool annotations must be an object")
        result[name] = tool
    return result


def pointer(parts: list[str]) -> str:
    return "/" + "/".join(p.replace("~", "~0").replace("/", "~1") for p in parts)


def changes(old: Any, new: Any, path: list[str] | None = None) -> list[dict[str, Any]]:
    path = path or []
    if canonical(old) == canonical(new):
        return []
    if isinstance(old, dict) and isinstance(new, dict):
        result = []
        for key in sorted(old.keys() | new.keys()):
            location = path + [key]
            if key not in old:
                result.append({"path": pointer(location), "kind": "added", "after": new[key]})
            elif key not in new:
                result.append({"path": pointer(location), "kind": "removed", "before": old[key]})
            else:
                result.extend(changes(old[key], new[key], location))
        return result
    return [{"path": pointer(path), "kind": "changed", "before": old, "after": new}]


def errors(schema: dict[str, Any], instance: Any) -> list[dict[str, str]]:
    # An empty registry never retrieves remote resources.
    validator = Draft202012Validator(schema, registry=Registry())
    return sorted(
        [
            {"path": pointer([str(x) for x in e.absolute_path]), "rule": str(e.validator)}
            for e in validator.iter_errors(instance)
        ],
        key=lambda x: (x["path"], x["rule"]),
    )


def compare(
    old: dict[str, dict[str, Any]], new: dict[str, dict[str, Any]], fixtures: Any = None
) -> dict[str, Any]:
    delta: list[dict[str, Any]] = []
    for name in sorted(old.keys() | new.keys()):
        if name not in old:
            delta.append({"tool": name, "kind": "added", "changes": []})
        elif name not in new:
            delta.append({"tool": name, "kind": "removed", "changes": []})
        else:
            edits = changes(old[name], new[name])
            if edits:
                delta.append({"tool": name, "kind": "changed", "changes": edits})
    if fixtures is None:
        fixtures = []
    if not isinstance(fixtures, list):
        raise ContractError("Fixtures must be an array")
    evidence = []
    ids: set[str] = set()
    for fixture in fixtures:
        if not isinstance(fixture, dict) or set(fixture) != {"id", "tool", "kind", "value"}:
            raise ContractError("Fixture requires exactly id, tool, kind, value")
        ident, name, kind = fixture["id"], fixture["tool"], fixture["kind"]
        if not isinstance(ident, str) or not ident or ident in ids:
            raise ContractError("Fixture IDs must be nonempty unique strings")
        ids.add(ident)
        if not isinstance(name, str) or name not in old:
            raise ContractError(f"Fixture {ident!r} names a tool absent from baseline")
        if kind not in ("input", "output"):
            raise ContractError("Fixture kind must be input or output")
        key = "inputSchema" if kind == "input" else "outputSchema"
        if key not in old[name]:
            raise ContractError(f"Fixture {ident!r}: baseline has no {key}")
        baseline_errors = errors(old[name][key], fixture["value"])
        if baseline_errors:
            raise ContractError(f"Fixture {ident!r} does not validate against baseline")
        if name not in new:
            status, failures = "regression", [{"path": "/", "rule": "tool_removed"}]
        elif key not in new[name]:
            status, failures = "unverified", [{"path": "/", "rule": "schema_removed"}]
        else:
            failures = errors(new[name][key], fixture["value"])
            status = "regression" if failures else "passed"
        evidence.append(
            {"id": ident, "tool": name, "kind": kind, "status": status, "errors": failures}
        )
    regression = any(e["status"] == "regression" for e in evidence)
    return {
        "format_version": 1,
        "baseline_sha256": fingerprint(old),
        "candidate_sha256": fingerprint(new),
        "status": "regression" if regression else ("review" if delta else "unchanged"),
        "changes": delta,
        "fixtures": evidence,
    }
