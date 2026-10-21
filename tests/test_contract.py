import copy
import json
import subprocess
import sys

import pytest

from capability_delta.cli import render
from capability_delta.core import ContractError, catalog, changes, compare, load


def tool():
    return {
        "name": "note",
        "inputSchema": {
            "type": "object",
            "properties": {"q": {"type": "string"}},
            "required": ["q"],
        },
        "outputSchema": {
            "type": "object",
            "properties": {"n": {"type": "integer"}},
            "required": ["n"],
        },
    }


def indexed(t=None):
    return catalog({"tools": [t or tool()]})


def fixture(kind="input", value=None):
    return [
        {
            "id": "sample",
            "tool": "note",
            "kind": kind,
            "value": value if value is not None else {"q": "hi"},
        }
    ]


def test_input_regression():
    t = tool()
    t["inputSchema"]["required"].append("limit")
    r = compare(indexed(), indexed(t), fixture())
    assert r["status"] == "regression"
    assert r["fixtures"][0]["errors"] == [{"path": "/", "rule": "required"}]


def test_output_regression():
    t = tool()
    t["outputSchema"]["properties"]["n"]["minimum"] = 5
    assert compare(indexed(), indexed(t), fixture("output", {"n": 2}))["status"] == "regression"


def test_schema_removed_unverified():
    t = tool()
    del t["outputSchema"]
    r = compare(indexed(), indexed(t), fixture("output", {"n": 2}))
    assert r["status"] == "review"
    assert r["fixtures"][0]["status"] == "unverified"


def test_tool_removed():
    assert compare(indexed(), {}, fixture())["status"] == "regression"


def test_added_and_removed():
    assert compare({}, indexed())["changes"][0]["kind"] == "added"
    assert compare(indexed(), {})["changes"][0]["kind"] == "removed"


def test_baseline_invalid():
    with pytest.raises(ContractError, match="baseline"):
        compare(indexed(), indexed(), fixture(value={"q": 12}))


def test_unknown_tool():
    f = fixture()
    f[0]["tool"] = "missing"
    with pytest.raises(ContractError):
        compare(indexed(), indexed(), f)


def test_duplicate_fixture():
    with pytest.raises(ContractError):
        compare(indexed(), indexed(), fixture() * 2)


@pytest.mark.parametrize(
    "value",
    [
        [],
        {},
        {"tools": [tool(), tool()]},
        {"tools": [], "nextCursor": "x"},
        {"tools": [{"name": "bad"}]},
        {"result": {"tools": []}, "error": {}},
    ],
)
def test_bad_catalog(value):
    with pytest.raises(ContractError):
        catalog(value)


def test_rpc_and_order():
    a = tool()
    b = copy.deepcopy(a)
    b["name"] = "other"
    old = catalog({"tools": [a, b]})
    new = catalog({"result": {"tools": [b, a]}})
    r = compare(old, new)
    assert r["status"] == "unchanged"
    assert r["baseline_sha256"] == r["candidate_sha256"]


def test_metadata_review():
    t = tool()
    t["annotations"] = {"readOnlyHint": False}
    assert compare(indexed(), indexed(t), fixture())["status"] == "review"


def test_pointer_escape_and_typed_values():
    assert changes({"a/b~c": True}, {"a/b~c": 1})[0]["path"] == "/a~1b~0c"


def test_local_refs():
    t = tool()
    t["inputSchema"]["$defs"] = {"text": {"type": "string"}}
    t["inputSchema"]["properties"]["q"] = {"$ref": "#/$defs/text"}
    assert compare(indexed(t), indexed(t), fixture())["fixtures"][0]["status"] == "passed"


@pytest.mark.parametrize(
    "extra",
    [
        {"$ref": "https://example.com/schema"},
        {"$schema": "http://json-schema.org/draft-07/schema#"},
        {"$id": "https://example.com/schema"},
    ],
)
def test_unsupported_schema(extra):
    t = tool()
    t["inputSchema"].update(extra)
    with pytest.raises(ContractError):
        indexed(t)


@pytest.mark.parametrize("text", ['{"a":1,"a":2}', '{"a":NaN}', '{"a":Infinity}'])
def test_strict_json(tmp_path, text):
    p = tmp_path / "x.json"
    p.write_text(text)
    with pytest.raises(ContractError):
        load(str(p))


def test_size_depth(tmp_path):
    p = tmp_path / "x.json"
    p.write_text(" " * (5 * 1024 * 1024 + 1))
    with pytest.raises(ContractError):
        load(str(p))
    p.write_text("[" * 66 + "0" + "]" * 66)
    with pytest.raises(ContractError):
        load(str(p))


def test_markdown_escaped():
    t = tool()
    t["name"] = "<script>alert(1)</script>"
    output = render(compare({}, indexed(t)), True)
    assert "<script>" not in output and "&lt;script&gt;" in output


@pytest.mark.parametrize(
    "flags,code",
    [
        ([], 1),
        (["--fail-on", "never"], 0),
        (["--fail-on", "regression"], 0),
        (["--fail-on", "regression", "--fixtures", "examples/fixtures.json"], 1),
    ],
)
def test_cli_policies(flags, code):
    p = subprocess.run(
        [
            sys.executable,
            "-m",
            "capability_delta.cli",
            "examples/before.json",
            "examples/after.json",
            "--format",
            "json",
            *flags,
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    assert p.returncode == code, p.stderr
    assert json.loads(p.stdout)["format_version"] == 1


def test_cli_error(tmp_path):
    p = tmp_path / "bad.json"
    p.write_text("{")
    result = subprocess.run(
        [sys.executable, "-m", "capability_delta.cli", str(p), str(p)],
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 2 and "Traceback" not in result.stderr


def test_example_identical():
    a = catalog(load("examples/before.json"))
    assert compare(a, a, load("examples/fixtures.json"))["status"] == "unchanged"


@pytest.mark.parametrize(
    "schema,value,expected",
    [
        ({"type": "integer"}, True, "regression"),
        ({"enum": ["a", "b"]}, "a", "passed"),
        ({"oneOf": [{"type": "string"}, {"type": "integer"}]}, "a", "passed"),
        ({"type": "array", "items": {"type": "integer"}}, ["a"], "regression"),
        ({"type": "string", "minLength": 5}, "a", "regression"),
    ],
)
def test_schema_semantics(schema, value, expected):
    before = tool()
    before["inputSchema"]["properties"]["q"] = {}
    after = copy.deepcopy(before)
    after["inputSchema"]["properties"]["q"] = schema
    report = compare(indexed(before), indexed(after), fixture(value={"q": value}))
    assert report["fixtures"][0]["status"] == expected


def test_unknown_metadata_not_lost():
    t = tool()
    t["_meta"] = {"future": {"enabled": True}}
    assert compare(indexed(), indexed(t))["changes"][0]["changes"][0]["path"] == "/_meta"


def test_invalid_ref_cli(tmp_path):
    t = tool()
    t["inputSchema"]["properties"]["q"] = {"$ref": "#/$defs/missing"}
    p = tmp_path / "catalog.json"
    p.write_text(json.dumps({"tools": [t]}))
    f = tmp_path / "fixtures.json"
    f.write_text(json.dumps(fixture()))
    result = subprocess.run(
        [sys.executable, "-m", "capability_delta.cli", str(p), str(p), "--fixtures", str(f)],
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 2 and "Traceback" not in result.stderr
