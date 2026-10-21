# Selection and acceptance criteria

Selected before implementation: **Capability Delta**, an offline MCP contract regression checker for server maintainers and integration teams. Agent adoption increases the number of tool contracts teams depend on; recent developer reports describe silent parameter and output changes. Sources and weighted alternatives are in `research/REPORT.md`.

Differentiation: combine complete tool metadata diffs with concrete baseline-valid input AND output examples. Existing scanners focus on security findings; proxies record runtime activity; OpenAPI tools target a different API description. This project neither copies their implementations nor claims a new underlying diff algorithm.

Stack: Python 3.11+, jsonschema Draft 2020-12, standard-library CLI and hashing, pytest/ruff/mypy. Reuse a maintained validator rather than invent incomplete JSON Schema semantics.

MVP acceptance: reject incomplete/malformed catalogs; detect additions/removals/field changes deterministically; show exact JSON Pointer locations; demonstrate both input and output regressions; reject invalid baseline fixtures; support clean/changed/error exit codes; never fetch refs or execute a tool; install from a built wheel; pass cross-platform CI and publish a new repository.

Output fixtures exercise old outputs against new declared output contracts. They are not a consumer contract nor samples of future behavior. Unknown metadata changes get review, never a fabricated security score. Default policy fails on any drift; opt-in regression policy intentionally tolerates unproven changes.
