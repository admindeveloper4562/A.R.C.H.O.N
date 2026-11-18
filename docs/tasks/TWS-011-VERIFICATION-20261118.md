# TWS-011 verification — Blender Linux candidate

This is a bounded Linux/Blender verification packet for `TWS-011`. It does
not claim Apple SceneKit, Xcode, macOS or physical-device validation.

## Pinned inputs and outputs

| Item | SHA-256 | Result |
| --- | --- | --- |
| Source blockout `.blend` | `23e20c5ba2da1f68b90243368b42b9fb63ac3855c672b04468cfc942fce394bf` | Opened read-only |
| Blender 5.3.0 binary | `baaa36cb5d7a35092388e6d123739b0829012c252b0705bc2debec292e4ebffb` | Exit 0 |
| Generated editable `.blend` | `1c3888a6122729e7a1aa43c7f3999f9adba55eac1974d1e333a3916e30959c3f` | Reopened successfully |
| Generated `.usdz` | `30b3e13de9b42091c4ce432c63e51a1fe893bc86da3d5c2fe23ff8124012633d` | Valid USDZ archive |

The generated candidate contains eight source meshes, one root armature and
eight armature modifiers binding the blockout vertices to `root`. The USDZ
archive contains one USD binary and one generated material texture.

## Reproduction

```text
blender --background --factory-startup --python prepare_candidate.py
  exit 0; TWS_CANDIDATE ... 8 1; USD export succeeded

blender --background --factory-startup --python-expr <reopen candidate>
  BLEND_VALID 8 1 8; exit 0

file jarvis_tws_blockout_rigged.usdz
  Zip archive data
```

The deterministic Master binds the external evidence packet to these artifact
hashes and keeps the follow-on native-device requirement unclaimed. TWS-012
and later tasks must not inherit a fabricated Apple/device pass.
