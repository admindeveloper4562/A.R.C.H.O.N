# Disk and cleanup report

| Measurement | Value |
| --- | ---: |
| Home filesystem before migration checkpoint | 1.7G available in the supplied preflight |
| Home filesystem at final handoff snapshot | 920M available |
| Old Astra state | 4.6G |
| New ARCHON source checkout | 29M |
| New ARCHON runtime state | 37M |
| Final audit checkpoint | 757M |
| Actual space reclaimed | 0 bytes |

The available-space decrease is attributable to preserved recovery artifacts and the new canonical checkout, not deletion. The filesystem is critically full. Cleanup remains a dry run until the owner approves the exact manifest and every live-path/reference check is repeated.
