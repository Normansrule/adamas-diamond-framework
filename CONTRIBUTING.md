# Contributing to ADAMAS

Thank you for helping. The repository has a few firm rules that keep it trustworthy.

## The rules

1. **Every formula, constant, and figure carries a `[bibkey]`** that exists in `references/refs_a.psv` or `references/refs_b.psv`.
2. **Never invent a citation.** If you are unsure of a volume or page, write `TODO: verify` in the locator field and set the status to `K`. Do not type Digital Object Identifiers (DOIs) from memory; let `tools/verify_refs.py` retrieve them.
3. **Separate demonstrated from proposed.** Proposals belong in Chapter 11 or must be labeled "proposal of this repository."
4. **Label evidence.** Peer-reviewed (P), news (N), or vendor statement (V). Vendor claims never support a physics claim.
5. **Write for every reader.** Each chapter opens with a plain-language summary. Write acronyms out in full on first use, with the short form in parentheses.
6. **Style.** United States English, Oxford commas, a warm professional tone.

## Adding a reference

Append one line to the appropriate `.psv` file:

```
key | Authors | year | Title | Venue | volume, pages | tags | K
```

Keys are `firstauthorYEAR` in lowercase, with a short suffix if needed. Then:

```bash
cd tools
python build_refs.py          # regenerates references.bib and REFERENCES.md
python check_citations.py     # must print no MISSING lines
python verify_refs.py         # optional, needs internet; promotes confidence in K entries
```

## Before you open a pull request

```bash
pytest -q
python examples/make_all_figures.py
```

Python 3.10 or newer; the reference environment is Python 3.12 under conda.
