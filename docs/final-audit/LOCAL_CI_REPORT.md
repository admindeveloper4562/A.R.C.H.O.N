# Local release verification report

Qualified application source SHA: 759e78dc04c61ed7f01a4b714d35ab8c999d2a85. Source tree: 7472b26bbc24538851a920ff89ac9a65206050a8. Package version: 0.0.3. Build environment: Linux, Python 3.12.3.

## Result

- Full local release verifier: PASS, exit 0.
- Root regression suite: 635 passed, 0 failed, 0 skipped in 47.793 seconds; verifier wall time 48.243 seconds.
- Local CI equivalent: 42 checks, all classified as expected and passed. Forty returned 0; two expected negative checks returned 2 for caller trust-store rejection and 1 for uninstall absence.
- Coordination suite: 191 passed, 0 failed, 0 skipped in 62.389 seconds.
- Dependency, secret, and source scans passed. pip-audit 2.10.1 reported zero known vulnerabilities.
- Reproducible duplicate wheel/sdist builds produced identical hashes. Fresh Python 3.12.3 package and CLI checks passed.
- Clean-container smoke and saved-image archive reload passed; source, health, module registration, and SQLite integrity were verified.
- Python 3.11 installation is not evidenced for this exact candidate. Hosted GitHub Actions was not run because billing was unavailable.
- Independent QC passed for the root evidence source 759e78dc04c61ed7f01a4b714d35ab8c999d2a85. The runbook marker test on a follow-up docs/test candidate passed 1/1, but the full verifier on that child candidate is pending.

## Artifact checksums

- Wheel, 303,942 bytes: 66d6ac2e977c65f7d48321852d7021383ab3c38540f2299612a56d93dd15f879.
- Source distribution, 346,655 bytes: 9f585df16ac92b14d088a69fb20fa24a3573029ecefc873a526b8f982af70aeb.
- Root saved container image archive: 4a6d21a613c9611c63c94c2a2410b1817c53c574ed49d5e537d86dbc9a258709.

Qualification addendum SHA-256: d207ae3841092a77e231fb7cda821c2f564bc27c52dc884a226c9272994736ee. Selected source-bound evidence report hashes are recorded in that addendum.
