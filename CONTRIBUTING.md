# Adding a skill

1. Create `skills/<name>/` with `SKILL.md`, `skill.json`, and `CHANGELOG.md`.
2. `SKILL.md` frontmatter needs `name` and a `description` stating both what the
   skill does and when to trigger it.
3. Keep `SKILL.md` lean; push detail into `references/` for progressive disclosure.
4. Ship executable verification wherever possible — a skill that cannot check its
   own environment fails silently.
5. Add the skill to `registry.json` and the README table.
6. Verify against the real tool before committing; record it in `skill.json`.

## Provenance rules

Never present upstream work as original. Set `origin` correctly, and for derived
skills include the upstream repo, license, and license URL in `skill.json` and
`SKILL.md`, marking what is derived vs. original. A separate `NOTICE.md` is
optional.
