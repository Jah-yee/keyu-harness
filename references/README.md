# References, Claims, and Artifacts

This directory separates bibliographic references, source provenance, claim support, and artifact lineage.

- `bibliography.bib`: formal publications, software projects, model configuration pages, and reporting.
- `source_registry.csv`: source role, original title, URL, revision, review state, capture state, and limitations.
- `claim_ledger.csv`: claims, source IDs, support relation, assessment state, missing evidence, and next action.
- `artifact_registry.csv`: public baseline references and historical artifacts that remain unavailable.
- `unknowns.csv`: unresolved questions, required evidence, and priority.

## Important distinctions

A source role is not a numerical trust score. A page can be a primary source for what the page says while remaining insufficient to verify the original material it displays. `PAGE_REVIEWED` does not mean locally captured. `REVISION_IDENTIFIED` does not mean the file has been downloaded or hashed.

Only populate `sha256` and `local_path` after obtaining the actual file. Do not use a Git commit ID as a file hash. Keep syndicated copies of the same article linked to the same reporting origin rather than counting them as independent corroboration.
