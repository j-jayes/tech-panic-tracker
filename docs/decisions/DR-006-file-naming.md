# DR-006 — File naming convention for source texts and analysis assets

**Date:** 2026-08-26 · **Status:** accepted · **Closes:** OPEN-QUESTIONS 18

## Decision

Files under `data/raw/`, `data/interim/`, and `analysis/` follow:

```
{first-author-surname}{-etal}?-{year}-{short-title-slug}.{ext}
```

lowercase ASCII, hyphen-separated, no spaces, apostrophes, or non-ASCII characters; slug of at most five words; institutional authors slugged as the institution (`mckinsey-2017-jobs-lost-jobs-gained.pdf`); collisions disambiguated with `-YYYY-MM` or `-v2`. The convention and its edge cases live in `.claude/skills/file-naming/SKILL.md` so the assistant applies it without being asked each time.

Worked example — the file that prompted this decision:

| | |
|---|---|
| as downloaded | `&lt;The&gt; technology trap capital, labor, and power in the -- Carl Benedikt Frey -- Princeton University Press, Princeton, New Jersey, 2019 -- isbn13 9780691172798 -- 39173bd1462e8d1b39ff2db75a464cbc -- Anna's Archive.pdf` |
| renamed | `frey-2019-technology-trap.pdf` |

## Rationale

The original name is not merely ugly: it contains literal HTML-escaped angle brackets (`&lt;`, `&gt;`), a Unicode right single quotation mark, and 190 characters of spaces and double hyphens. Every shell command touching it needs quoting and still trips on the escapes; it breaks path handling in R and Python chunks; and it embeds a content hash from the download source rather than anything a reader would recognise. Reproducibility is the point of the repository, and a path a collaborator cannot type is a path that does not reproduce.

## Consequences

- `data/raw/` is git-ignored, so renames are local; the durable record of any raw file is its `full_text_location` pointer in `sources.csv`, which must be updated in the same commit as any rename.
- `.claude/skills/file-naming/SKILL.md` created.
- `data/raw/README.md` states the convention for anyone adding files by hand.
