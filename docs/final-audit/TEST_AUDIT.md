# Current test audit

Exact application source candidate: `2e24790c983bf3c8d2d0f99de7a086427355f172` (tree `5dc151512b5df78ecf5e911a93222ad2a44fb94b`).

- Root regression: 637/637 passed on Python 3.12.3 and 637/637 on Python 3.11.18; zero failures/skips in the root runs.
- Coordination: 191/191 passed.
- Local CI equivalent: 42 checks with the two expected-negative outcomes classified correctly.
- Independent QC repeated the full verifier twice with different color environment settings and observed matching wheel/sdist hashes.
- Container smoke and archive-backed fresh restart passed.
- The 72-task inference/data soak was run against a previous whole-source SHA with an identical `src/` tree; it was not multi-hour and is not exact-whole-source soak evidence.
- GitHub Actions unavailable due billing; not run.

Full report hashes are in [QUALIFICATION_ADDENDUM_2E24790.json](QUALIFICATION_ADDENDUM_2E24790.json).
