# teleconference-mcp — TODO (from 2026-06-12 assessment)

Fix order matters. Total ≈ one focused day. See ASSESSMENT.md for full detail.

## 1. Rescue the uncommitted work — DO FIRST (~30 min)
- [ ] Commit the 43 dirty entries in logical chunks:
  - chunk A: test infrastructure (tests/test_tools_*.py, conftest changes, pytest.ini removal)
  - chunk B: FleetStartMode vendoring (scripts/, start.ps1 changes)
  - chunk C: LiveKit 2026 (livekit.yaml, agent.py, docs/LIVEKIT.md, docs/FEATURES.md)
  - chunk D: docs (AGENTS.md, ASSESSMENT.md, TODO.md, docs/llms.txt, CHANGELOG.md)
  - chunk E: rest (pyproject.toml, uv.lock, packages/* tool changes)
- [ ] DO NOT commit: pyproject.toml.bak, ASSESSMENT_*.bak (delete instead)
- [ ] `git pull --rebase` — expect conflicts in start.ps1/docs from the 3 upstream
      FleetStartMode commits; resolve, then push

## 2. Fix the 5 broken tests (~15 min)
- [ ] Restore `temp_lancedb` fixture in `apps/agent/tests/conftest.py`
      (root tests/conftest.py is out of scope for apps/agent/tests — pytest
      conftest visibility is directory-based)
- [ ] Verify: `uv run pytest tests/ apps/agent/tests/ -q` → 95 passed

## 3. CI repair (~1-2 h)
- [ ] pyproject.toml: add `; sys_platform == 'win32'` markers to pywin32,
      pywinctl, pynput, mss; `uv lock` to regenerate
- [ ] Verify lazy-import fallbacks in remoting_mcp, contacts_substrate,
      vision_analyze for non-Windows
- [ ] ci.yml web job: drop working-directory, run `npm ci` at repo root, then
      `npm run lint --workspace=web`, `npx tsc --noEmit -p apps/web`,
      `npm run test --workspace=web`
- [ ] Push, watch for first-ever green run

## 4. Untrack runtime artifacts (~30 min)
- [ ] `git rm --cached -r apps/agent/lancedb_data`
- [ ] `git rm --cached packages/conferencing_mcp/conference.db apps/agent/contacts_cache.json apps/web/lint_output.txt`
- [ ] Audit git history of contacts_cache.json for real PII (public repo);
      decide: history rewrite vs accept

## 5. Delete dead files (~15 min)
- [ ] `docker-compose.yml` (stale Redis-only, wrong port 6379)
- [ ] `pyproject.toml.bak`, `scripts/FleetStartMode.ps1.*.bak` (3×)
- [ ] `packages/conferencing_mcp/package.json`, `package-lock.json`,
      `tsconfig.json` (legacy TS remnants; Turbo stops treating it as JS workspace)
- [ ] Root logs: mcp_server.log, agent_industrial.log, build_agent_log*.txt

## 6. justfile fix (~5 min)
- [ ] `agent` recipe: `.\venv\Scripts\activate; python agent.py dev`
      → `uv run python agent.py dev`

## 7. Version sync (~15 min)
- [ ] pyproject.toml 2.2.0 → 2.3.0; release the CHANGELOG 2.3.0 entry with date
- [ ] README: Python badge 3.13+ vs prereq 3.12+ — pick one (requires-python is >=3.12)

## 8. Coverage gate (~30 min, after CI is green)
- [ ] ci.yml pytest step: add `--cov --cov-fail-under=70`
- [ ] Ratchet upward later

## 9. Doc cleanup pass (~1 h, lowest priority)
- [ ] PRD.md: fix duplicate §7/§8 numbering, move shipped features out of
      "Phase 2 Planned", fix "Fast_MCP 2.14.4" → FastMCP 3.2, fix review date
- [ ] CHANGELOG.md: remove stray mid-file [Unreleased], move Keep-a-Changelog
      preamble to top, delete stale "Version History" footer
