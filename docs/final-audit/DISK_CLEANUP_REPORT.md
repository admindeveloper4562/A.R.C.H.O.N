# Disk and cleanup report

| Measurement | Value |
| --- | ---: |
| Home filesystem before migration checkpoint | 1.7G available in the supplied preflight |
| Home filesystem at final handoff snapshot | 880,873,472 bytes available (about 840 MiB; 100% used) |
| Old Astra state | 4,341,176,473 bytes (about 4.05 GiB) |
| New ARCHON source checkout | 42,221,734 bytes (about 40.3 MiB) |
| New ARCHON runtime state | 102,913,550 bytes (about 98.2 MiB) |
| Final audit checkpoint | 792,685,749 bytes (about 756 MiB) |
| Actual space reclaimed | 0 bytes |

The available-space decrease is attributable to preserved recovery artifacts and the new canonical checkout, not deletion. The filesystem is critically full. Cleanup remains a dry run until the owner approves the exact manifest and every live-path/reference check is repeated.
