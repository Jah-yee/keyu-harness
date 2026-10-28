# Evidence Storage Policy

This directory is reserved for materials actually obtained and lawfully retained during research. It is currently a scaffold; **an empty directory does not mean that original internal artifacts have been acquired**.

Recommended layout:
- `raw/` — read-only original public captures or lawfully supplied source files;
- `manifests/` — hashes, acquisition metadata, commit IDs and file-tree manifests;
- `derived/` — parsed outputs, diffs, charts and analysis products;
- `simulated/` — synthetic data only, explicitly marked.

Never overwrite an original capture with a normalized or redacted copy. Keep derived files separate and link them to their input hashes. Do not place credentials, private personal data, or unauthorized confidential company material here.
