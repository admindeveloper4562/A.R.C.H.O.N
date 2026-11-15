# Owner approval workflow

Owner approval is a signed, digest-bound receipt. The architecture SHA flag in
SQLite is not an owner identity and is never sufficient by itself.

## Trust anchor

The operator provisions an owner Ed25519 public key in a private local
`allowed_signers` file. The private key remains outside Astra state and is used
only by the owner for an interactive signing operation.

```bash
STATE="$HOME/.local/state/archon-astra"
mkdir -m 700 -p "$STATE/owner"
install -m 600 /path/to/owner-ed25519.pub "$STATE/owner/owner-ed25519.pub"
printf 'owner %s\n' "$(cat "$STATE/owner/owner-ed25519.pub")" > "$STATE/owner/allowed_signers"
chmod 600 "$STATE/owner/allowed_signers"
```

The trusted signer file is hashed into every receipt. Changing it invalidates
existing receipts.

## BASE-008

After inspecting the emitted payload and exact packet digests, prepare a
request without changing SQLite:

```bash
PYTHONPATH=bootstrap/astra-one python3 -B -m astra_one.linux_cli \
  --home "$STATE" owner-approval-request BASE-008 --owner-id owner
```

The owner must inspect the JSON and then sign the displayed message file:

```bash
ssh-keygen -Y sign -f /path/to/owner-ed25519 \
  -n archon-owner-approval-v1 \
  "$STATE/private/owner-approvals/BASE-008/BASE-008.message"
chmod 600 "$STATE/private/owner-approvals/BASE-008/BASE-008.message.sig"
```

The deterministic Master verifies the signature, packet SHA, full architecture
SHA, bounded focus SHA, parent payload SHA, source checkpoint, integration
checkpoint and scope before recording the owner receipt and BASE-008.S01–S03
receipts in one transaction:

```bash
PYTHONPATH=bootstrap/astra-one python3 -B -m astra_one.linux_cli \
  --home "$STATE" approve-owner BASE-008 \
  --owner-receipt "$STATE/private/owner-approvals/BASE-008/BASE-008.json"
```

No command in this workflow publishes, deploys, cuts over SDA, clears a pause
marker or changes `main`.

## Review-only source authorization

For SDA-001, the owner decision payload must bind source commit
`5227b91d2725bf4be4336a5ad26189fdf1034704`, candidate
`a82c09336868f8abf424da370a3e62debc802373`, the review-only destination, and
the restrictions against redistribution, relicensing, installation and
production deployment. It must also state that third-party rights remain
unresolved. Prepare that JSON with the generic helper, sign it with the same
owner key, and let independent QC verify the receipt before reconsidering F1.

The receipt is evidence of the owner's internal review authorization only; it
does not assert or grant third-party license rights.
