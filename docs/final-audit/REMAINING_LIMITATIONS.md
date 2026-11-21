# Remaining Linux release limitations

The release verdict remains CONDITIONAL. The evidence does not justify an unattended production service or PASS.

1. Production owner-signed delegation and trust provisioning are not present; test signers are disposable only.
2. A separately protected AEGIS watchdog, crash/reboot recovery, signed rollback application, and failback soak remain unqualified. Native SDA cutover remains disabled.
3. Full ALFRED/CORTEX/SAGE/HORIZON, SMITH/QC/merge, and controlled-clock RELAY/ATLAS workflows were not run end to end.
4. Native queue throughput was tested serially; parallel worker fairness is not proven. The live qwen3:4b soak lasted 289.326 seconds, not multiple hours.
5. GitHub Actions was not run because billing was unavailable. Local CI does not provide hosted enforcement.
6. Windows, Apple, device-specific Blender, live feeds, external model providers, finance accounts, and communications integrations were not validated.
7. The host user service remains disabled. Existing public Git history may retain earlier absolute home-path references; current tracked documentation has been normalized without rewriting history.

Detailed exact-source evidence is in FINAL_RELEASE_VERDICT.md and its linked reports.
