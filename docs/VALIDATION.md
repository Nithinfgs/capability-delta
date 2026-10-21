# Validation — 2026-10-21

Executed locally in an isolated virtual environment on macOS:

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -e '.[dev]'
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pytest -q
.venv/bin/ruff check .
.venv/bin/ruff format --check .
.venv/bin/mypy src
.venv/bin/python -m build
.venv/bin/pip-audit
python3 -m venv work/wheel-env
work/wheel-env/bin/python -m pip install dist/capability_delta-0.1.0-py3-none-any.whl
work/wheel-env/bin/capability-delta examples/before.json examples/after.json --fixtures examples/fixtures.json
work/wheel-env/bin/capability-delta examples/before.json examples/before.json --fixtures examples/fixtures.json
```

Results: 39 tests passed; lint, formatting and strict source type checks passed; wheel and sdist built. Clean wheel install succeeded. Changed-catalog demo exited 1 with two demonstrated regressions; unchanged-catalog demo exited 0 with two passing examples. Actual changed output is in [demo.txt](demo.txt).

Initial findings and fixes: mypy required an explicit heterogeneous delta-list annotation; lint required explicit subprocess return-code handling; pip-audit found advisories against the virtual environment's bundled pip 25.3. Upgrading pip in that environment removed those audit findings. The final environment audit reported no known vulnerabilities. The original local project itself is not on PyPI and was skipped by pip-audit; its third-party installed dependencies were audited. This is not a security certification.

Tests include input/output schema changes, removed tools/contracts, invalid baseline examples, duplicate fixtures/tools/JSON keys, local and missing references, external reference rejection, unsupported dialects, JSON limits, deterministic ordering, metadata changes, HTML escaping, real CLI errors/policies and schema combinators/types.

Pre-publication review includes staged-file inspection and a targeted credential-pattern scan for private keys, common GitHub/AWS/OpenAI tokens, and sensitive filenames. This is a heuristic scan, not proof that all possible secrets are absent. No live MCP integration was tested: this release intentionally consumes saved exports only. Cross-platform behavior is checked by GitHub Actions after publication; see the live workflow for current status.
