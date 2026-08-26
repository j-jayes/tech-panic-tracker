---
name: file-naming
description: Naming convention for source texts, extracted passages, and analysis assets in this repository. Use whenever adding, downloading, renaming, or referencing a file under data/raw/, data/interim/, or analysis/ — especially for PDFs downloaded from archives, publishers, or shadow libraries, whose original filenames are unusable.
---

# File naming

## The convention

```
{first-author-surname}{-etal}?-{year}-{short-title-slug}.{ext}
```

- **lowercase ASCII only** — no spaces, apostrophes, ampersands, brackets, HTML escapes, or non-ASCII characters. Hyphens separate everything.
- **surname**: the first author's family name, unaccented (`lof` for Löf). Institutional authors use the institution slug: `mckinsey`, `oecd`, `pwc`, `wef`, `bls`.
- **`-etal`**: add for three or more authors (`freyosborne` for exactly two is also fine when the pair is the recognised unit, as with `frey-osborne-2013`).
- **year**: four digits, the publication year. Add `-MM` only to disambiguate two items from the same author-year (`wef-2020-01-future-of-jobs`).
- **slug**: at most five words from the title, stopwords dropped. `The Technology Trap: Capital, Labor, and Power in the Age of Automation` → `technology-trap`.
- **extension**: lowercase, real (`.pdf`, `.txt`, `.json`, `.csv`).

## Worked examples

| Source | File name |
|---|---|
| Frey, *The Technology Trap* (2019) | `frey-2019-technology-trap.pdf` |
| Frey & Osborne, *The Future of Employment* (2013) | `frey-osborne-2013-future-of-employment.pdf` |
| McKinsey Global Institute, *Jobs Lost, Jobs Gained* (2017) | `mckinsey-2017-jobs-lost-jobs-gained.pdf` |
| OECD WP 189, Arntz, Gregory & Zierahn (2016) | `arntz-etal-2016-risk-of-automation.pdf` |
| A passage extracted for LLM coding | `frey-2019-technology-trap-p304.txt` |

## Anti-example

This is what a shadow-library download looks like, and what it must never stay as:

```
<The> technology trap capital, labor, and power in the -- Carl Benedikt Frey --
Princeton University Press, Princeton, New Jersey, 2019 -- isbn13 9780691172798
-- 39173bd1462e8d1b39ff2db75a464cbc -- Anna's Archive.pdf
```

It carries literal HTML escapes (`&lt;`, `&gt;`), a Unicode right single quote, double-hyphen separators, and a download-side content hash. It needs shell quoting that still breaks, it defeats tab completion, and it trips path handling in R and Python chunks. Rename on arrival, before anything references it.

## Rules that go with the name

1. **`data/raw/` is git-ignored.** A rename is local only, so the durable record of any raw file is its `full_text_location` value in `data/processed/sources.csv`. Update that pointer in the same commit as any rename — an unfindable full text is a broken provenance chain, which Principle II does not allow.
2. **Never commit copyrighted full texts** (constitution, Open-Science Constraints). Public-domain or open-licence texts may be committed by exception, noted in `data/raw/README.md`.
3. **Bibliographic detail belongs in `sources.csv`**, not in the filename. The filename only has to be unique, typable, and recognisable; the ISBN, publisher, and city live in the data.
4. **Extracted passages** keep the parent file's stem and add a locator suffix (`-p304`, `-ch12`), so the passage's provenance is legible from its path alone.
