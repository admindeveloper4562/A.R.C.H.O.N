from __future__ import annotations

import hashlib
import io
import json
from pathlib import Path
import os
import sys
import tarfile
import tempfile
import unittest
from subprocess import CompletedProcess
from unittest.mock import patch

from tools.container_smoke import inspect_oci_image_archive, release_image_ref
from tools.verify_release import Verification


def _write_oci_archive(
    path: Path,
    source_sha: str,
    *,
    embedded_source_sha: str | None = None,
    ref_name: str | None = None,
    image_name: str | None = None,
) -> tuple[str, str]:
    image_ref = release_image_ref(source_sha)
    config = {
        "architecture": "amd64",
        "os": "linux",
        "config": {"Env": [f"ARCHON_SOURCE_SHA={embedded_source_sha or source_sha}"]},
    }
    config_bytes = json.dumps(config, sort_keys=True, separators=(",", ":")).encode()
    config_digest = "sha256:" + hashlib.sha256(config_bytes).hexdigest()
    manifest = {
        "schemaVersion": 2,
        "mediaType": "application/vnd.oci.image.manifest.v1+json",
        "config": {
            "mediaType": "application/vnd.oci.image.config.v1+json",
            "digest": config_digest,
            "size": len(config_bytes),
        },
        "layers": [],
    }
    manifest_bytes = json.dumps(manifest, sort_keys=True, separators=(",", ":")).encode()
    manifest_digest = "sha256:" + hashlib.sha256(manifest_bytes).hexdigest()
    artifact_config = b"{}"
    artifact_config_digest = "sha256:" + hashlib.sha256(artifact_config).hexdigest()
    artifact = {
        "schemaVersion": 2,
        "mediaType": "application/vnd.oci.image.manifest.v1+json",
        "artifactType": "application/vnd.example.attestation.v1",
        "config": {
            "mediaType": "application/vnd.oci.empty.v1+json",
            "digest": artifact_config_digest,
            "size": len(artifact_config),
        },
        "layers": [],
        "subject": {
            "mediaType": "application/vnd.oci.image.manifest.v1+json",
            "digest": manifest_digest,
            "size": len(manifest_bytes),
        },
    }
    artifact_bytes = json.dumps(artifact, sort_keys=True, separators=(",", ":")).encode()
    artifact_digest = "sha256:" + hashlib.sha256(artifact_bytes).hexdigest()
    inner_index = {
        "schemaVersion": 2,
        "mediaType": "application/vnd.oci.image.index.v1+json",
        "manifests": [
            {
                "mediaType": "application/vnd.oci.image.manifest.v1+json",
                "digest": manifest_digest,
                "size": len(manifest_bytes),
                "platform": {"architecture": "amd64", "os": "linux"},
            },
            {
                "mediaType": "application/vnd.oci.image.manifest.v1+json",
                "digest": artifact_digest,
                "size": len(artifact_bytes),
            },
        ],
    }
    inner_index_bytes = json.dumps(inner_index, sort_keys=True, separators=(",", ":")).encode()
    image_id = "sha256:" + hashlib.sha256(inner_index_bytes).hexdigest()
    tag = image_ref.rsplit(":", 1)[1] if ref_name is None else ref_name
    index = {
        "schemaVersion": 2,
        "mediaType": "application/vnd.oci.image.index.v1+json",
        "manifests": [{
            "mediaType": "application/vnd.oci.image.index.v1+json",
            "digest": image_id,
            "size": len(inner_index_bytes),
            "annotations": {
                "io.containerd.image.name": image_name or f"docker.io/library/{image_ref}",
                "org.opencontainers.image.ref.name": tag,
            },
        }],
    }
    index_bytes = json.dumps(index, sort_keys=True, separators=(",", ":")).encode()
    legacy_manifest = [{
        "Config": "blobs/sha256/" + config_digest.split(":", 1)[1],
        "RepoTags": [image_ref],
        "Layers": [],
    }]
    members = {
        "index.json": index_bytes,
        "manifest.json": json.dumps(legacy_manifest).encode(),
        "blobs/sha256/" + image_id.split(":", 1)[1]: inner_index_bytes,
        "blobs/sha256/" + manifest_digest.split(":", 1)[1]: manifest_bytes,
        "blobs/sha256/" + config_digest.split(":", 1)[1]: config_bytes,
        "blobs/sha256/" + artifact_digest.split(":", 1)[1]: artifact_bytes,
        "blobs/sha256/" + artifact_config_digest.split(":", 1)[1]: artifact_config,
    }
    with tarfile.open(path, "w") as archive:
        for name, data in members.items():
            member = tarfile.TarInfo(name)
            member.size = len(data)
            archive.addfile(member, io.BytesIO(data))
    return image_id, config_digest


class VerificationSubprocessTests(unittest.TestCase):
    def test_source_date_epoch_comes_from_git_commit_time(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            verifier = Verification(Path(directory))
            result = CompletedProcess(["git"], 0, stdout="1795190000" + chr(10), stderr="")
            with patch.object(verifier, "run", return_value=result) as run:
                self.assertEqual(verifier.source_date_epoch("a" * 40), "1795190000")
        run.assert_called_once_with(
            "source-date-epoch", ["git", "show", "-s", "--format=%ct", "a" * 40]
        )

    def test_source_date_epoch_rejects_non_numeric_git_output(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            verifier = Verification(Path(directory))
            result = CompletedProcess(["git"], 0, stdout="unknown" + chr(10), stderr="")
            with patch.object(verifier, "run", return_value=result):
                with self.assertRaisesRegex(RuntimeError, "numeric SOURCE_DATE_EPOCH"):
                    verifier.source_date_epoch("b" * 40)

    def test_color_environment_is_sanitized_for_machine_readable_tools(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            with patch.dict(os.environ, {"FORCE_COLOR": "1", "CLICOLOR_FORCE": "1"}, clear=False):
                verifier = Verification(Path(directory))

        self.assertNotIn("FORCE_COLOR", verifier.environment)
        self.assertNotIn("CLICOLOR_FORCE", verifier.environment)
        self.assertEqual(verifier.environment["NO_COLOR"], "1")
        self.assertEqual(verifier.environment["PIP_NO_COLOR"], "1")

    def test_records_an_expected_nonzero_exit(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            verifier = Verification(Path(directory))
            result = verifier.run(
                "expected-rejection",
                [sys.executable, "-c", "raise SystemExit(2)"],
                expected_returncodes=(2,),
            )
        self.assertEqual(result.returncode, 2)
        self.assertEqual(verifier.records[0]["exit_classification"], "expected")
        self.assertEqual(verifier.records[0]["expected_returncodes"], [2])

    def test_unexpected_exit_is_reported_and_raises(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            verifier = Verification(Path(directory))
            with self.assertRaisesRegex(RuntimeError, r"expected \(1,\)"):
                verifier.run(
                    "unexpected-success",
                    [sys.executable, "-c", "raise SystemExit(0)"],
                    expected_returncodes=(1,),
                )
        self.assertEqual(verifier.records[0]["exit_classification"], "unexpected")


class OciImageArchiveTests(unittest.TestCase):
    def test_candidate_image_tag_requires_a_full_source_sha(self) -> None:
        with self.assertRaisesRegex(ValueError, "full lowercase Git source SHA"):
            release_image_ref("4a83fd07")

    def test_candidate_image_tag_is_deterministic_and_source_sha_specific(self) -> None:
        source_sha = "a" * 40
        first = release_image_ref(source_sha)
        second = release_image_ref(source_sha)
        self.assertIn(source_sha, first)
        self.assertEqual(first, second)
        self.assertNotEqual(first, release_image_ref("b" * 40))

    def test_index_digest_and_source_sha_are_verified_separately_from_config_digest(self) -> None:
        source_sha = "a" * 40
        with tempfile.TemporaryDirectory() as directory:
            archive = Path(directory) / "candidate.oci.tar"
            image_id, config_digest = _write_oci_archive(archive, source_sha)
            result = inspect_oci_image_archive(
                archive,
                source_sha=source_sha,
                image_ref=release_image_ref(source_sha),
                image_id=image_id,
            )
        self.assertEqual(result["index_descriptor_digest"], image_id)
        self.assertEqual(result["config_digests"], [config_digest])
        image_ref = release_image_ref(source_sha)
        self.assertEqual(result["index_ref_name"], image_ref.rsplit(":", 1)[1])
        self.assertEqual(result["index_image_name"], f"docker.io/library/{image_ref}")
        self.assertNotEqual(image_id, config_digest)

    def test_rejects_index_descriptor_digest_mismatch(self) -> None:
        source_sha = "b" * 40
        with tempfile.TemporaryDirectory() as directory:
            archive = Path(directory) / "candidate.oci.tar"
            _, config_digest = _write_oci_archive(archive, source_sha)
            with self.assertRaisesRegex(RuntimeError, "index descriptor digest"):
                inspect_oci_image_archive(
                    archive,
                    source_sha=source_sha,
                    image_ref=release_image_ref(source_sha),
                    image_id=config_digest,
                )

    def test_rejects_wrong_source_sha_in_image_config(self) -> None:
        source_sha = "c" * 40
        with tempfile.TemporaryDirectory() as directory:
            archive = Path(directory) / "candidate.oci.tar"
            image_id, _ = _write_oci_archive(
                archive, source_sha, embedded_source_sha="d" * 40
            )
            with self.assertRaisesRegex(RuntimeError, "source SHA does not match"):
                inspect_oci_image_archive(
                    archive,
                    source_sha=source_sha,
                    image_ref=release_image_ref(source_sha),
                    image_id=image_id,
                )

    def test_rejects_wrong_index_tag_even_when_manifest_repo_tags_match(self) -> None:
        source_sha = "e" * 40
        with tempfile.TemporaryDirectory() as directory:
            archive = Path(directory) / "candidate.oci.tar"
            image_id, _ = _write_oci_archive(archive, source_sha, ref_name="archon-local")
            with self.assertRaisesRegex(RuntimeError, "unique descriptor"):
                inspect_oci_image_archive(
                    archive,
                    source_sha=source_sha,
                    image_ref=release_image_ref(source_sha),
                    image_id=image_id,
                )

    def test_rejects_archive_tag_for_another_source_sha(self) -> None:
        source_sha = "f" * 40
        with tempfile.TemporaryDirectory() as directory:
            archive = Path(directory) / "candidate.oci.tar"
            image_id, _ = _write_oci_archive(archive, source_sha)
            with self.assertRaisesRegex(RuntimeError, "not source-SHA-specific"):
                inspect_oci_image_archive(
                    archive,
                    source_sha=source_sha,
                    image_ref=release_image_ref("e" * 40),
                    image_id=image_id,
                )

    def test_rejects_wrong_oci_image_name_even_when_ref_name_matches(self) -> None:
        source_sha = "9" * 40
        with tempfile.TemporaryDirectory() as directory:
            archive = Path(directory) / "candidate.oci.tar"
            image_id, _ = _write_oci_archive(
                archive,
                source_sha,
                image_name="docker.io/library/archon-local:0.0.3",
            )
            with self.assertRaisesRegex(RuntimeError, "unique descriptor"):
                inspect_oci_image_archive(
                    archive,
                    source_sha=source_sha,
                    image_ref=release_image_ref(source_sha),
                    image_id=image_id,
                )


if __name__ == "__main__":
    unittest.main()
