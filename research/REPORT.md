# Research and selection — 2026-10-21

Live observations collected via GitHub Trending HTML and authenticated read-only GitHub REST API. Observation timestamps are in repositories.json. Counts are snapshots, not audited adoption statistics. Trending period gains are GitHub-displayed figures, not independently reconstructed star histories. No inference of future growth is made.

## Repository review

| Repository | Stars | Assessment |
|---|---:|---|
| [modelcontextprotocol/servers](https://github.com/modelcontextprotocol/servers) | 91,448 | Reference ecosystem; broad adoption proxy |
| [modelcontextprotocol/python-sdk](https://github.com/modelcontextprotocol/python-sdk) | 24,632 | Python integration surface |
| [modelcontextprotocol/typescript-sdk](https://github.com/modelcontextprotocol/typescript-sdk) | 13,632 | TypeScript integration surface |
| [PrefectHQ/fastmcp](https://github.com/PrefectHQ/fastmcp) | 28,162 | Server authoring demand |
| [modelcontextprotocol/inspector](https://github.com/modelcontextprotocol/inspector) | 11,114 | Interactive debugger; different workflow |
| [snyk/agent-scan](https://github.com/snyk/agent-scan) | 3,161 | Security scanning incumbent |
| [coder27/mcp-provenance-proxy](https://github.com/coder27/mcp-provenance-proxy) | 0 | Runtime provenance competitor; tiny adoption |
| [rebecazm129-commits/xclaude-gateway](https://github.com/rebecazm129-commits/xclaude-gateway) | 2 | Mac audit gateway; tiny adoption |
| [astral-sh/uv](https://github.com/astral-sh/uv) | 90,986 | Python packaging incumbent |
| [astral-sh/ruff](https://github.com/astral-sh/ruff) | 50,203 | Quality tooling incumbent |
| [openai/codex](https://github.com/openai/codex) | 130,291 | Agent CLI adoption proxy |
| [anthropics/claude-code](https://github.com/anthropics/claude-code) | 152,715 | Agent workflow adoption proxy |
| [zizmorcore/zizmor](https://github.com/zizmorcore/zizmor) | 6,745 | Workflow security incumbent |
| [rhysd/actionlint](https://github.com/rhysd/actionlint) | 4,344 | CI correctness incumbent |
| [oasdiff/oasdiff](https://github.com/oasdiff/oasdiff) | 1,427 | API diff precedent, OpenAPI-focused |
| [getsops/sops](https://github.com/getsops/sops) | 23,470 | Established secrets workflow |
| [trufflesecurity/trufflehog](https://github.com/trufflesecurity/trufflehog) | 28,626 | Established credential scanner |

These 17 available repositories were reviewed for description, language, license metadata, activity and fit. No source code was copied. The remaining trend-discovered repository metadata is retained in repositories.json.

## Momentum, separated from total stars

### [Daily Trending](https://github.com/trending?since=daily)
- [cloudflare/security-audit-skill](https://github.com/cloudflare/security-audit-skill): 1,997 stars today.
- [vllm-project/vllm](https://github.com/vllm-project/vllm): 439 stars today.
- [stablyai/orca](https://github.com/stablyai/orca): 1,543 stars today.
- [headroomlabs-ai/headroom](https://github.com/headroomlabs-ai/headroom): 477 stars today.
### [Weekly Trending](https://github.com/trending?since=weekly)
- [morluto/rea](https://github.com/morluto/rea): 157,631 stars this week.
- [anthropics/claude-plugins-official](https://github.com/anthropics/claude-plugins-official): 5,650 stars this week.
- [K-Dense-AI/scientific-agent-skills](https://github.com/K-Dense-AI/scientific-agent-skills): 4,549 stars this week.
- [ruvnet/ruflo](https://github.com/ruvnet/ruflo): 3,143 stars this week.
### [Monthly Trending](https://github.com/trending?since=monthly)
- [paperclipai/paperclip](https://github.com/paperclipai/paperclip): 24,372 stars this month.
- [debpalash/VoiceStudio](https://github.com/debpalash/VoiceStudio): 45,470 stars this month.
- [vectorize-io/hindsight](https://github.com/vectorize-io/hindsight): 28,261 stars this month.
- [heygen-com/hyperframes](https://github.com/heygen-com/hyperframes): 16,644 stars this month.

The visible pattern is agent orchestration, skills, memory, inference and agent security. Large weekly gains may reflect launches or hype; they do not prove durable retention. Contract testing addresses a persistent integration problem rather than competing on model quality or star counts.

## Discussion and launch signals

- [Recent HN production-use discussion](https://news.ycombinator.com/item?id=49548600): qualitative integration demand, not a representative survey.
- [HN security discussion](https://news.ycombinator.com/item?id=43600192): older context on tool trust boundaries.
- [Developer report: definition drift](https://www.reddit.com/r/mcp/comments/1x0ni45/anyone_actually_checking_when_mcp_tool/): October 8 report of observed schema changes, very small vote sample.
- [Offline pin-check competitor discussion](https://www.reddit.com/r/mcp/comments/1x6lcfr/i_built_a_readonly_checker_that_tells_you_when_an/): October 15; author explicitly discusses missing output-schema coverage. Marketing claims are not independently verified.
- [Product Hunt MCP Defender](https://www.producthunt.com/products/mcp-defender) and [MCP Snitch](https://www.producthunt.com/products/mcp-snitch?launch=mcp-snitch): evidence of competing security products; current launch dates and adoption metrics were not reliably available, so not scored as recent growth.
- [MCP tools specification](https://modelcontextprotocol.io/specification/2025-06-18/server/tools): primary reference for tools/list, inputSchema and outputSchema. This tool validates exported contracts, not every protocol-version requirement.

## Weighted opportunity matrix

Scores 1–5, subjective engineering judgments. Weights: demand 20%, differentiation 20%, feasibility 15%, usefulness 15%, maintainability 10%, testable MVP 15%, community potential 5%. Total is weighted score out of 5.

| Opportunity | Demand | Difference | Feasible | Useful | Maintain | Testable | Community | Total |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| MCP contract diff + fixture replay | 4 | 4 | 5 | 5 | 5 | 5 | 3 | 4.50 |
| GitHub Actions risk delta | 4 | 2 | 5 | 4 | 4 | 5 | 3 | 3.85 |
| Agent context budget profiler | 5 | 2 | 4 | 4 | 3 | 3 | 4 | 3.55 |
| Skill instruction drift checker | 4 | 2 | 5 | 4 | 4 | 4 | 3 | 3.70 |
| Local agent sandbox policy inspector | 5 | 3 | 2 | 5 | 2 | 2 | 4 | 3.35 |

1. **Contract replay:** SDK/inspector adoption and recent drift reports; compete with pin checkers and proxies through baseline-valid input/output evidence and CI-friendly offline use. Small, testable and maintainable; modest community size is a risk.
2. **Actions risk delta:** persistent supply-chain need, but zizmor/actionlint and the account’s actionvet already cover much of the space. Easy MVP; little differentiation.
3. **Context budget profiler:** strong headroom/context-mode momentum; token accounting varies by model and truncation can obscure behavior. Crowded and harder to validate.
4. **Skill drift:** skills are trending, but this account already has skillcheck/agentrot; avoid duplicating concurrent work.
5. **Sandbox inspector:** OpenShell momentum and genuine safety need; OS-specific enforcement, incomplete policy models and testing burden make a trustworthy MVP harder.

## Decision

Select Capability Delta. It targets maintainers reviewing MCP releases, not runtime browsing. Output examples and baseline validation differentiate it from description pinning, while the default drift gate remains conservative. The account’s existing MCPScope README describes an interactive debugger/proxy, not this offline CI workflow. Public account repository descriptions were checked read-only to avoid duplicating known work; unseen concurrent local work cannot be ruled out.

Research limitations: one observation window; no longitudinal API star sample; discussion samples are small and self-selected; repository counts and Trending rankings change. No claimed performance, market-size, retention or security guarantees.
