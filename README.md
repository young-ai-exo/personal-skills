# personal_skills

Version-controlled agent skills for [Codex](https://developers.openai.com/codex/)
and Claude Code.

📖 **[Browse the documentation site →](https://harnessyoung.github.io/personal-skills/)**

## Skills

| Skill | Version | Origin | Verified against | Docs |
| --- | --- | --- | --- | --- |
| [`cnsplots`](skills/cnsplots) | 1.8.0 | derivative of [faridrashidi/cnsplots](https://github.com/faridrashidi/cnsplots) (BSD-3-Clause) | cnsplots 0.8.0 | [page](https://harnessyoung.github.io/personal-skills/skills/cnsplots.html) |
| [`python-script-conventions`](skills/python-script-conventions) | 1.4.0 | original (Yusheng Yang, MIT) | snapshot 2026-08-12 | [page](https://harnessyoung.github.io/personal-skills/skills/python-script-conventions.html) |

Machine-readable index: [`registry.json`](registry.json).

## Layout

```
skills/<name>/
  SKILL.md        # the skill itself (YAML frontmatter + instructions)
  skill.json      # version, provenance, verification record
  CHANGELOG.md    # SemVer history for the skill
  NOTICE.md       # upstream attribution and license
  references/     # progressive-disclosure docs
  scripts/        # executable helpers
  templates/      # code templates
```

## Install

```bash
git clone https://github.com/HarnessYoung/personal-skills.git
cp -R personal-skills/skills/cnsplots ~/.codex/skills/cnsplots
cp -R personal-skills/skills/python-script-conventions ~/.codex/skills/python-script-conventions
```

Claude Code uses `~/.claude/skills/` instead. Verify a skill's environment:

```bash
python3 ~/.codex/skills/cnsplots/scripts/check_env.py
```

## Versioning

Each skill carries its **own** SemVer version in `skill.json`, independent of the
upstream tool it wraps:

- **major** — breaking workflow change; agents must relearn the flow
- **minor** — new capability, script, or reference doc
- **patch** — clarification or fix with no behavioral change

Every skill records `verification.verified_against_package_version`. When the
wrapped tool releases a new version, re-run the bundled checks and bump that
field with a changelog entry.

## Provenance policy

Every skill declares one `origin`:

- `original` — written from scratch here
- `derivative-enhancement` — based on an upstream skill, with upstream repo,
  license, and a file-level breakdown in `NOTICE.md`
- `vendored` — copied essentially unchanged

Derived skills keep their upstream license and credit the original author.

## License

BSD-3-Clause. See [`LICENSE`](LICENSE). Derived skills additionally carry upstream
terms; see each skill's `NOTICE.md`.
